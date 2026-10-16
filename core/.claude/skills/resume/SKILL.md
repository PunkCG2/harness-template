---
name: resume
description: Reports where the project stopped and continues from there. Use when the user says /resume or opens a project that has docs/progress/progress.md and asks to continue.
---

# Resume

1. Read `docs/progress/progress.md`, the task files' `estado` (in `docs/tasks/` and `docs/tasks/qa/`), `git status`, `git branch` and `.harness/harness.toml`.
2. Report in a few lines (no long dumps):
   - last finished milestone and whether the author already tested it;
   - the current milestone: done and pending tasks;
   - a half-done task: a `task/NNN-*` branch or a dirty tree → offer **continue** or **discard** (never discard
     without asking);
   - un-harvested notes in `docs/harness-notes.md` (count), and whether the template version in `harness.toml` is
     older than the template folder (suggest `/sync`).
3. Ask whether to continue. If yes, resume with `/task next` from the first pending task of the current milestone.
   If the previous milestone was never confirmed as tested, ask first.
