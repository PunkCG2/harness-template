# Unity questions for /kickoff (skeleton: untested)

The project already exists in the folder where `/kickoff` runs. **Read before asking**, and only confirm what is found:
- Unity version: `ProjectSettings/ProjectVersion.txt`. Editor executable: the Unity Hub install folder for that version.
- Render pipeline, Input System and installed packages: `Packages/manifest.json`. Target platforms: build settings.
- Existing asmdefs, test assemblies, folders and namespaces: `Assets/`.
- Same rule for any other tool version the project needs (Git LFS, .NET SDK, IDE, plugins).

## Questions
- Which target platforms, if the build settings do not say?
- Tests: EditMode, PlayMode or both? Propose from the existing test assemblies.
- Which folder and namespace convention? Propose `Game.<Folder>` when the project has none.
- Which packages beyond the ones in `manifest.json` may the worker add? Default: none.

## Fixed, not asked
- Input: the new Input System.
- Git: Git LFS enabled; `.gitignore` starts from GitHub's standard Unity template and grows with the project.
- Test commands: build them with the `unity:unity-cli` skill (batch mode, `-runTests`), run them once and record the
  cold and warm timings in `[gates]` and `[timing]`.
- Who edits what:
  - Worker (local models): C# scripts and token-expensive tasks.
  - Scenes (`.unity`): the author, by hand in the Editor.
  - Prefabs (`.prefab`): never the local worker; the task starts at `claude-sonnet` (`--start claude-sonnet`) or runs in the main Claude session.
- `[scope] protected`: `ProjectSettings/**`, `Packages/manifest.json`, `**/*.meta`, `**/*.unity`, `**/*.prefab`, `Library/**`, `Temp/**`.
