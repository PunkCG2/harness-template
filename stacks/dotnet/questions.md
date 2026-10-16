# .NET questions for /kickoff (skeleton)

**Read before asking** (versions, tools, dependencies): `dotnet --version`, `global.json` and the project files. Only confirm what is found; ask the rest.

- Web API, console or library?
- Where is it deployed?
- Is there authentication?
- Which external services does it use (database, queues, third-party APIs)? In-memory replacements for tests?
- Test framework (xUnit, NUnit, MSTest)? Integration tests that start the app?
- API style (minimal APIs, controllers), validation approach, error format (ProblemDetails)?

## Default architecture
Small services behind interfaces, dependency injection, no static state.
