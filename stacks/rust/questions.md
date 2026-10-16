# Rust questions for /kickoff (skeleton)

**Read before asking** (versions, tools, dependencies): `rustc --version`, `rust-toolchain` and `Cargo.toml`. Only confirm what is found; ask the rest.

- Library or binary? Single crate or workspace?
- Domain: CLI, library, systems, service?
- Concurrency or async? With which runtime?
- Minimum supported Rust version; allowed dependencies (offline builds?).
- Clippy level (`-D warnings`)?
- Error handling style (custom enum, `thiserror`, `anyhow`)?

## Default architecture
Small modules, `Result` everywhere, no global mutable state.

## Fixed, not asked
- `unsafe` is forbidden unless the author approves it explicitly.
