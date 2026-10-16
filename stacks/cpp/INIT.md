# Start a C++ project (skeleton)

1. Create the folder with a `CMakeLists.txt` (C++17+), a `src/` and a `tests/` folder; configure once:
   `cmake -S . -B build` and check `cmake --build build` works with your compiler.
2. `git init`; ignore `build/`; commit.
3. `python <harness-template>\init.py --stack cpp --into <project>`; review with `git status`; commit.
4. Open Claude Code in the folder and run `/kickoff` (it detects the compiler), then `/plan`.
5. Start with `/task next`.

## Verifying
- Gates: `cmake --build build` and `ctest --test-dir build --output-on-failure`.
- Milestones: run the executable or tests listed in "how to test it".
