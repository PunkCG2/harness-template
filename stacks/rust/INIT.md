# Start a Rust project (skeleton)

1. `cargo new <name>` (or `--lib`). Check `cargo build` works. Install the linker toolchain if the build fails.
2. `git init` (cargo may already do it); commit the generated files.
3. `python <harness-template>\init.py --stack rust --into <project>`; review with `git status`; commit.
4. Open Claude Code in the folder and run `/kickoff`, then `/plan`.
5. Start with `/task next`. The first gate pass is cold and slow; the harness calibrates the timeout from it.

## Verifying
- Gates: `cargo build` and `cargo test` (fast); add `cargo clippy -- -D warnings` for the full gate.
- Milestones are usually "run the binary / the test suite and check the output".
