import sys

from .cli import main

# 终端若是 GBK（Windows 默认），中文会按 UTF-8 输出成乱码；统一成 UTF-8。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

sys.exit(main())
