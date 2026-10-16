# Web questions for /kickoff

**Read before asking** (versions, tools, dependencies): package.json, lockfile, config files and installed browsers. Only confirm what is found; ask the rest.

- Plain HTML5/CSS/JS, or a framework (Vite + vanilla, React, Vue…)? (Only Vite + vanilla + Vitest is proven.)
- Test runner and build command? (becomes the fast / full gates)
- Browsers to support; is one installed for automated visual checks (Edge, Opera GX, Firefox needs Playwright's own build)?
- Responsive breakpoints and the widths to check; mobile layout: stacked, carousel, other?
- Motion policy: respect OS reduced-motion or always animate? (L-017)
- Languages (i18n) and where the dictionaries live; any text that must never be hard-coded?
- Design tokens (colours, fonts, spacing) in one file? Dark and light themes?
