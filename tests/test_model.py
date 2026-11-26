import unittest

from upstream_gate.model import Entry, classify, may_copy, normalize


class LicenseTest(unittest.TestCase):
    def test_permissive(self):
        for raw in ("MIT", "mit", "Apache-2.0", "ISC", "BSD-3-Clause", "0BSD"):
            self.assertEqual(classify(normalize(raw)), "permissive", raw)
            self.assertTrue(may_copy(normalize(raw)))

    def test_copyleft(self):
        for raw in ("AGPL-3.0", "GPL-3.0", "LGPL-2.1", "MPL-2.0", "agpl"):
            self.assertEqual(classify(normalize(raw)), "copyleft", raw)
            self.assertFalse(may_copy(normalize(raw)))

    def test_unknown(self):
        for raw in ("", "none", "无", "见仓库", "WTFPL-ish"):
            self.assertEqual(classify(normalize(raw)), "unknown", raw)

    def test_alias(self):
        self.assertEqual(normalize("Apache 2.0"), "Apache-2.0")
        self.assertEqual(normalize("AGPL 3.0"), "AGPL-3.0")
        self.assertEqual(normalize("无"), "NOASSERTION")

    def test_entry_class(self):
        self.assertEqual(Entry("a/b", "x", "MIT", 1).klass, "permissive")


if __name__ == "__main__":
    unittest.main()
