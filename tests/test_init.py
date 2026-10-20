import contextlib
import io
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import init  # noqa: E402

EXPECTED_STACKS = {"web", "unity", "rust", "dotnet", "cpp", "python"}


def run_init(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = init.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class InitTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name) / "MyGame"
        self.project.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_lists_expected_stacks(self):
        self.assertEqual(set(init.list_stacks()), EXPECTED_STACKS)

    def test_every_stack_initialises_cleanly(self):
        for stack in sorted(EXPECTED_STACKS):
            with self.subTest(stack=stack):
                with tempfile.TemporaryDirectory() as d:
                    code, out, err = run_init("--stack", stack, "--into", d)
                    self.assertEqual(code, 0, err)
                    p = Path(d)
                    for rel in ("CLAUDE.md", ".harness/harness.toml", ".harness/INIT.md", ".harness/questions/core.md",
                                ".harness/questions/stack.md", ".harness/roles/implementer.md", ".claude/settings.json",
                                ".claude/skills/task/SKILL.md", ".claude/skills/resume/SKILL.md",
                                "docs/progress/progress.md", "docs/harness-notes.md", "docs/guardrails.md",
                                "docs/tasks/_template.md", ".gitignore"):
                        self.assertTrue((p / rel).exists(), rel)
                    self.assertFalse(list(p.rglob("*.tmpl")), "no .tmpl files must be left")
                    self.assertNotIn("{{", (p / "CLAUDE.md").read_text(encoding="utf-8"))
                    self.assertNotIn("{{", (p / ".harness/harness.toml").read_text(encoding="utf-8"))
                    self.assertIn(f'name = "{stack}"', (p / ".harness/harness.toml").read_text(encoding="utf-8"))
                    cfg = tomllib.loads((p / ".harness/harness.toml").read_text(encoding="utf-8"))
                    self.assertEqual(cfg["project"]["base_branch"], "")
                    self.assertIn("full", cfg["gates"])

    def test_settings_merge_stack_permissions(self):
        code, _, err = run_init("--stack", "python", "--into", str(self.project))
        self.assertEqual(code, 0, err)
        settings = json.loads((self.project / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertIn("Bash(git status*)", settings["permissions"]["allow"])
        self.assertIn("Bash(python -m pytest*)", settings["permissions"]["allow"])
        self.assertIn("Bash(pip install*)", settings["permissions"]["deny"])
        self.assertIn("Bash(git push*)", settings["permissions"]["deny"])

    def test_stack_rules_are_inserted_in_claude_md(self):
        run_init("--stack", "rust", "--into", str(self.project))
        text = (self.project / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("unwrap()", text)
        self.assertIn("MyGame", text)

    def test_refuses_to_overwrite_and_changes_nothing(self):
        (self.project / "CLAUDE.md").write_text("mine", encoding="utf-8")
        code, _, err = run_init("--stack", "web", "--into", str(self.project))
        self.assertEqual(code, 2)
        self.assertIn("CLAUDE.md", err)
        self.assertEqual((self.project / "CLAUDE.md").read_text(encoding="utf-8"), "mine")
        self.assertFalse((self.project / ".harness").exists())

    def test_second_run_is_refused(self):
        self.assertEqual(run_init("--stack", "web", "--into", str(self.project))[0], 0)
        self.assertEqual(run_init("--stack", "web", "--into", str(self.project))[0], 2)

    def test_dry_run_writes_nothing(self):
        code, out, _ = run_init("--stack", "unity", "--into", str(self.project), "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("CLAUDE.md", out)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_does_not_touch_existing_project_files(self):
        (self.project / "Assets").mkdir()
        (self.project / "Assets" / "keep.txt").write_text("x", encoding="utf-8")
        (self.project / ".gitignore").write_text("Library/\n", encoding="utf-8")
        code, out, _ = run_init("--stack", "unity", "--into", str(self.project))
        self.assertEqual(code, 0)
        self.assertEqual((self.project / "Assets" / "keep.txt").read_text(encoding="utf-8"), "x")
        self.assertEqual((self.project / ".gitignore").read_text(encoding="utf-8"), "Library/\n")
        self.assertIn("add these lines to your .gitignore", out)

    def test_unknown_stack_and_missing_folder(self):
        self.assertEqual(run_init("--stack", "nope", "--into", str(self.project))[0], 1)
        self.assertEqual(run_init("--stack", "web", "--into", str(self.project / "missing"))[0], 1)

    def test_list_flag(self):
        code, out, _ = run_init("--list")
        self.assertEqual(code, 0)
        self.assertIn("web", out)
        self.assertIn("tested", out)


if __name__ == "__main__":
    unittest.main()
