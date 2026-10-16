# Install the harness in a Rust project (skeleton)

## Prerequisites
- Rust toolchain (rustup) with its linker toolchain, Git, Python 3, Claude Code.
- A local model server (LM Studio or Bionic) on `127.0.0.1:<port>`, optional but needed for the local worker.

## Steps
1. **Create the project with its own tool**: `cargo new <name>` (or `--lib`) and check that `cargo build` works.
2. **Start git**: `git init` (cargo may already do it), commit the generated files.
3. **Copy the harness**: `python <harness-template>\init.py --stack rust --into <project>`.
4. **Review and commit**: `git status`, then commit the harness files.
5. **Start the harness**: open Claude Code in the folder and run `/kickoff`.

The first gate pass is cold and slow; the harness calibrates the timeout from it.

## What `init.py` does (and does not)
- Copies `.claude/` (settings and skills), `.harness/` (worker, roles, questions, `harness.toml`), `CLAUDE.md` and `docs/` into the project.
- Merges the stack's permissions into `.claude/settings.json` and records the template version in `harness.toml`.
- Creates `.gitignore` if missing; if one exists it only prints the lines to add (`.harness/state/` and the stack's lines).
- If any destination file already exists it writes **nothing** and lists the conflicts (exit code 2): move them and run again.
- Never commits, never pushes, never overwrites. Use `--dry-run` to see the file list first.

## After `init.py`
1. Review with `git status`, add the `.gitignore` lines it printed if any, and commit the harness files.
2. Open Claude Code in the project folder and run `/kickoff`. It detects what it can, then interviews you one question at a time.
3. Review the files it writes, then run `/plan`: it creates tasks and proposes testable milestones for you to approve.
4. Run `/task next`. The worker implements, the gates run, Claude reviews and merges.
5. Test each milestone by hand ("how to test it") and use `/qa` to report what you saw.

## Later
- `/sync` (from the project) pulls updated harness files from the template. It needs `[template] path` in `.harness/harness.toml`
  to point at the template folder; files listed in `[sync] skip` are left alone.
- Lessons learned in the project go to `docs/harness-notes.md`; `/harvest <project>`, run from the template, moves them back.

## Verifying
- Gates: `cargo build` and `cargo test` (fast); add `cargo clippy -- -D warnings` for the full gate.
- Milestones are usually "run the binary / the test suite and check the output".
