---
name: sync
description: Compares a project's managed harness files with the template and applies only those. Use when the user says /sync or asks to update the harness in a project.
---

# Sync (run in a project)

Managed files (safe to replace): `.harness/run_worker.py`, `.harness/questions/`, `.claude/skills/`.
Paths listed in `[sync] skip` of `.harness/harness.toml` are never replaced (for example skills a project translated).
Owned files (never touch): `CLAUDE.md`, `docs/`, `.harness/harness.toml`, `.harness/roles/`, `.claude/settings.json`. `docs/guardrails.md` is the project's own record of failures; for a project
that predates it, only suggest copying the template.

1. Ask for the template folder if it is not in `.harness/harness.toml` (`[template] path`). Read its `CHANGELOG.md`
   and compare `[template] version` with the template's current commit.
2. List which managed files differ and summarise the changelog entries since the project's version.
3. Show the diff of each managed file; apply only what the author approves. For owned files that gained new
   defaults in the template (for example a new `harness.toml` key), only **suggest** the change.
4. Update `[template] version` after applying. Do not commit.
