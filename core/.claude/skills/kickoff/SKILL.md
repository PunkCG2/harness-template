---
name: kickoff
description: Interviews the author at the start of a project and writes CLAUDE.md, docs/spec.md, docs/design.md, the three roles and .harness/harness.toml. Use when the user says /kickoff or the project still has the template placeholders.
---

# Kickoff: interview → project files

1. Read `.harness/harness.toml`, `.harness/questions/core.md`, `.harness/questions/stack.md` and `.harness/INIT.md`.
   If `docs/spec.md` already has real content, ask whether to redo it or only fill the gaps.
2. **Detect first.** Read what the repository, the installed tools and the local server can tell you: tool and stack
   versions, packages, existing config, and the installed models (`GET <url>/api/v0/models`). Show what you found and
   ask only to confirm it or to fill the gaps.
   Ask **one focused question at a time**, in the author's language, offering a recommended default when there is one.
   Skip anything already answered. Order: purpose and constraints (core 1-2), the stack questions, then core 3-8.
   The worker ladder, Claude budget and git workflow are not asked: use the template ladder, no budget limit, and
   propose a git workflow that fits the project.
3. After each area, summarise what you understood in two or three lines and let the author correct it.
4. Write, in this order (show each result briefly, never dump long files):
   - `docs/spec.md` and `docs/design.md` (from the answers; keep `Open questions` honest);
   - `.harness/harness.toml`: gates (fast / full), worker ladder, local server address, preferred and secondary local model (`model`, `fallback_model`), budget, `[scope] protected`, timings;
   - the three roles in `.harness/roles/` (3–6 lines each; implementer, reviewer, planner; `learning` mode adds the
     "explain why" lines);
   - `CLAUDE.md` (short: purpose, where things are, rules, notes rule, validation);
   - the author's own check steps into `docs/progress/progress.md` (how they test by hand).
5. Run the **fast gate once** on the empty project to record a first timing; if the project is empty, mark the
   calibration as provisional in `harness.toml`.
6. Tell the author to review the files and run `/plan`. Do not plan or implement anything from this skill.
