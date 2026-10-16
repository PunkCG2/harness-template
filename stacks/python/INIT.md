# Start a Python project (skeleton)

1. Create the folder, `python -m venv .venv`, activate it and install your base dependencies (pytest at least).
2. `git init`; ignore `.venv/`; commit.
3. `python <harness-template>\init.py --stack python --into <project>`; review with `git status`; commit.
4. Open Claude Code in the folder and run `/kickoff`, then `/plan`.
5. Start with `/task next`. The worker must run inside the venv; installs are denied by default.

## Verifying
- Gates: `python -m pytest -q` (fast); add ruff and mypy for the full gate if you use them.
- Milestones: run the entry point (or the app) as described in "how to test it".
