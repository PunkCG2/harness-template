# Start a Unity project (skeleton: untested)

1. Create the project in **Unity Hub first** (an empty folder is required). Pick the version and pipeline.
2. In that folder: `git init`; make sure `.gitignore` excludes `Library/`, `Temp/`, `Obj/`, `Logs/`, `UserSettings/`.
   Set "Visible Meta Files" and "Force Text" serialization in Project Settings. Commit.
3. `python <harness-template>\init.py --stack unity --into <project>`; review with `git status`; commit.
4. Write the Editor executable path into `.harness/harness.toml` (`[verify] unity_path`) and the batch-mode test
   commands into `[gates]` (see the comments in the file).
5. Open Claude Code in the folder and run `/kickoff`, then `/plan`.
6. Approve milestones (each one ends with steps you test in the Editor) and start with `/task next`.

## Verifying
- Run the gate commands once by hand to see they work and how long they take (cold, then warm).
- Each milestone: open the scene named in "how to test it", press Play, follow the steps.
