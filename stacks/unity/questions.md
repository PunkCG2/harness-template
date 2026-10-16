# Unity questions for /kickoff (skeleton: untested)

The project already exists in the folder where `/kickoff` runs. **Read before asking**, and only confirm what is found:
- Unity version: `ProjectSettings/ProjectVersion.txt`. Editor executable: the Unity Hub install folder for that version.
- Render pipeline, Input System and installed packages: `Packages/manifest.json`. Target platforms: build settings.
- Existing asmdefs, test assemblies, folders and namespaces: `Assets/`.
- UI system (uGUI or UI Toolkit), Addressables, Cinemachine, DOTween, TextMeshPro, Localization: `manifest.json` and `Assets/`.
- Same rule for any other tool version the project needs (Git LFS, .NET SDK, IDE, plugins).

## Questions
Game first, then technical.
- What kind of game is it: 2D or 3D, camera (top-down, side, first person…) and genre?
- Single player or multiplayer? If multiplayer, which model (co-op, versus, dedicated server, relay)?
- Describe the **feel** you want in your own words: pace, weight of movement, responsiveness, game juice, mood, references
  to other games. Add anything else that may seem minor but could affect architecture or implementation (determinism,
  replays, mods, many entities, long sessions, accessibility, controller support…). Free text; Claude turns it into
  architecture notes in `docs/design.md`.
- Which performance target: frames per second and minimum hardware (PC, mobile, Quest)? If XR, apply the `meta-vr` skills.
- Where does art and audio come from: placeholders (primitives, free assets) or final assets? Who imports them and with
  which import settings?
- Scope of the first milestone: minimal playable prototype or vertical slice?
- Is there save/load? If so, where and in which format?
- Preferred architecture? Default: ScriptableObjects for data, C# events for communication, no singletons.
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
- Scene wiring: scenes are the author's, so every task that adds a `[SerializeField]` lists the Inspector steps to do by
  hand (component, field, reference) under "how to test it".
- Scene merges: configure `UnityYAMLMerge` as the git merge tool for `.unity` and `.prefab` (see `INIT.md`).
- Editor scripts: the worker may write them but never runs them against scenes or prefabs.
