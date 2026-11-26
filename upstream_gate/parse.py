"""解析 upstream.md。两种行式都收：列表式与表格式。

格式故意死板——写成散文就没法判，判不了就等于没有。
"""
from __future__ import annotations

import re

from .model import Entry, Upstream, normalize

REQUIRED_SECTIONS = ("来源", "许可", "改了什么")
REPO = re.compile(r"^[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+$")
LIST = re.compile(r"^\s*[-*]\s*repo\s*:\s*(\S+)\s*$")
FIELD = re.compile(r"^\s+(took|license)\s*:\s*(.+?)\s*$")
TABLE = re.compile(r"^\s*\|?\s*([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)\s*\|\s*(.+?)\s*\|\s*([^|]+?)\s*\|?\s*$")


class ParseProblem:
    def __init__(self, line, message):
        self.line = line
        self.message = message


def section_of(line):
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    title = stripped.lstrip("#").strip()
    for name in REQUIRED_SECTIONS:
        if name in title:
            return name
    return "其他"


def parse(text, path="upstream.md"):
    up = Upstream(path=path)
    problems = []
    current = None
    pending = None  # 正在补 took/license 的 Entry
    for i, line in enumerate(text.splitlines(), 1):
        sec = section_of(line)
        if sec:
            current = sec
            if sec in REQUIRED_SECTIONS:
                up.sections.add(sec)
            pending = None
            continue
        if current != "来源":
            continue
        if not line.strip() or line.strip().startswith(("|--", "|---")):
            continue
        m = LIST.match(line)
        if m:
            pending = _add(up, problems, m.group(1), i)
            continue
        f = FIELD.match(line)
        if f and pending is not None:
            key, value = f.group(1), f.group(2)
            if key == "took":
                pending.took = value
            else:
                pending.license = normalize(value)
            continue
        t = TABLE.match(line)
        if t and not line.strip().startswith("| repo"):
            repo, took, lic = t.groups()
            if REPO.match(repo):
                entry = _add(up, problems, repo, i)
                entry.took = took
                entry.license = normalize(lic)
                pending = None
            continue
        if line.lstrip().startswith(("-", "*")) and not LIST.match(line):
            problems.append(ParseProblem(i, "疑似来源行但不是 repo: owner/name"))
    return up, problems


def _add(up, problems, repo, line):
    repo = repo.strip().strip("`")
    if not REPO.match(repo):
        problems.append(ParseProblem(line, f"不是 owner/repo: {repo!r}"))
        return None
    entry = Entry(repo, "", "NOASSERTION", line)
    up.entries.append(entry)
    return entry
