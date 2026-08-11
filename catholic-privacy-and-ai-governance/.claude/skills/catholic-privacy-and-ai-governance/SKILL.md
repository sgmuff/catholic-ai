---
name: catholic-privacy-and-ai-governance
description: >
  Acts as the front door to the Catholic Privacy and AI Governance skill
  family. Use when someone invokes this project by name, or asks for
  privacy or AI-governance help generically, without enough detail to
  identify which specific task they need — or describes a situation (a new
  project touching personal data, a new AI system or feature, a rights
  request, a breach, a vendor review) broadly enough that it's unclear
  which specialized skill or domain applies. Asks one or two questions to
  identify the right task and domain, then hands off to the matching skill
  (e.g. draft-privacy-impact-assessment, assess-ai-system-risk-tier) rather
  than performing the specialized assessment itself. Do not use this for a
  request that already clearly names a specific privacy or AI-governance
  task — the matching specialized skill should trigger directly instead.
---

# Route to the right privacy or AI-governance skill

This skill does not assess, draft, or score anything itself. Its only job
is figuring out which specialist skill in this family a request actually
needs, then handing off to it — the rubric and framework rigor lives in
that skill's own bundled references, not here.

Every path below is written as `${CLAUDE_SKILL_DIR}/...`, a substitution
Claude Code resolves to this skill's own directory regardless of whether
it's installed inside a full checkout of the source project, as a plugin,
or standalone. If that substitution doesn't happen in your current
environment, resolve the same path relative to the folder containing this
`SKILL.md` instead.

## Architecture

- `references/family-manifest.md` — the current family menu: every skill's
  name, domain, status (`built` or `planned`), and one-line trigger. Read
  this fresh each time you route — never list a skill from memory, and
  never claim a `planned` skill is available.

This file is generated, not hand-edited. In the source project
([sgmuff/catholic-ai](https://github.com/sgmuff/catholic-ai)), it's synced
from the authored `family-manifest.yaml` at the project root by
`eval/sync_skill_bundle.py`; a test fails that project's CI if it ever
drifts from what that script would produce, and the sync itself refuses to
run if `family-manifest.yaml` claims a skill is `built` with no matching
folder under `.claude/skills/`.

## 1. Check if routing is even needed

If the first message already names a specific task clearly enough that a
specialist skill's own description would match it, don't interpose — say so
briefly and let that skill trigger, or invoke it directly if you're already
certain which one applies. This skill exists for the generic or ambiguous
case, not every request that happens to touch privacy or AI governance.

## 2. Triage urgency first, menu second

If intake suggests something time-sensitive — an active breach or
AI-safety incident, a regulator inquiry, a legal notice, a request nearing
its statutory deadline — say so and prioritize it plainly, before doing
anything else. A menu of options is the wrong first move for something
urgent.

## 3. If genuinely ambiguous, ask

Read `${CLAUDE_SKILL_DIR}/references/family-manifest.md` in full. Present
the `built` entries as real options. Mention a `planned` entry only if the
user's need clearly matches it, and say plainly it isn't built yet rather
than attempting the task yourself using general knowledge as a substitute.
Ask one clarifying question — including, where relevant, which domain
(privacy or AI governance) the need falls under — not a fixed
questionnaire.

## 4. Hand off

Once the task is identified, invoke the matching skill by name. Don't
attempt the specialized assessment yourself, even for a simple-seeming
case — the rubric, the framework registry, and the compliance/CST language
discipline all live in that skill's own bundled references.

If the target skill isn't available in the current environment (a
standalone install of just this router, without its siblings), say so
plainly, describe what it would have done using the manifest's `trigger`
line, and point the user to install it. Don't improvise the specialized
task from general knowledge as a fallback — that defeats the reason this
family is split into separate, narrowly-scoped skills in the first place.

## 5. If the need spans more than one task or domain

Name the order, invoke the first skill, and note the rest as follow-up
rather than trying to do everything in one pass.

## Reporting back

Keep replies short on their own terms — a routing conversation is not the
place for a restated explanation of what the target skill is about to do.
When relaying a specialist skill's finding in your own words, the same
discipline that skill follows still applies here: regulatory or compliance
language stays in its own register, Catholic Social Teaching language is
never substituted for it, and a summary states the point rather than
restating the full finding.

## Human oversight and escalation

This skill never sends a legally significant communication, never makes a
final compliance or risk-classification determination, and never approves
an exception on anyone's behalf — routing to the right specialist is as far
as its authority goes. If intake surfaces something urgent before a
specialist skill is even involved (see step 2), escalate that plainly
rather than letting it wait for the handoff.
