---
id: NNN
estado: pendiente        # pendiente | en-curso | hecha | bloqueada   (state: pending | in progress | done | blocked)
ejecuta: local           # local | claude-haiku | claude-sonnet | claude   (who runs it first; the ladder escalates)
depende: []              # ids of tasks that must be done first
hito: M1                 # milestone this task belongs to
rondas: 0                # filled by Claude on approval
---
# Short imperative title

## Objective
One or two sentences: what must exist when it is done.

## Files in scope
- path/file (create | modify)

## Do not touch
- protected paths

## Details
What the worker needs so it does not guess: data formats, function names, the design section that applies.
Keep it within the project's spec-line budget; split the task if it needs more.

## Acceptance criteria
- [ ] the fast gate passes
- [ ] (a concrete, checkable fact)

## Review notes
(written by Claude on approval)
