#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init.py - copy the harness core plus one stack into a project.

    python init.py --list
    python init.py --stack unity --into E:\\Projects\\MyGame
    python init.py --stack web --into . --dry-run

Rules (see docs/spec.md section 4):
  * the stack wins over the core when both provide a file;
  * if any destination file already exists, NOTHING is written and the conflicts are listed (exit code 2);
  * never commits, never pushes, never touches files it does not create.
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
CORE = ROOT / "core"
STACKS = ROOT / "stacks"

# Files inside stacks/<stack>/ that are inputs for the merge (not copied as they are).
STACK_INPUTS = {"stack.toml", "permissions.json", "CLAUDE.part.md", "questions.md", "INIT.md", "gitignore.part"}


def list_stacks():
    if not STACKS.is_dir():
        return []
    return sorted(p.name for p in STACKS.iterdir() if p.is_dir() and (p / "stack.toml").exists())


def template_version():
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return "unversioned"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def render(text, ctx):
    for key, value in ctx.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def merge_settings(core_text, stack_perm_text):
    settings = json.loads(core_text)
    perms = settings.setdefault("permissions", {})
    extra = json.loads(stack_perm_text) if stack_perm_text else {}
    for kind in ("allow", "deny"):
        merged = list(perms.get(kind, []))
        for item in extra.get(kind, []):
            if item not in merged:
                merged.append(item)
        perms[kind] = merged
    return json.dumps(settings, indent=2, ensure_ascii=False) + "\n"


def build_plan(stack, project):
    """Returns {relative destination path: text}."""
    sdir = STACKS / stack

    def stack_file(name):
        p = sdir / name
        return read(p) if p.exists() else ""

    ctx = {
        "project_name": project.name,
        "stack": stack,
        "date": datetime.date.today().isoformat(),
        "template_version": template_version(),
        "stack_rules": stack_file("CLAUDE.part.md").strip(),
        "stack_toml": stack_file("stack.toml").strip(),
    }
    plan = {}
    for src in sorted(CORE.rglob("*")):
        if not src.is_file() or "__pycache__" in src.parts:
            continue
        rel = src.relative_to(CORE).as_posix()
        text = read(src)
        if rel.endswith(".tmpl"):
            rel = rel[: -len(".tmpl")]
            text = render(text, ctx)
        if rel == ".claude/settings.json":
            text = merge_settings(text, stack_file("permissions.json"))
        plan[rel] = text
    # Stack inputs that are copied for reference inside the project.
    plan[".harness/questions/stack.md"] = stack_file("questions.md")
    plan[".harness/INIT.md"] = stack_file("INIT.md")
    # Anything else a stack ships (extra templates) is copied under the same relative path.
    for src in sorted(sdir.rglob("*")):
        if src.is_file() and "__pycache__" not in src.parts and src.relative_to(sdir).as_posix() not in STACK_INPUTS:
            plan[src.relative_to(sdir).as_posix()] = read(src)
    return plan, stack_file("gitignore.part")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Copy the harness core plus one stack into a project.")
    ap.add_argument("--stack", help="stack name (see --list)")
    ap.add_argument("--into", help="project folder (must already exist)")
    ap.add_argument("--list", action="store_true", help="list the available stacks")
    ap.add_argument("--dry-run", action="store_true", help="show what would be written and change nothing")
    args = ap.parse_args(argv)

    stacks = list_stacks()
    if args.list:
        for name in stacks:
            status = "skeleton"
            for line in read(STACKS / name / "stack.toml").splitlines():
                if line.strip().startswith("status"):
                    status = line.split("=", 1)[1].strip().strip('"')
            print(f"{name:8} {status}")
        return 0
    if not args.stack or not args.into:
        ap.print_usage()
        print("error: --stack and --into are required (or use --list)", file=sys.stderr)
        return 1
    if args.stack not in stacks:
        print(f"error: unknown stack '{args.stack}'. Available: {', '.join(stacks)}", file=sys.stderr)
        return 1
    project = Path(args.into).resolve()
    if not project.is_dir():
        print(f"error: the project folder does not exist: {project}", file=sys.stderr)
        return 1

    plan, gitignore_part = build_plan(args.stack, project)
    conflicts = sorted(rel for rel in plan if (project / rel).exists())
    if conflicts:
        print("Nothing was written. These files already exist in the project:", file=sys.stderr)
        for rel in conflicts:
            print(f"  {rel}", file=sys.stderr)
        print("Move or delete them (or merge by hand) and run init again.", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"Would write {len(plan)} files into {project}:")
        for rel in sorted(plan):
            print(f"  {rel}")
        return 0

    for rel, text in plan.items():
        dest = project / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")

    ignore_lines = [l for l in ["# harness", ".harness/state/"] + gitignore_part.splitlines() if l.strip()]
    gi = project / ".gitignore"
    if not gi.exists():
        gi.write_text("\n".join(ignore_lines) + "\n", encoding="utf-8", newline="\n")
        ignore_note = "created .gitignore"
    else:
        missing = [l for l in ignore_lines if l not in gi.read_text(encoding="utf-8").splitlines()]
        ignore_note = ("add these lines to your .gitignore: " + ", ".join(missing)) if missing else ".gitignore already covers the harness"

    print(f"Wrote {len(plan)} files into {project} (stack: {args.stack}, template {template_version()}).")
    print(f".gitignore: {ignore_note}")
    print("Nothing was committed. Review with `git status`.")
    print(f"Next: read {project / '.harness' / 'INIT.md'}, then open Claude Code here and run /kickoff.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
