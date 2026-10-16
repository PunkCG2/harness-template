# Web questions for /kickoff

**Read before asking** (versions, tools, dependencies): package.json, lockfile, config files and installed browsers. Only confirm what is found; ask the rest.

- What kind of site: landing page, web app or content site? Is there a backend or external data?
- Plain HTML5/CSS/JS, or a framework (Vite + vanilla, React, Vue…)? (Only Vite + vanilla + Vitest is proven.)
- Test runner and build command? (becomes the fast / full gates)
- Browsers to support; is one installed for automated visual checks (Edge, Opera GX, Firefox needs Playwright's own build)?
- Responsive breakpoints and the widths to check; mobile layout: stacked, carousel, other?
- Motion policy: respect OS reduced-motion or always animate? (L-017)
- Languages (i18n) and where the dictionaries live; any text that must never be hard-coded?
- Where do texts and images come from, and who provides them?
- Design tokens (colours, fonts, spacing) in one file? Dark and light themes?
- SEO and performance target (for example a Lighthouse score)?
- Analytics: wanted or not? Which tool (Google Analytics, Plausible, other), which events to track, and is a consent banner needed?

## Default architecture
Plain modules, one concern per file, data and texts in separate files, no framework unless the author asks.
