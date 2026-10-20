---
name: plan
description: Turns docs/spec.md and docs/design.md into task files in docs/tasks/ and proposes testable milestones. Use when the user says /plan or asks to generate or regenerate the tasks.
---

# Plan: spec → tasks and milestones

1. Read `docs/spec.md`, `docs/design.md`, `docs/tasks/_template.md`, `.harness/harness.toml` (`[budget]`) and
   `.harness/roles/planner.md`. If the spec has unanswered open questions, stop and ask them.
2. Split the work into **small, verifiable tasks** within the project's budget (default: ≤ 3 files, spec ≈ 15 lines).
   - UI or multi-file work: split into *text/styles*, *component*, *tests* so no single worker answer is large.
   - Every acceptance criterion must be checkable by a command or a concrete fact. Before writing a criterion check it
     against what the design already guarantees (docs/lessons.md L-007).
   - Put tests in the same task as the code they cover, or in a following task of the same milestone.
   - `runner: claude` only for work that depends on design judgement that is hard to specify; `runner: claude-haiku` or
     `claude-sonnet` for a task known to be too heavy for the local worker (stack rules may require it, e.g. Unity prefabs).
3. Number tasks in dependency order (`docs/tasks/NNN-short-name.md`, template format, field `milestone:`).
4. **Propose milestones.** A milestone is a point where a piece of functionality is complete and the author can test
   it by hand (for example, in the Unity Editor). For each: id, goal, tasks, **how to test it** (concrete steps),
   done criteria. If `session_max_hours` is set and the calibrated estimate exceeds it, split the milestone.
5. Write the milestones into `docs/progress/progress.md` and show the author one table: tasks (id, title, who runs
   it, dependencies, milestone) and the milestones. **Wait for approval.** Do not run any task from this skill.
