# AI Dev Harness

A starter kit for AI-assisted development with a **local-first worker**: a local model implements small tasks,
automatic checks verify them, and Claude plans and reviews. Works for any stack (web, Unity, Rust, .NET, C++, Python…).

> Status: **phase 1** — spec, lessons, `init.py`, core templates and stack skeletons. The unified worker script
> (`core/.harness/run_worker.py`) is phase 2. Read [`docs/spec.md`](docs/spec.md) first.

## Quick start

```
git clone <this repository> E:\IA\harness-template        # once
# create your project with its own tool (Unity Hub, cargo new, npm create…), then:
cd <project> && git init
python E:\IA\harness-template\init.py --stack unity --into <project>
git status                                                   # review what was added
claude                                                       # open Claude Code in the project
/kickoff                                                     # interview → CLAUDE.md, spec, roles, harness.toml
/plan                                                        # tasks + milestones, you approve
/task next                                                   # worker implements, gates run, Claude reviews
```

`python init.py --list` shows the available stacks. Each stack has an `INIT.md` with its own short steps.

## Daily use

| command | what it does |
|---|---|
| `/kickoff` | interviews you and writes the project files |
| `/plan` | creates tasks and proposes testable milestones |
| `/task <file or next>` | runs one task: worker → gates → review → merge |
| `/qa` | turns your by-eye review into items, tasks and checks in `docs/tasks/qa/` (asks for approval) |
| `/resume` | continues where the last session stopped |
| `/harvest <project>` | (from this folder) moves lessons from a project's `docs/harness-notes.md` into the template |
| `/sync` | updates the managed files of a project from the template |

## Layout

See [`docs/spec.md`](docs/spec.md) §3. Lessons already learned are in [`docs/lessons.md`](docs/lessons.md).

## Tests

```
python -m unittest discover -s tests
```
