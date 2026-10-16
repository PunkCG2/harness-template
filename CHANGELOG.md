# Changelog

## Unreleased
- Phase 1: specification, lessons from `bench-site` (L-001…L-019), `init.py` with tests, core templates (roles,
  skills, progress, notes), stack skeletons: web (tested), unity, rust, dotnet, cpp, python.

## Phase 2 — unified worker
- `core/.harness/run_worker.py`: proxy, model discovery (`/api/v0/models`), escalation ladder, scope guard, fast gates, adaptive timeouts, review brief. Stdlib only; `tests/test_run_worker.py` (24 tests).
- Proxy ignores client-dropped connections (no more `ConnectionResetError` tracebacks).
- `/qa` skill: human review at milestone close becomes logged items, tasks and checks.
- `init.py` skips `__pycache__` when copying `core/` and stacks.
- First real use (bench-site tasks 030, 031): both passed on the first local attempt.
- `/task`: touches merged files so a running dev server does not serve stale CSS (L-021).
- `.harness/state/` is ignored by the scope guard and excluded from the worker commit.
- `/qa` and `/task`: QA tasks and their logs live in `docs/tasks/qa/`.
- `strip_thinking_attempts = 2` (default): the first two local attempts run with thinking stripped, the third with it on (L-024).
- Live progress display (`--watch`, status line, token counters) was built and then removed: a second terminal was not useful and the chat window cannot show it.
- L-025: the strip-thinking result was repeated with gemma-4-26b-a4b-qat (same quality, 1.9-3.8x faster).
- Default server URL is `127.0.0.1:1234`, not `localhost` (a dev server on IPv6 `::1:1234` answered instead of the model server; L-026).
- Model loading: instances are checked before loading, a load order is never repeated, loading is serialized with a lock, only one run per project at a time (exit code 6), and a model that is already loaded is used instead of loading another (L-027).
- `model` is now the preferred model and `fallback_model` an optional secondary one; `/kickoff` asks for both.
- Harvest of bench-site notes: L-028 (offsetLeft), L-029 (visual conditions), L-030 (stopping chained commands), L-031 (proxy tracebacks), L-032 (heavy three-file tasks), L-033 (live display removed).
- `/sync` honours `[sync] skip` in `harness.toml`; `harness.toml.tmpl` gains `[sync]` and `[template] path`.
- spec §8.2/§8.3/§7/§12/§13 and `CLAUDE.md` updated: model discovery and loading rules, thinking policy, `/qa`, phase status and handoff.
- `/kickoff` question review (L-034): atomic questions, detect before asking, no GPU / hand-typed numbers / machine-hours questions, fixed ladder, budget and git workflow, Unity questions rewritten (fixed decisions and who edits what).
- Unity questions: game type, multiplayer, free-text feel, performance target, art source, first-milestone scope, save/load, architecture; fixed scene-wiring, `UnityYAMLMerge` and editor-script rules.
- Kickoff review of web (analytics, SEO, content source), python, dotnet, rust and cpp; common questions (feel, first milestone, architecture) moved to core.
- Every stack's `INIT.md` is now a full install guide: prerequisites, steps, what `init.py` does, what happens after, `/sync` and `/harvest`.
