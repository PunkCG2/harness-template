# Unity questions for /kickoff (skeleton: untested)

- Unity version and the full path of the Editor executable (for batch mode)?
- Render pipeline (Built-in, URP, HDRP)? Target platforms?
- Tests: EditMode, PlayMode or both? Where do they live (asmdefs)? How long does a headless run take, cold and warm?
- Which assets are authored in the Editor by the author (scenes, prefabs) and which are code the worker may write?
- Folder and namespace conventions (e.g. `Game.<Folder>`)? Balance values that must never be typed by hand?
- What does the author test in the Editor at each milestone (scene to open, what to press, what to see)?
- Machine-time limit per session (a Unity project can be long even in machine time)?
