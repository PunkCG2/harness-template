# AI Dev Harness — Specification

Status: **draft for review** (2026-10-15). Design agreed in conversation with the author while building the
`bench-site` project. Nothing here is final until the author approves it.

## 1. Purpose

A reusable starting kit for AI-assisted development in **any stack** (web, Unity, Rust, .NET, C++, Python, …).
It gives a new project, from day one:

- a workflow: spec → plan → tasks → worker implements → automatic checks → Claude reviews → merge;
- a **local-first worker** that does the heavy work, so Claude's subscription tokens are spent on planning and
  review only, without lowering the quality of the result;
- written roles, milestones, progress tracking and a way to feed lessons learned back into the kit.

Primary goal: **keep development local as long as possible** and escalate to Claude only when needed.

## 2. Principles

1. **Stack-agnostic core.** Nothing in `core/` assumes Node, Vite, npm or any language. Stack specifics live in
   `stacks/<stack>/` and in the project's `harness.toml`.
2. **Everything is a file.** The model remembers nothing between sessions; rules, roles, progress and notes are files.
3. **Small, verifiable tasks.** Task size is a *parameter of the project* (depends on the worker model), not a
   fixed rule. Every acceptance criterion is checkable by a command or a concrete fact.
4. **Automatic gates before human/Claude review.** Claude reads a short summary, not the whole code.
5. **Honest about what is tested.** Only `web` is proven; other stacks ship as skeletons marked `status = "skeleton"`.
6. **Template text is English.** Conversations with the author may be in any language.
7. **Nothing is overwritten.** The kit never replaces files the project owns; it never commits or pushes for you.

Non-goals: cost/token accounting per task, parallel workers, packaging as a Claude Code plugin (can come later
without redesign).

## 3. Repository layout

```
harness-template/
├─ README.md
├─ CHANGELOG.md
├─ init.py                      copies core + one stack into a project
├─ .claude/skills/harvest/      the /harvest skill lives here (it runs from the template folder, not in projects)
├─ core/                        stack-agnostic files copied into every project
│  ├─ CLAUDE.md.tmpl            short rules; {{stack_rules}} is filled from the stack
│  ├─ .claude/
│  │  ├─ settings.json.tmpl     generic permissions; the stack's permissions.json is merged in
│  │  └─ skills/{kickoff,plan,task,qa,resume,sync}/SKILL.md
│  ├─ .harness/
│  │  ├─ harness.toml.tmpl      project config (stack gates, worker ladder, timings, template version)
│  │  ├─ roles/{implementer,reviewer,planner}.md.tmpl
│  │  ├─ questions/core.md      question bank for /kickoff
│  │  └─ run_worker.py          unified worker script (phase 2, see §12)
│  └─ docs/
│     ├─ spec.md.tmpl  design.md.tmpl  harness-notes.md.tmpl  guardrails.md.tmpl
│     ├─ tasks/_template.md      (tasks born from `/qa` go in tasks/qa/, created on demand)
│     └─ progress/progress.md.tmpl
├─ stacks/<stack>/              web (tested), unity, rust, dotnet, cpp, python (skeletons)
│  ├─ stack.toml                status, fast/full gates, initial timings
│  ├─ permissions.json          extra allow/deny entries for settings.json
│  ├─ gitignore.part            lines for the project's .gitignore
│  ├─ CLAUDE.part.md            stack-specific rules inserted into CLAUDE.md
│  ├─ questions.md              stack questions for /kickoff
│  └─ INIT.md                   ≤ 25 lines: how to start a project of this stack, and how to verify it
├─ docs/{spec.md,lessons.md}
└─ tests/                       tests for init.py
```

Inside a project, files are either **managed** (replaceable by `/sync`: `.harness/run_worker.py`,
`.harness/questions/`, the skills) or **owned** (never touched by the kit: `CLAUDE.md`, `docs/`, `harness.toml`,
`.harness/roles/`, `docs/guardrails.md`).

## 4. Starting a project

1. Create the project with its normal tool (Unity Hub, `cargo new`, `npm create`, …) and `git init`.
2. `python <harness-template>/init.py --stack <stack> --into <project>`:
   - merges `core/` with `stacks/<stack>/` (the stack wins on conflicts);
   - **refuses to run if any destination file already exists**, listing the conflicts and changing nothing;
   - writes `.harness/harness.toml` with the stack and the template version (git hash of the template, if any);
   - never commits; prints the path of the stack's `INIT.md`.
