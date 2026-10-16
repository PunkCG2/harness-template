# AI Dev Harness

A starter kit for AI-assisted development with a **local-first worker**: a local model implements small tasks,
automatic checks verify them, and Claude plans and reviews. Works for any stack (web, Unity, Rust, .NET, C++, Python…).

> Status: phases 1 and 2 are done (spec, lessons, `init.py`, core templates, the unified worker `core/.harness/run_worker.py`
> and the skills). Phase 3 is using the template on a real Unity project. Read [`docs/spec.md`](docs/spec.md) first.

## Requirements

- Python 3 and Git (`init.py` and the worker use only the standard library).
- [Claude Code](https://claude.com/claude-code).
- Optional, for the local worker: a local model server (LM Studio or Bionic) listening on `127.0.0.1:<port>`.
- The tools of your stack (Node.js, Unity Hub, Rust, .NET SDK, CMake…). Each stack's `INIT.md` lists them.

## Stacks

| stack | status |
|---|---|
| `web` | tested (Vite + vanilla JS + Vitest) |
| `unity`, `rust`, `dotnet`, `cpp`, `python` | skeletons: questions and install guides exist, not yet proven on a real project |

`python init.py --list` shows them.

## Quick start

`<harness-template>` is the folder where you cloned this repository.

```
git clone <this repository> <harness-template>             # once
# create your project with its own tool (Unity Hub, cargo new, npm create…), then:
cd <project> && git init
python <harness-template>/init.py --stack <stack> --into .
git status                                                  # review what was added
claude                                                      # open Claude Code in the project
/kickoff                                                    # interview → CLAUDE.md, spec, design, roles, harness.toml
/plan                                                       # tasks + milestones, you approve
/task next                                                  # worker implements, gates run, Claude reviews
```

`init.py` copies the core plus the chosen stack into the project. It never overwrites, commits or pushes: if any
destination file already exists it writes nothing and lists the conflicts.

### Install guides

Each stack ships a step-by-step install guide: prerequisites, how to create the project, where the harness is copied
and started, what `init.py` writes, and how to verify. After `init.py` it is also available inside the project as
`.harness/INIT.md`. Source files: [`stacks/<stack>/INIT.md`](stacks).

## How `/kickoff` works

`/kickoff` is an interview that writes `CLAUDE.md`, `docs/spec.md`, `docs/design.md`, the three roles and
`.harness/harness.toml`.

- **Detect first.** It reads what the repository, the installed tools and the local server can tell it (tool versions,
  packages, installed models through `GET /api/v0/models`) and only asks you to confirm or fill the gaps.
- **One question at a time**, in your language, with a recommended default when there is one.
- **Order:** purpose and constraints, then the stack questions, then workers, gates, scope, budget, code rules and how you
  verify each milestone.
- **Free-text "feel" question** for style, mood and details that may affect architecture.
- **Fixed, not asked:** the worker ladder (2 local attempts without thinking, 1 with thinking, then Claude Haiku, Sonnet and
  the main session), no Claude budget limit, and a git workflow proposed by Claude.

The question banks live in [`core/.harness/questions/core.md`](core/.harness/questions/core.md) and
`stacks/<stack>/questions.md`.

## Daily use

| command | what it does |
|---|---|
| `/kickoff` | interviews you and writes the project files |
| `/plan` | creates tasks and proposes testable milestones |
| `/task <file or next>` | runs one task: worker → gates → review → merge |
| `/qa` | turns your by-eye review into items, tasks and checks in `docs/tasks/qa/` (asks for approval) |
| `/resume` | continues where the last session stopped |
| `/sync` | updates the managed files of a project from the template |
| `/harvest <project>` | (from this folder) moves lessons from a project's `docs/harness-notes.md` into the template |

## Layout

See [`docs/spec.md`](docs/spec.md) §3. Lessons already learned are in [`docs/lessons.md`](docs/lessons.md); changes are
listed in [`CHANGELOG.md`](CHANGELOG.md).

## Tests

```
python -m unittest discover -s tests
```
