---
name: qa
description: Turns the author's by-eye review into items, tasks and checks. Use when the user says /qa or describes things they saw while testing a milestone and wants them fixed.
---

# QA: human review → items → tasks

Input: what the author saw while testing (free text, screenshots), usually when a milestone closes.

1. **Items.** Split it into independent items. One item = one symptom or one requested change. If an item is ambiguous
   (which browser, which width, what was expected) ask before going on; never guess. Mark it **defect** (something
   broken) or **adjustment** (the author's preference), with severity high / medium / low.
2. **Log.** Write `docs/tasks/qa/qa-<milestone>.md` (create the folder if missing; create or append): table `id | item | kind | severity | expected | task | status`.
   Describe screenshots in one line; do not copy them.
3. **Tasks.** One task per item (or per group touching the same file) in `docs/tasks/qa/` (numbering continues the project's), from the task template and the
   `/plan` rules: at most the project's files-per-task budget, a verifiable criterion, `runner: local` unless it needs
   design judgement. Attach them to the current milestone.
4. **Checks.** Every task carries its own check:
   - automatable (logic, text, a measurable style value) → a test inside the task's scope;
   - visual only (scroll, hover, drag) → an acceptance line "verified in <browser> at <width>" that you run, closing the
     browser afterwards.
5. **Approval.** Show the table (id, item, severity, task, runner) and **wait for the go-ahead**. Run nothing from here.
6. **After.** With the go-ahead, run `/task` on each. When they finish, ask the author to re-check by eye. The milestone is
   not closed while `docs/tasks/qa/qa-<milestone>.md` has open items.
7. For each **defect** that a short rule would have prevented, propose a sign for `docs/guardrails.md` (format in that
   file; needs evidence, the author approves before it is added).
8. If an item exposes a harness or stack flaw (not a project flaw), add an entry to `docs/harness-notes.md`.
