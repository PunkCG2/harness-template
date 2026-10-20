---
name: harvest
description: Run from the harness-template folder. Moves lessons from a project's docs/harness-notes.md into the template (core or a stack), with a changelog line and a traceable commit. Use when the user says /harvest <project path>.
---

# Harvest (run in the template folder)

1. Read `<project>/docs/harness-notes.md`; take entries with status `new`. If none, say so and stop.
2. Show them one by one. For each the author decides: **core**, **stack:<name>**, or **discard** (project-only
   notes stay in the project). Do not decide for them.
3. For each promoted entry edit the template: `docs/lessons.md` (new row with the next id), the right question in
   `core/.harness/questions/core.md` or `stacks/<stack>/questions.md`, a rule in `stacks/<stack>/CLAUDE.part.md`, a
   default in `stack.toml`, or the script/skills when the lesson is about them.
   Also read the `Signs` of `<project>/docs/guardrails.md`: a sign that would help other projects is offered the same
   way (core `lessons.md`, a stack's `CLAUDE.part.md` rule, or a gate). Signs stay in the project unless promoted.
4. Add a line per entry to `CHANGELOG.md` and commit locally with a trailer
   `Source: <project>#<note title>`. **Never push** (the author pushes).
5. In the project's notes mark each handled entry `harvested <commit>` (or `discarded`) and say what was left to do.
