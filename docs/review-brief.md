# Review brief

Purpose: a full review of the harness template by a fresh session (Opus). Nothing here is a decision; it tells the
reviewer where to look. Read `CLAUDE.md`, `docs/spec.md` and `docs/lessons.md` first.

## State at 96d2eb0
- 62 tests pass: `python -m unittest discover -s tests`.
- Local commits not pushed: `43a6778`, `ac2aa3f`, `96d2eb0`. Do not push; the author does.
- `bench-site` (`E:\IA\bench-site`) is aligned with this template (its commit `b154cf3`). It has the author's own
  uncommitted work; do not touch it.

## What changed since the last harvest (cfa6e4d)
1. Kickoff question banks: `core/.harness/questions/core.md`, `stacks/*/questions.md`, `core/.claude/skills/kickoff/SKILL.md`.
2. Install guides: `stacks/*/INIT.md` (generated once; now plain files).
3. Repo files: `README.md`, `.gitignore`, `.gitattributes`.
4. Guardrails: `core/docs/guardrails.md.tmpl`, `read_signs` and `role_with_signs` in `core/.harness/run_worker.py`,
   changes in the skills `task`, `qa`, `sync` and in `.claude/skills/harvest`, spec §3 and §9, L-035.

## Review questions
- **Consistency:** do spec, README, skills, question banks and `init.py` say the same thing? Look for stale numbers
  (test counts, lesson ids), renamed files and promises no code keeps.
- **Core stays stack-agnostic:** any Node, npm, Vite or language assumption inside `core/`?
- **Guardrails:** is `read_signs` robust (headings, CRLF, comments, bullets inside code fences)? Does the 20-sign limit
  only warn? Could signs hurt a small local context? Is the split between Enforced (tools) and Signs (advice) honest?
- **Kickoff:** does the question order work end to end (core 1-2, stack, core 3-8)? Any question the machine could
  answer, a duplicate, or a fixed decision still asked?
- **Stacks:** the five skeletons list untested commands; flag anything that looks wrong rather than guessing fixes.
- **Safety rules:** `init.py` never overwrites, commits or pushes; skills never push; `/sync` leaves owned files alone.
- **Tests:** gaps in `tests/` for what changed (for example `init.py` with `guardrails.md`, `main` printing the
  guardrails line).
- **Unity readiness (phase 3):** what is missing before `init.py --stack unity` on a real project (batch-mode timings,
  headless test command, scene and prefab rules)?

## Out of scope
Claude Code Projects, a per-project `tool_guidance.md` and a milestone reflection step are future ideas (spec §13).

## Output wanted
Findings ranked by severity, each with file and line, what is wrong, and a suggested fix. Do not change files without
the author's approval.
