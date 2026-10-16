---
name: task
description: Runs one task from docs/tasks/ through the worker ladder, the automatic gates and Claude's review, then merges it. Use when the user says /task <file|next> or asks to execute pending tasks.
---

# Task: worker → gates → review → merge

## 1. Prepare
- Read the task. If scope or criteria are missing or not checkable, complete them first.
- `git status` must be clean and on the main branch; otherwise stop and say so. Pick `next` = first `pendiente`
  task whose dependencies are `hecha`, in milestone order.
- Set `estado: en-curso`. Branch: `task/NNN-name`. Update `docs/progress/progress.md` (current task).

## 2. Delegate (unless `ejecuta: claude`)
```
python .harness/run_worker.py docs/tasks/NNN-name.md   # tasks from /qa live in docs/tasks/qa/
```
If the exit code means "no model chosen", show the listed models to the author, ask which one and run again with
`--model <id>`. Run it in the background (it can take minutes) and leave the tree alone while it runs. The script runs the ladder, the scope guard and the gates by itself and returns a **review brief**
(diff stat, gate results, scope result, worker and rounds used). For `ejecuta: claude` implement it yourself on the
branch and run the gates yourself.

## 3. Review (cheap)
- Read the brief first; read the full diff only where gates cannot see (scope, quality, unautomated criteria).
- Run `git status`: no stray files. Check every acceptance criterion.
- If the worker hit `max turns` or errored, judge by the files and the gates, not by the exit status.

## 4. Correct (max 3 rounds)
If something fails, write `NNN-name.fix-K.md` next to the task (same folder) with numbered, concrete corrections (file, what is wrong,
what is expected) and run the worker again on the same branch. Split the fix into parts if the first answer
overflowed. After round 3, fix small leftovers yourself or explain the blocker to the author.

## 5. Approve
- `git switch main`, `git merge --squash task/NNN-name`, commit `NNN: <summary>`, delete the branch. If a dev server is running, touch the files that changed (`git diff --name-only HEAD~1 HEAD | xargs touch`) so it does not serve stale files after the branch switch.
- Task: `estado: hecha`, `rondas: K`, one or two lines in review notes. Commit.
- **Harness notes:** if the task needed escalation or more than one round, or anything about the harness itself was
  wrong, append an entry to `docs/harness-notes.md`.
- Update `docs/progress/progress.md`.

## 6. Milestone stop
When the last task of a milestone is done: stop, summarise what now works, repeat its **how to test it**, and ask the
author whether to continue with the next milestone or stop here. Never start the next milestone on your own. If
there are 5 or more un-harvested notes, mention it once.
