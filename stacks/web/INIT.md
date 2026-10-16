# Start a web project

1. Create the project: `npm create vite@latest <name> -- --template vanilla` (or your framework), `npm install`.
2. `git init` in the project folder and make a first commit of the generated files.
3. `python <harness-template>\init.py --stack web --into <project>`; review with `git status`; commit the harness files.
4. Open Claude Code in the folder and run `/kickoff` (it will ask framework, gates, browser, motion policy…).
5. Run `/plan`; approve tasks and milestones; start with `/task next`.

## Verifying
- Gates: `npm test` (fast), `npm test` + `npm run build` (full).
- Visual checks: `npm run dev`, then check the widths in `[verify]` in a real browser; restart the dev server after
  switching branches. The first milestone's "how to test it" is "open the page and look".
