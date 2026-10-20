# Core question bank for /kickoff

Ask ONE focused question at a time, in the author's language, with a recommended default when there is one.
Skip a question the author already answered. **Read before asking:** anything the repository, the installed tools or the
local server can tell you (versions, installed models, packages, existing config) is detected and only confirmed.
Each item says why it exists (lesson id in docs/lessons.md of the template).

Order: 1, 2, then the stack questions (`stack.md`), then 3 to 8. The gates depend on the stack answers.

## 1. Purpose and audience
- What is being built and for whom?
- How will you know it is done?
- Describe the **feel** you want in your own words: style, tone, what matters most to you (speed, simplicity,
  robustness, polish), references to other products. Add anything else that may seem minor but could affect
  architecture or implementation. Free text; Claude turns it into architecture notes in `docs/design.md`.
- Is the first milestone a minimal prototype or a usable first version?
- Is this project `production` or `learning`? (learning: the worker comments *why*, the reviewer explains corrections.)

## 2. Constraints
- Where will it run or be published?
- Is there a deadline?
- Language of the product?
- Language of the code comments?
- Accessibility requirements beyond the stack defaults?

## 3. Workers and machine
Detect first: `GET <url>/api/v0/models` lists the installed models and which one is loaded. Do not ask what it answers.
- Is a local server running (LM Studio, Bionic…) and on which port? Write it as `127.0.0.1:<port>`, not `localhost`. (L-026)
- From the installed models, which is the **preferred** one (the worker loads it whenever nothing is loaded)? Propose one from the list. (L-027)
- Which is the **secondary** one, used if the preferred cannot be loaded (for example not enough memory)? Optional. If another model is already loaded the worker uses it. (L-027)

Fixed, not asked: the ladder is 2 local attempts without thinking, 1 with thinking, then Claude Haiku, Claude Sonnet and
the main Claude session (L-024, L-025). The context length is the server's load setting and the output cap stays at the
template's `max_output_tokens` (L-003). Claude usage has no budget limit. Git workflow (branches, commits per task) is
proposed by Claude from the project, not asked.

## 4. Gates
- What is the command of the **fast** gate (compile, quick tests)?
- What is the command of the **full** gate?
- How long does each take, cold and warm? Run them once instead of asking, when they can run.
- Is a browser or other tool installed for visual checks, and which? Detect it first. (L-008)
- Formatter and line-ending conventions? Detect from config files first. (L-013)

## 5. Scope and protected data
- Which files are generated and must never be edited by hand? Name concrete examples from the project. (L-004)
- Which folders are untouchable?
- Which tool output folders must be git-ignored? (L-010)

## 6. Task budget
- Start with 3 files and ~15 spec lines per task; ask only if the author wants other limits. (L-003, L-006)

## 7. Code rules
- Conventions that tests should enforce?
- Which dependencies are allowed? Detect the ones already in the project first.
- Preferred architecture? Propose the stack's default (see `stack.md`) and let the author correct it.

## 8. Human verification and milestones
- What do you test by eye at the end of a milestone, and how (Editor, browser, console, device)? These steps become "how to test it".
