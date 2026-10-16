# Core question bank for /kickoff

Ask ONE focused question at a time, in the author's language, with a recommended default when there is one.
Skip a question the author already answered. Each item says why it exists (lesson id in docs/lessons.md of the template).

## 1. Purpose and audience
- What is being built, for whom, and how will you know it is done?
- Is this project `production` or `learning`? (learning: the worker comments *why*, the reviewer explains corrections.)

## 2. Constraints
- Where will it run or be published? Any deadline?
- Language of the product and of the code comments?
- Accessibility and **motion/animation policy** (respect or ignore OS reduced-motion)? (L-017)

## 3. Workers and machine
- Which local models can be served, with what context length and output-token cap? GPU memory?
- Which Claude models and subscription are available for escalation and review? (L-003, L-006)
- Is a local server running (LM Studio, Bionic…) and on which address and port? (write it as `127.0.0.1:<port>`, not `localhost`; L-026)
- Which local model is the **preferred** one and, optionally, which is the **secondary** one? The preferred model is the one the worker tries to load whenever no model is loaded; the secondary one is used if the preferred cannot be loaded (for example not enough memory). If another model is already loaded the worker uses it instead of loading a second one. (`model` and `fallback_model` in `harness.toml`; L-027)

## 4. Gates
- Commands for the **fast** gate (compile, quick tests) and the **full** gate. How long does each take?
- Is a browser or other tool installed for visual checks (and which)? (L-008)
- Line endings and formatter conventions? (L-013)

## 5. Scope and protected data
- Which files are generated and must never be edited by hand? Which folders are untouchable? (L-004)
- Which tool output folders must be git-ignored? (L-010)

## 6. Task budget
- Files per task and spec length for the chosen worker (start with 3 files / ~15 lines and calibrate). (L-003, L-006)

## 7. Numbers and code rules
- Which values must never be typed by hand (they come from data or config)?
- Conventions that tests should enforce? Allowed dependencies?

## 8. Human verification and milestones
- What do you test by eye, and how (Editor, browser, console, device)? These steps become "how to test it".
- Optional: maximum machine hours per session (milestones above it get split).