3. Open Claude Code in the project and run `/kickoff`.
4. Run `/plan`, approve tasks and milestones, then `/task`.

## 5. `/kickoff` — interview and project files

Reads `.harness/questions/core.md` and `stacks/<stack>/questions.md` (copied into the project at init), asks one
focused question at a time, then writes `CLAUDE.md` (short), `docs/spec.md`, `docs/design.md`, `.harness/harness.toml`
(gates, ladder, budgets) and the three roles. Core question areas:

1. Purpose and audience; how "done" is recognised.
2. Constraints: hosting, deadlines, language, accessibility and motion policy.
3. Workers and machine: local models available, context length and output cap, GPU memory, which Claude models and
   subscription are available.
4. Gates: fast and full check commands, how long they take, whether a browser is installed for visual checks.
5. Scope and protected data: generated files never edited by hand, untouchable folders.
6. Task budget: files per task and spec length, calibrated to the worker.
7. Numbers and code rules: values never typed by hand, conventions, allowed dependencies.
8. Human verification: what the author tests by eye and how (editor, browser, console).
9. Project mode: `production` or `learning`.

Every question exists because of a real problem (see `docs/lessons.md`); new ones arrive through `/harvest`.

## 6. Roles

`/kickoff` generates three short roles in `.harness/roles/` (3–6 lines each — the local worker pays for them in
every request):

- **implementer** — the worker (local or Claude). Used as the worker's system prompt.
- **reviewer** — whoever reviews a diff.
- **planner** — Claude when running `/plan`; summarised in `CLAUDE.md`.

A role states: specialty, mission, what it must **not** do, and the format of its answer. In `learning` mode the
implementer adds comments that explain *why*, and the reviewer explains corrections instead of only listing them.
Roles are guidance, not a security boundary: permissions and the scope guard are.

## 7. Planning, milestones and progress

`/plan` turns spec and design into task files and **proposes milestones**. A milestone is a point where a piece of
functionality is complete and the author can **test it** (for example, in the Unity Editor). Each milestone has:
goal, tasks, **how to test it**, and done criteria. The author approves milestones together with the task table.

Optionally `/kickoff` records a maximum of machine hours per session; a milestone estimated beyond it is split.

When a milestone is complete, Claude stops, summarises, repeats "how to test it" and asks whether to continue with the
next milestone or stop. It never starts the next one on its own. Review by Claude happens **per task**, as soon as a
task finishes; the milestone is the stop-and-test point.

Progress lives in `docs/progress/progress.md` (in git): milestones, status, current task, decisions. `/resume`
reads it together with task states and git, and reports: last finished milestone, current milestone with done and
pending tasks, any half-done task branch (continue or discard), notes not yet harvested, a newer template version.
Then it asks whether to continue.

After the author tests a milestone by eye, `/qa` turns what they saw into numbered items in `docs/tasks/qa/qa-<milestone>.md`,
creates one task per item (in `docs/tasks/qa/`, each with its own check), waits for approval and then hands them to `/task`. The
milestone is not closed while its QA log has open items.

## 8. The worker

A single portable Python script, `.harness/run_worker.py`, replaces the PowerShell launcher and the separate proxy.
Invoked by `/task` as `python .harness/run_worker.py <task.md> [--model X]`.

### 8.1 Backends

- **Local server** speaking the Anthropic API (LM Studio, Bionic…). Claude Code (`claude -p`) is pointed at an
  **in-process proxy** on a free port that moves any `role: "system"` entry out of `messages` into `system`
  (otherwise some chat templates fail with "System message must be at the beginning"). The proxy can also strip the
  `thinking`, `output_config` and `context_management` fields (`strip_thinking`, see §8.3).
- **Claude** (`claude -p --model haiku|sonnet`), no proxy.

Claude Code is started with a reduced tool set (`--tools`), a short `--system-prompt` (the implementer role), and an
output cap (`CLAUDE_CODE_MAX_OUTPUT_TOKENS`) so a looping model fails fast; the default prompt (~36k tokens) would not
fit a 32k context.

### 8.2 Model discovery and loading

`GET /api/v0/models` lists **downloaded** models with `state` and `type` (chat models are `llm`/`vlm`);
`GET /api/v1/models` adds `loaded_instances`. Loading uses `POST /api/v1/models/load {"model": id}` (404/405 → the server
loads on first use); unloading uses `POST /api/v1/models/unload {"instance_id": ...}`. Always write the address as
`127.0.0.1:<port>`, never `localhost` (L-026).

