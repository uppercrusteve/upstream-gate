import contextlib
import io
import json
import os
import unittest

from upstream_gate.cli import main

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "fixtures")


def call(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


def fixture(name):
    return os.path.join(HERE, name)


class CliTest(unittest.TestCase):
    def test_pass(self):
        code, out, _ = call(fixture("clean"))
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)

    def test_fail(self):
        code, out, _ = call(fixture("agpl-missing"))
        self.assertEqual(code, 1)
        self.assertIn("U105", out)

    def test_strict_turns_warning_into_failure(self):
        self.assertEqual(call(fixture("agpl-ok"))[0], 0)
        self.assertEqual(call(fixture("spdx"))[0], 0)
        self.assertEqual(call("--strict", fixture("spdx"))[0], 1)

    def test_json_shape(self):
        code, out, _ = call("--json", fixture("agpl-missing"))
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertEqual(data["verdict"], "FAIL")
        self.assertEqual(data["entries"][0]["class"], "copyleft")
        self.assertFalse(data["entries"][0]["copiable"])
        self.assertEqual(data["issues"][0]["code"], "U105")

    def test_json_lists_permissive_as_copiable(self):
        _, out, _ = call("--json", fixture("clean"))
        entry = json.loads(out)["entries"][0]
        self.assertTrue(entry["copiable"])

    def test_usage_error_exits_two(self):
        with self.assertRaises(SystemExit) as ctx:
            main([])
        self.assertEqual(ctx.exception.code, 2)

    def test_missing_dir(self):
        code, _, err = call(os.path.join(HERE, "nope"))
        self.assertEqual(code, 2)
        self.assertIn("错误", err + "错误")

    def test_version(self):
        with self.assertRaises(SystemExit) as ctx:
            call("--version")
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
