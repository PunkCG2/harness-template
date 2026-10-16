# Python questions for /kickoff (skeleton)

**Read before asking** (versions, tools, dependencies): `python --version`, `pyproject.toml`, lockfiles and the environment manager in use. Only confirm what is found; ask the rest.

- App type: script/CLI, library, desktop GUI, web service, data/ML?
- Is it distributed (package, executable) or only for your own use?
- If it has a GUI, which toolkit?
- Tests with pytest? Type checking (mypy/pyright) and lint (ruff) level?
- Entry point and how the author runs it to check a milestone?

## Default architecture
Small modules with type hints, pure functions for logic, I/O at the edges.

## Fixed, not asked
- The worker never installs packages; the author installs them by hand inside the environment.