Which model is used (`[workers.local]` in `harness.toml`):
- `model` is the **preferred** model and `fallback_model` an optional **secondary** one (`/kickoff` asks for both).
- `--model X` on the command line wins over the configuration.
- If a model is already loaded the script uses it (the preferred one first, then the secondary, then whatever is loaded, with a
  note) instead of loading another on top of it.
- If nothing is loaded it tries to load the preferred model and, if that fails (for example not enough memory), the secondary.
- With nothing configured it uses the only loaded model, or asks (or prints the list and exits with a dedicated code when started by
  Claude, which asks the author and runs again with `--model`). The last model used is stored in `.harness/state/` (git-ignored).

Loading is guarded because a second load order for a loaded model creates a second instance that uses the memory twice
(L-027): the loaded instances are checked first, a load order is never repeated (after an error the script waits and looks again),
loading is serialised with a lock file, and only **one run per project** is allowed at a time (`.harness/state/worker.lock`,
exit code 6).

### 8.3 Ladder and attempts

Configured per project, for example `local → claude-haiku → claude-sonnet → main Claude`.

- `local`: **3 attempts** before escalating (the author wants development to stay local); Claude workers 1–2.
- An *attempt* is the first try or a correction round. After an overflow or no output the retry does **not** repeat
  the same prompt; it adds: one file per write call, compact code, no explanations, no temporary files. After failed
  gates the retry includes the failure output and the files outside scope.
- A timed-out attempt counts as failed; what it wrote is kept so the next attempt continues from there.
- The last step is the main Claude session, which takes over by hand.
- **Thinking policy.** `strip_thinking_attempts = 2` (default): attempts 1 and 2 of the local worker run with the `thinking`,
  `output_config` and `context_management` fields removed (same quality, 2-6x faster in the tests, L-024, L-025); attempt 3 keeps them
  as a safety net. `strip_thinking = true` strips every attempt. Only easy tasks have been measured so far.

### 8.4 Inner loop (automatic)

After every delivery: **scope guard** → **gates** → on failure feed the output back to the same worker (up to the
attempt limit) → escalate → only when everything passes, return a **review brief** to Claude: diff stat, gate results,
scope result, worker and rounds used.

- **Scope guard**: compares changed files with the task's "Files in scope"; deletes obvious temporary files
  (`_tmp*`, `*.tmp`, `scratch/`, debug scripts) and flags the rest.
- **Gates**: two lists in `harness.toml`. `fast` (compile, quick tests) runs in the inner loop; `full` runs once
  before Claude is called. If even `fast` does not fit the stack's timeout the script warns at start-up and suggests
  splitting the tests.

### 8.5 Timeouts and calibration

