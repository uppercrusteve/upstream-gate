"""许可归一与分级。分级决定「能不能搬代码」。"""
from __future__ import annotations

from dataclasses import dataclass, field

PERMISSIVE = {
    "mit", "apache-2.0", "apache2", "bsd-2-clause", "bsd-3-clause", "bsd",
    "isc", "0bsd", "unlicense", "cc0-1.0",
}
COPYLEFT = {
    "gpl-2.0", "gpl-3.0", "gpl", "agpl-3.0", "agpl", "lgpl-2.1", "lgpl-3.0",
    "lgpl", "mpl-2.0", "eupl-1.2",
}
UNKNOWN = {"", "none", "noassertion", "unknown", "n/a", "unlicensed", "见仓库"}

ALIAS = {
    "apache 2.0": "apache-2.0",
    "apache-2": "apache-2.0",
    "bsd 3": "bsd-3-clause",
    "bsd 2": "bsd-2-clause",
    "agpl 3.0": "agpl-3.0",
    "agpl3": "agpl-3.0",
    "gpl 3.0": "gpl-3.0",
    "gpl3": "gpl-3.0",
    "无": "none",
    "未标注": "none",
}

PERMISSIVE_CLASS = "permissive"
COPYLEFT_CLASS = "copyleft"
UNKNOWN_CLASS = "unknown"


CANON = {
    "mit": "MIT", "isc": "ISC", "bsd": "BSD",
    "apache-2.0": "Apache-2.0", "bsd-2-clause": "BSD-2-Clause",
    "bsd-3-clause": "BSD-3-Clause", "0bsd": "0BSD", "unlicense": "Unlicense",
    "cc0-1.0": "CC0-1.0", "gpl": "GPL", "agpl": "AGPL", "lgpl": "LGPL",
    "gpl-2.0": "GPL-2.0", "gpl-3.0": "GPL-3.0", "agpl-3.0": "AGPL-3.0",
    "lgpl-2.1": "LGPL-2.1", "lgpl-3.0": "LGPL-3.0", "mpl-2.0": "MPL-2.0",
    "eupl-1.2": "EUPL-1.2",
}


def normalize(raw):
    value = (raw or "").strip().lower()
    value = ALIAS.get(value, value)
    if value in UNKNOWN:
        return "NOASSERTION"
    if value in PERMISSIVE or value in COPYLEFT:
        return CANON[value]
    return value


def classify(license_id):
    low = (license_id or "").lower()
    if low in PERMISSIVE:
        return PERMISSIVE_CLASS
    if low in COPYLEFT or low.startswith(("gpl", "agpl", "lgpl", "mpl", "eupl")):
        return COPYLEFT_CLASS
    return UNKNOWN_CLASS


def may_copy(license_id):
    return classify(license_id) == PERMISSIVE_CLASS


@dataclass
class Entry:
    repo: str
    took: str
    license: str
    line: int

    @property
    def klass(self):
        return classify(self.license)


@dataclass
class Upstream:
    entries: list = field(default_factory=list)
    sections: set = field(default_factory=set)
    path: str = ""

    def idea_only_repos(self):
        return [e.repo for e in self.entries if not may_copy(e.license)]

    def duplicates(self):
        seen, dup = set(), []
        for e in self.entries:
            if e.repo in seen:
                dup.append(e)
            seen.add(e.repo)
        return dup
