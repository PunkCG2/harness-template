# harness-template

Reusable starter kit for AI-assisted development with a local-first worker. Read `docs/spec.md` (approved design) and
`docs/lessons.md` before changing anything.

## State
- Phase 1 is done: spec, lessons, `init.py` (+ tests), core templates, stack skeletons (web tested; unity, rust, dotnet,
  cpp, python are skeletons).
- Phase 2 is done: `core/.harness/run_worker.py` (+ `tests/test_run_worker.py`), adopted in `bench-site` (tasks 030, 031 passed first attempt). Attempts 1-2 of the local worker run with thinking stripped (`strip_thinking_attempts = 2`, L-024); the third runs with it. The ladder was seen working for real (local x3 -> Haiku). Untested: `--model` selection when nothing is loaded.
- Phase 3: exercise `/harvest` and `/sync` on a second real project.

## Rules
- Everything in this repository is English. The author may talk in Spanish.
- `core/` stays stack-agnostic: no Node, npm, Vite or language assumptions. Stack specifics go in `stacks/<stack>/`.
- Never overwrite a project's files from `init.py`; never commit or push on the author's behalf (`/harvest` commits locally,
  the author pushes).
- Keep `python -m unittest discover -s tests` green. Every change that comes from a real project gets a row in
  `docs/lessons.md` and a line in `CHANGELOG.md`.
- Open spikes (spec section 13): stripping `thinking` in the proxy, real Unity batch timings. Confirmed: Bionic model endpoints.

## Context for the worker script
- The local server (LM Studio or Bionic) listens on `http://localhost:1234`; model list: `GET /api/v0/models`; load:
  `POST /api/v1/models/load`; unload: `POST /api/v1/models/unload`. The reference scripts are the author's
  `agente_benchmark.py` / `pareja_benchmark.py` (they stripped sampling parameters to use the saved preset).
- Claude Code sends `thinking`, `output_config` and `context_management`; it does not send temperature/top_p/top_k.
- Windows: PowerShell 5.1 mangles non-ASCII in launcher scripts; prefer Python.
