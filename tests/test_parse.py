import unittest

from upstream_gate.parse import parse

DOC = """# 上游

## 来源

- repo: a/one
  took: 甲
  license: MIT
- repo: b/two
  took: 乙
  license: AGPL-3.0

## 许可

混合。

## 改了什么

自写。
"""


class ParseTest(unittest.TestCase):
    def test_sections(self):
        up, problems = parse(DOC)
        self.assertEqual(up.sections, {"来源", "许可", "改了什么"})
        self.assertEqual(problems, [])

    def test_entries(self):
        up, _ = parse(DOC)
        self.assertEqual([e.repo for e in up.entries], ["a/one", "b/two"])
        self.assertEqual(up.entries[1].license, "AGPL-3.0")
        self.assertEqual(up.entries[1].line, 8)

    def test_idea_only_filter(self):
        up, _ = parse(DOC)
        self.assertEqual(up.idea_only_repos(), ["b/two"])

    def test_duplicates(self):
        doc = DOC.replace("## 许可", "- repo: a/one\n  took: 丙\n  license: MIT\n\n## 许可")
        up, _ = parse(doc)
        self.assertEqual([e.repo for e in up.duplicates()], ["a/one"])

    def test_table_form(self):
        doc = "## 来源\n\n| repo | took | license |\n|---|---|---|\n| a/one | 甲 | MIT |\n"
        up, problems = parse(doc)
        self.assertEqual(up.entries[0].took, "甲")
        self.assertEqual(problems, [])

    def test_bad_repo_shape(self):
        up, problems = parse("## 来源\n\n- repo: notarepo\n  took: 甲\n  license: MIT\n")
        self.assertEqual(problems[0].line, 3)

    def test_field_outside_list_is_ignored(self):
        up, problems = parse("## 来源\n\ntook: 甲\n")
        self.assertEqual(up.entries, [])
        self.assertEqual(problems, [])

    def test_fields_only_collected_in_source_section(self):
        doc = "## 许可\n\n- repo: a/one\n  took: 甲\n  license: MIT\n"
        up, _ = parse(doc)
        self.assertEqual(up.entries, [])


if __name__ == "__main__":
    unittest.main()
