# Start a .NET project (skeleton)

1. `dotnet new <template> -n <name>` (for example `webapi` or `classlib`) and a test project if needed; `dotnet build`.
2. `git init`; add a `.gitignore` for .NET (`bin/`, `obj/`); commit.
3. `python <harness-template>\init.py --stack dotnet --into <project>`; review with `git status`; commit.
4. Open Claude Code in the folder and run `/kickoff`, then `/plan`.
5. Start with `/task next`.

## Verifying
- Gates: `dotnet build` and `dotnet test`.
- Milestones for APIs: run the app and call the endpoints listed in "how to test it".
