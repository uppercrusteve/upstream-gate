import os
import unittest

from upstream_gate.policy import check_dir, verdict

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "fixtures")


def codes(name):
    issues, _ = check_dir(os.path.join(HERE, name))
    return [i.code for i in issues]


def result(name):
    issues, _ = check_dir(os.path.join(HERE, name))
    return verdict(issues)


class FixtureTest(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(result("clean"), "PASS")

    def test_copyleft_with_idea_declaration(self):
        self.assertEqual(result("agpl-ok"), "PASS")

    def test_copyleft_without_declaration(self):
        self.assertIn("U105", codes("agpl-missing"))

    def test_duplicate_repo(self):
        self.assertIn("U108", codes("dupe"))

    def test_missing_sections(self):
        self.assertEqual(codes("no-sections").count("U102"), 2)

    def test_empty_sources(self):
        self.assertIn("U103", codes("empty"))

    def test_missing_upstream(self):
        self.assertIn("U101", codes("missing-upstream"))

    def test_vendor_next_to_idea_claim_is_warning(self):
        self.assertEqual(result("vendor-warn"), "WARN")
        self.assertIn("U106", codes("vendor-warn"))

    def test_spdx_mismatch(self):
        self.assertIn("U111", codes("spdx"))

    def test_license_text_mismatch(self):
        self.assertIn("U109", codes("clash"))


class EdgeTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def put(self, name, text):
        path = os.path.join(self.tmp.name, name)
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_missing_readme(self):
        self.put("upstream.md", "## 来源\n\n- repo: a/b\n  took: 甲\n  license: MIT\n\n"
                               "## 许可\n\nMIT\n\n## 改了什么\n\n自写\n")
        self.assertIn("U107", codes(self.tmp.name))

    def test_empty_took(self):
        self.put("README.md", "## 上游\n\n## 原创\n\n自写\n")
        self.put("LICENSE", "MIT License\n")
        self.put("upstream.md", "## 来源\n\n- repo: a/b\n  license: MIT\n\n"
                                "## 许可\n\nMIT\n\n## 改了什么\n\n自写\n")
        self.assertIn("U112", codes(self.tmp.name))

    def test_no_license_is_warning(self):
        self.put("README.md", "## 上游\n\n## 原创\n\n自写\n")
        self.put("upstream.md", "## 来源\n\n- repo: a/b\n  took: 甲\n  license: MIT\n\n"
                                "## 许可\n\nMIT\n\n## 改了什么\n\n自写\n")
        issues, _ = check_dir(self.tmp.name)
        self.assertEqual(verdict(issues), "WARN")

    def test_unknown_license_warns(self):
        self.put("README.md", "## 上游\n\n## 原创\n\n思路级重写\n")
        self.put("LICENSE", "MIT License\n")
        self.put("upstream.md", "## 来源\n\n- repo: a/b\n  took: 甲\n  license: 见仓库\n\n"
                                "## 许可\n\n未标注\n\n## 改了什么\n\n自写\n")
        self.assertIn("U104", codes(self.tmp.name))


if __name__ == "__main__":
    unittest.main()
