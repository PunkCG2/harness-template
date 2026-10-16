# C++ questions for /kickoff (skeleton)

**Read before asking** (versions, tools, dependencies): compiler, CMake and Visual Studio versions from the installed tools. Only confirm what is found; ask the rest.

- Library or executable? Which target platforms?
- C++ standard (17, 20, 23)? On Windows is Visual Studio Build Tools installed?
- Build system (CMake, Make, MSBuild)? Where is the build folder?
- Test framework (Catch2, GoogleTest, plain asserts)? How are tests run?
- Warning policy? Formatter (clang-format)?
- Memory rules (RAII, smart pointers only, raw pointers allowed where)?
- Allowed third-party libraries and how they are fetched (offline?)?

## Default architecture
RAII everywhere, smart pointers for ownership, small headers, no globals.

## Fixed, not asked
- Sanitizers (ASan/UBSan) are part of the full gate where the compiler supports them.
