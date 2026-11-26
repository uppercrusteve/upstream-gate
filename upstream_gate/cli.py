"""命令行：判定一个候选目录能不能带着它的上游声明出门。"""
from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .policy import check_dir, verdict


def build_parser():
    p = argparse.ArgumentParser(prog="upstream-gate",
                                description="检查 upstream.md 的三段、许可分级与思路级声明")
    p.add_argument("dir", help="候选目录")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true", help="连警告也返回 1")
    p.add_argument("--version", action="version", version=__version__)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not os.path.isdir(args.dir):
        print(f"目录不存在: {args.dir}", file=sys.stderr)
        return 2
    try:
        issues, up = check_dir(args.dir)
    except OSError as exc:
        print(f"读不了目录: {exc}", file=sys.stderr)
        return 2

    result = verdict(issues)
    if args.json:
        print(json.dumps({
            "verdict": result,
            "entries": [{"repo": e.repo, "license": e.license, "class": e.klass,
                         "copiable": e.klass == "permissive", "line": e.line}
                        for e in (up.entries if up else [])],
            "issues": [i.as_dict() for i in issues],
        }, ensure_ascii=False, indent=2))
    else:
        for i in issues:
            print(i)
        print(f"-- 判定 {result}：{len(issues)} 条")
    if result == "FAIL":
        return 1
    if result == "WARN" and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
