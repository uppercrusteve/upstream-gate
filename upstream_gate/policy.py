"""判定。规则分错误与警告：错误拦发布，警告只提示。"""
from __future__ import annotations

import os
import re

from .parse import REQUIRED_SECTIONS, parse

BINARY_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".woff",
              ".woff2", ".ttf", ".mp4", ".so", ".dll", ".exe"}
BIG = 1024 * 1024
IDEA_MARK = re.compile(r"思路级|idea[- ]level|只重写思路|只抄思路|抄思路|only ideas?", re.I)
README_SECTIONS = ("原创", "上游")
MIT_TEXT = re.compile(r"\bMIT License\b", re.I)
APACHE_TEXT = re.compile(r"Apache License", re.I)
LICENSE_SPDX = (MIT_TEXT, APACHE_TEXT, re.compile(r"BSD \d-Clause", re.I),
                re.compile(r"\bISC License\b", re.I))
SPDX_HEADER = re.compile(r"SPDX-License-Identifier:\s*([\w.\-+]+)")


class Issue:
    def __init__(self, code, severity, message, path="", line=0):
        self.code = code
        self.severity = severity
        self.message = message
        self.path = path
        self.line = line

    def as_dict(self):
        return {"code": self.code, "severity": self.severity, "message": self.message,
                "path": self.path, "line": self.line}

    def __str__(self):
        where = ""
        if self.path:
            where = f" {self.path}:{self.line}" if self.line else f" {self.path}"
        return f"{self.severity.upper()} {self.code}{where} {self.message}"


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def walk(root):
    for base, dirs, names in os.walk(root):
        for skip in ("__pycache__", ".git", "dist"):
            if skip in dirs:
                dirs.remove(skip)
        for name in names:
            yield os.path.join(base, name)


def check_dir(root):
    issues = []
    up_text = read(os.path.join(root, "upstream.md"))
    if up_text is None:
        issues.append(Issue("U101", "error", "缺 upstream.md，来源不可追溯", "upstream.md"))
        return issues, None

    up, problems = parse(up_text)
    for p in problems:
        issues.append(Issue("U103", "error", p.message, "upstream.md", p.line))
    for name in REQUIRED_SECTIONS:
        if name not in up.sections:
            issues.append(Issue("U102", "error", f"缺「{name}」小节", "upstream.md"))
    if not up.entries:
        issues.append(Issue("U103", "error", "「来源」没有 repo 行", "upstream.md"))
    for entry in up.duplicates():
        issues.append(Issue("U108", "error", f"{entry.repo} 重复登记", "upstream.md", entry.line))
    for entry in up.entries:
        if entry.klass == "unknown":
            issues.append(Issue("U104", "warn",
                                f"{entry.repo} 的许可认不出（{entry.license}），按 idea-only 处理",
                                "upstream.md", entry.line))
        if not entry.took:
            issues.append(Issue("U112", "error", f"{entry.repo} 没写借鉴了什么", "upstream.md", entry.line))

    readme = read(os.path.join(root, "README.md"))
    if readme is None:
        issues.append(Issue("U107", "error", "缺 README.md", "README.md"))
        readme = ""
    for name in README_SECTIONS:
        if f"## {name}" not in readme:
            issues.append(Issue("U107", "error", f"README 缺「{name}」小节", "README.md"))

    idea_ok = bool(IDEA_MARK.search(readme))
    risky = up.idea_only_repos()
    if risky and not idea_ok:
        issues.append(Issue("U105", "error",
                            f"{', '.join(risky)} 非宽松许可，README 没声明思路级", "README.md"))
    if risky and idea_ok:
        markers = ("vendor", "LICENSE.upstream", "LICENSE-")
        hits = [p for p in walk(root)
                if os.path.basename(p).startswith(markers)
                and not os.path.relpath(p, root).startswith("fixtures")]
        if hits:
            issues.append(Issue("U106", "warn",
                                "声明思路级但带了上游 LICENSE 一类的文件，确认没搬代码",
                                os.path.relpath(hits[0], root)))

    license_file = next((p for p in walk(root)
                         if os.path.basename(p).upper().startswith("LICENSE")), None)
    declared = [e for e in up.entries if e.klass == "permissive"]
    ours_is_upstreams = bool(declared) and len(declared) == len(up.entries)
    if license_file and ours_is_upstreams:
        text = read(license_file) or ""
        rel = os.path.relpath(license_file, root).replace(os.sep, "/")
        if declared and not any(rx.search(text) for rx in LICENSE_SPDX):
            issues.append(Issue("U109", "error", "LICENSE 文本认不出，和登记的上游许可对不上", rel))
        for rx, sid in ((MIT_TEXT, "mit"), (APACHE_TEXT, "apache-2.0")):
            if rx.search(text) and declared and not any(sid in e.license.lower() for e in declared):
                issues.append(Issue("U109", "warn", f"LICENSE 写的是 {sid}，与登记不符", rel))
    elif not license_file:
        issues.append(Issue("U101", "warn", "没有 LICENSE 文件", "LICENSE"))

    for path in walk(root):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        if rel.startswith(("tests/", "fixtures/")):
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext in BINARY_EXT and os.path.getsize(path) > BIG:
            issues.append(Issue("U110", "warn", "大二进制没有来源说明", rel))
        if ext in (".py", ".js", ".mjs", ".ts", ".sh"):
            m = SPDX_HEADER.search((read(path) or "")[:400])
            if m:
                actual = m.group(1).lower()
                declared_ids = {e.license.lower() for e in up.entries}
                if declared_ids and actual not in declared_ids:
                    issues.append(Issue("U111", "warn",
                                        f"源码声称 {actual}，与登记的 {', '.join(sorted(declared_ids))} 不符",
                                        rel))
    return issues, up


def verdict(issues):
    if any(i.severity == "error" for i in issues):
        return "FAIL"
    return "WARN" if issues else "PASS"
