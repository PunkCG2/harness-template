# harness-template

Reusable starter kit for AI-assisted development with a local-first worker. Read `docs/spec.md` (approved design) and
`docs/lessons.md` before changing anything.

## State (handoff)
- Phases 1 and 2 are done: spec, lessons (L-001..L-033), `init.py`, core templates, six stack skeletons (web tested), the
  unified worker `core/.harness/run_worker.py` (58 tests in `tests/`) and the skills kickoff, plan, task, qa, resume, sync
  (+ harvest at the repo root).
- First project that used it: `bench-site` (`E:\IA\bench-site`, a Vite site). Its `docs/harness-notes.md` has been harvested up to the
  commit that introduced this handoff; its `harness.toml` carries `[template] version` and `[sync] skip = [".claude/skills"]`
  (its skills are in Spanish, so `/sync` must not overwrite them).
- **Next (phase 3):** use the template on a real Unity project (`init.py --stack unity`), then `/harvest <project>` for its notes and
  `/sync` from the project when this repository changes. The `unity` stack is a skeleton: real batch-mode timings, the headless test
  command and the stack questions are still to be confirmed. Compare the thinking policy (§8.3) on harder tasks.
- Decisions to respect: no cost/token logging; no live progress display (L-033); local server address as `127.0.0.1` (L-026);
  tasks of at most ~3 files and ~15 spec lines; QA tasks live in `docs/tasks/qa/`.

## Rules
- Everything in this repository is English. The author may talk in Spanish.
- `core/` stays stack-agnostic: no Node, npm, Vite or language assumptions. Stack specifics go in `stacks/<stack>/`.
- Never overwrite a project's files from `init.py`; never commit or push on the author's behalf (`/harvest` commits locally,
  the author pushes).
- Keep `python -m unittest discover -s tests` green. Every change that comes from a real project gets a row in
  `docs/lessons.md` and a line in `CHANGELOG.md`.
- Open spikes (spec section 13): stripping `thinking` in the proxy, real Unity batch timings. Confirmed: Bionic model endpoints.
- Future idea (spec §13): Claude Code Projects for parallel work, only when it can run in a local environment.

## Context for the worker script
- The local server (LM Studio or Bionic) listens on `http://localhost:1234`; model list: `GET /api/v0/models`; load:
  `POST /api/v1/models/load`; unload: `POST /api/v1/models/unload`. The reference scripts are the author's
  `agente_benchmark.py` / `pareja_benchmark.py` (they stripped sampling parameters to use the saved preset).
- Claude Code sends `thinking`, `output_config` and `context_management`; it does not send temperature/top_p/top_k.
- Windows: PowerShell 5.1 mangles non-ASCII in launcher scripts; prefer Python.