Maximum time per attempt = **worker time** (from the model's measured speed, per model) + **two gate passes**.

Initial table (minutes, worker / one gate pass): web 10/5 (measured), rust 12/10, dotnet 12/10, cpp 12/8,
python 8/5, unity with stubs 12/5, unity with the real Editor 15/15–20 and unreal 20/30–60 (the last two unmeasured).

Calibration is automatic:

- **At `init`/first run**: run the gates cold and warm; the gate timeout is 3 × the measured value between the
  stack's floor and ceiling; if the measurement is more than 5 × the table the author is asked to confirm; an empty
  project keeps the table values and is flagged *provisional*; recalibrate after the first 3 finished tasks.
- **Continuously**: record every gate pass and attempt duration in `.harness/state/` (per machine); timeout = p90
  of the last 10 × a margin, clamped to floor/ceiling, rising quickly and falling slowly; a timed-out run raises the
  limit ×1.5 up to the ceiling before escalating; a change of more than 2 × triggers a warning and recalibration.
- Model speed (prefill and generation tokens/s) is measured once per model.

## 9. Traceability: notes, `/harvest`, `/sync`

- Every project has `docs/harness-notes.md`. When the harness itself misbehaves, Claude appends an entry:
  date, what happened, cause, remedy, **applies to** (`core`, `stack:<name>` or `project`), status (`new`,
  `harvested <template-commit>`). `/task` reminds Claude to check at the end of any task that needed escalation or
  more than one round.
- **`/harvest <project-path>`**, run by the author from the template folder at any milestone: Claude reads the new
  entries, the author decides per entry (core / stack / discard), Claude edits the template, adds a `CHANGELOG.md`
  line and commits with `Source: <project>#<note>`. The author pushes. The project's note is marked harvested.
- **`/sync`**, run in a project: compares the managed files with the template and applies only those.
- A reminder (never automatic action) appears when 5 or more notes are un-harvested.
- **Guardrails** (`docs/guardrails.md`, owned by the project). *Enforced* section: pointers to what the tools already
  enforce (`[scope] protected`, scope guard, gates, permissions). *Signs* section: one line per rule learned from a
  failure, `When <situation>: <rule>. Evidence: <...>`, at most 20. `run_worker.py` appends the signs to the worker's
  system prompt; `/task` review checks them. After a correction round, an escalation or a `/qa` defect Claude proposes a
  sign and the author approves it; no evidence, no sign. The file is advice, not a security boundary: anything that
  must hold goes in a gate or `protected`. `/harvest` offers signs that help other projects. Idea from Google's
  Harness2 (editable `guardrails.md`, evidence-backed lessons, enforcement outside the editable harness).

## 10. Stacks

| stack | status | gates (fast) | notes |
|---|---|---|---|
| web | tested (Vite + Vitest); plain HTML5 / other frameworks untested | project test + build | browser checks via Playwright MCP |
| unity | skeleton | compile + EditMode tests (batch) | slow Editor start; two-level gates are essential |
| rust | skeleton | `cargo build`, `cargo test` | first build is cold and slow |
| dotnet | skeleton | `dotnet build`, `dotnet test` | |
| cpp | skeleton | build + tests (CMake/Make) | reuse compiler detection (g++/clang/MSVC) |
| python | skeleton | `pytest` (+ `ruff`, `mypy` optional) | no compile step; venv permissions |

Each stack has an `INIT.md` of at most 25 lines (create the project with its own tool, `git init`, `.gitignore`,
`init.py`, record executable paths, `/kickoff`, `/plan`, first milestone) and a short "how to verify" section.
Unreal can be added later as another stack.

## 11. Question bank per stack (examples)

- **web**: plain HTML or framework; supported browsers; responsive breakpoints; motion policy; i18n.
- **unity**: version; render pipeline; EditMode vs PlayMode tests; batch-mode executable path; target platforms.
- **rust**: workspace; minimum compiler version; `unsafe` allowed; clippy level.
- **dotnet**: target framework; test framework; database; API style.
- **cpp**: standard; build system; test framework; warning policy; sanitizers.
- **python**: version; environment manager (venv/uv/poetry); app type; type-checking and lint level.

## 12. Implementation phases

1. **Phase 1 (this repository now):** spec, lessons, `init.py` with tests, core templates, stack skeletons.
2. **Phase 2:** `run_worker.py` (proxy, discovery, ladder, scope guard, inner loop, calibration) with unit tests;
   adopt it in `bench-site` first, then in the template.
3. **Phase 3:** `/harvest` and `/sync` exercised on a second real project; promote skeleton stacks as they are used.

Status: phases 1 and 2 are done (`bench-site` was the first project to use the unified worker). Phase 3 starts with the next
project (a Unity one); `bench-site` already carries `[template]` data in its `harness.toml` so `/sync` can compare against this repository.

## 13. Open items

- Resolved: Bionic serves `/api/v0/models`, `/api/v1/models` (with `loaded_instances`), `/load` and `/unload` like LM Studio.
- Resolved: stripping `thinking`/`output_config`/`context_management` in the proxy keeps quality and is much faster (L-024, L-025);
  it does not by itself explain the early output overflows (those need smaller tasks, L-003).
- To measure on harder tasks: the thinking policy of §8.3 (only small, well-specified tasks so far).
- Real Unity batch-mode timings; how to run Unity tests headless on the author's machine.
- Plain-HTML5 web projects: which gates make sense.
- Future idea (not scheduled): Claude Code Projects (beta, Sept 2026) splits a goal across parallel cloud sessions. Cloud sessions clone the repo from GitHub and cannot reach the local model server, so they do not fit the local worker today. Revisit when Projects can run in a local environment; until then it could only take over the Claude-tier work (tasks that start at `claude-sonnet`) on stacks whose gates run in the cloud.
- Future idea (not scheduled): a per-project `tool_guidance.md` (when to use which command, what to avoid) generated by `/kickoff`, and a short reflection step when a milestone closes that feeds `docs/guardrails.md`. Wait for evidence from a real project.
