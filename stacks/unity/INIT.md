# Install the harness in a Unity project (skeleton: untested)

## Prerequisites
- Unity Hub with the Editor version you want installed, Git and Git LFS, Python 3, Claude Code.
- A local model server (LM Studio or Bionic) on `127.0.0.1:<port>`, optional but needed for the local worker.

## Steps
1. **Create the project in Unity Hub first**. Pick the version and render pipeline; install the Input System package (the new one is the standard here).
2. **Start git** in the project folder: `git init`, `git lfs install`. Use GitHub's standard Unity `.gitignore` as the base
   (it excludes `Library/`, `Temp/`, `Obj/`, `Logs/`, `UserSettings/`); it grows with the project. Track binary assets with
   LFS (`.gitattributes`) and configure `UnityYAMLMerge` as the merge tool for `*.unity` and `*.prefab`.
3. **Set Project Settings**: "Visible Meta Files" and "Force Text" serialization. Commit.
4. **Copy the harness**: `python <harness-template>\init.py --stack unity --into <project>`.
5. **Review and commit**: `git status`, add the printed `.gitignore` lines, commit.
6. **Start the harness**: open Claude Code in the folder and run `/kickoff`. It reads the Unity version, the Editor path,
   the pipeline and the packages for you, and uses the `unity:unity-cli` skill to build the headless test commands.

## What `init.py` does (and does not)
- Copies `.claude/` (settings and skills), `.harness/` (worker, roles, questions, `harness.toml`), `CLAUDE.md` and `docs/` into the project.
- Merges the stack's permissions into `.claude/settings.json` and records the template version in `harness.toml`.
- Creates `.gitignore` if missing; if one exists it only prints the lines to add (`.harness/state/` and the stack's lines).
- If any destination file already exists it writes **nothing** and lists the conflicts (exit code 2): move them and run again.
- Never commits, never pushes, never overwrites. Use `--dry-run` to see the file list first.

## After `init.py`
1. Review with `git status`, add the `.gitignore` lines it printed if any, and commit the harness files.
2. Open Claude Code in the project folder and run `/kickoff`. It detects what it can, then interviews you one question at a time.
3. Review the files it writes, then run `/plan`: it creates tasks and proposes testable milestones for you to approve.
4. Run `/task next`. The worker implements, the gates run, Claude reviews and merges.
5. Test each milestone by hand ("how to test it") and use `/qa` to report what you saw.

## Later
- `/sync` (from the project) pulls updated harness files from the template. It needs `[template] path` in `.harness/harness.toml`
  to point at the template folder; files listed in `[sync] skip` are left alone.
- Lessons learned in the project go to `docs/harness-notes.md`; `/harvest <project>`, run from the template, moves them back.

## Verifying
- `/kickoff` runs the gate commands once to record cold and warm timings.
- Each milestone: open the scene named in "how to test it", press Play, follow the steps. Scenes are yours; the task
  lists any Inspector wiring you must do by hand.
