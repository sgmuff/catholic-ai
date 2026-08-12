---
description: Launch the Catholic Privacy and AI Governance menu — lists every built skill in the family and hands off to the one you pick.
argument-hint: "[optional: describe your situation]"
---

# Launch the privacy & AI-governance menu

Unlike the `catholic-privacy-and-ai-governance` skill — which only surfaces
a menu when it judges a request ambiguous, and asks a clarifying question
first — this command always shows the full menu immediately, every time
it's run. Don't skip the menu because `$ARGUMENTS` or the next message
already seems to name a task; show it regardless, then let the answer pick
the row.

1. Read `.claude/skills/catholic-privacy-and-ai-governance/references/family-manifest.md`
   in full, fresh, from this project's own checkout — never list a skill
   from memory, and never list an entry whose status isn't `built`.
2. Present every `built` entry as a single flat numbered list, grouped
   under two headings ("Privacy" and "AI governance") in the order the
   file lists them. Show each entry's name and its trigger line, not just
   the name.
3. If `$ARGUMENTS` was given, still show the full list, but note which
   entry (or entries) look closest to what was described.
4. Ask which one to run — by number or name — or to describe the
   situation in their own words if none fit.
5. Once it's picked, invoke that skill by name. Don't perform the
   specialized assessment yourself from this command.

If intake before or during this exchange reveals something time-sensitive —
an active breach, an AI-safety incident, a regulator inquiry, a deadline
close to expiring — say so and prioritize it above the menu, the same as
the router skill's own urgency-first step.

If a chosen skill isn't available in the current environment, say so
plainly, describe what it would have done using the manifest's `trigger`
line, and don't improvise the specialized task from general knowledge as a
substitute.
