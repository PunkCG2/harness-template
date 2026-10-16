# Install the harness in a Python project (skeleton)

## Prerequisites
- Python 3, Git, Claude Code, and your environment manager (venv, uv or poetry).
- A local model server (LM Studio or Bionic) on `127.0.0.1:<port>`, optional but needed for the local worker.

## Steps
1. **Create the folder and the environment**: `python -m venv .venv`, activate it, install your base dependencies (pytest at least).
2. **Start git**: `git init`, ignore `.venv/`, commit.
3. **Copy the harness**: `python <harness-template>\init.py --stack python --into <project>`.
4. **Review and commit**: `git status`, then commit the harness files.
5. **Start the harness**: open Claude Code in the folder (with the environment active) and run `/kickoff`.

The worker runs inside the environment and never installs packages; install them by hand.

## What `init.py` does (and does not)
- Copies `.claude/` (settings and skills), `.harness/` (worker, roles, questions, `harness.toml`), `CLAUDE.md` and `docs/` into the project.
- Merges the stack's permissions into `.claude/settings.json` and records the template version in `harness.toml`.
- Creates `.gitignore` if missing; if one exists it only prints the lines to add (`.harness/state/` and the stack's lines).
- If any destination file already exists it writes **nothing** and lists the conflicts (exit code 2): move them and run again.
- Never commits, never pushes, never overwrites. Use `--dry-run` to see the file list first.

## After `init.py`
1. Review with `git status`, add the `.gitignore` lines it printed if any, and commit the harness files.
2. Open Claude Code in the project folder and run `/kickoff`. It detects what it can, then interviews you one question at a time.
3. Review the files it writes, then run `/plan`: it creates tasks and proposes testable milestones for you to approve.
4. Run `/task next`. The worker implements, the gates run, Claude reviews and merges.
5. Test each milestone by hand ("how to test it") and use `/qa` to report what you saw.

## Later
- `/sync` (from the project) pulls updated harness files from the template. It needs `[template] path` in `.harness/harness.toml`
  to point at the template folder; files listed in `[sync] skip` are left alone.
- Lessons learned in the project go to `docs/harness-notes.md`; `/harvest <project>`, run from the template, moves them back.

## Verifying
- Gates: `python -m pytest -q` (fast); add ruff and mypy for the full gate if you use them.
- Milestones: run the entry point (or the app) as described in "how to test it".
