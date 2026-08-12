# catholic-privacy-and-ai-governance — build plan

This is a planning document, not a build. Nothing here is final — edit any section,
delete what you don't want, and this becomes the spec I build from once you say go.

**Naming note:** this project doesn't personify itself — no persona, no title,
no office-holder standing in for the skill family. Its name, and every skill's
own name, describes the task, not a role. Step 1 of the build sequence (§11) is
done: the directory has moved, and `README.md`, `CHECKLIST.md`, `Makefile`,
`pyproject.toml`, and an empty `src/privacy_and_ai_governance/` + `tests/`
skeleton exist. Nothing beyond that scaffold is built yet — step 2 onward is
still ahead.

Sources consulted: [agentskills.io](https://agentskills.io) (specification,
best-practices, and description-optimization pages), and this repo's own
[`docs/standards/skills.md`](../docs/standards/skills.md),
[`docs/standards/architecture.md`](../docs/standards/architecture.md), and
[`docs/standards/security-and-privacy.md`](../docs/standards/security-and-privacy.md).
This project is designed and built independently of every other project in this
repository — see §4. `jobduties.md` and `ai-gov-duties.md` (both in this
directory) are the source material for scope, one per domain.

---

## 1. Scope and shape

This project now covers two duty domains instead of one:

- **Privacy** — `jobduties.md`, eleven areas covering program management,
  regulatory monitoring, assessments, rights requests, incident response, vendor
  management, policy drafting, privacy-by-design, training, executive reporting,
  and administration.
- **AI governance** — `ai-gov-duties.md` (drafted alongside this plan, grounded in
  NIST AI RMF's four functions — Govern, Map, Measure, Manage — ISO/IEC 42001, and
  the EU AI Act's risk tiers), covering the parallel set: system inventory and
  risk classification, risk and impact assessments, model documentation, testing
  and monitoring, vendor AI governance, incident management, and the same
  regulatory-monitoring/policy/training/reporting/admin shape as the privacy side.
  This isn't a detour from repo convention — `docs/standards/architecture.md`
  already names exactly these three frameworks as the reference frameworks a
  project should map against; this is the first project here to build directly on
  top of that guidance rather than citing it in passing.

A Claude Skill is stateless and single-conversation: it activates, does one bounded
piece of work grounded in bundled reference material, and hands back a result. It
cannot maintain a live compliance calendar, poll regulatory feeds, send scheduled
reminders, or track ticket state across sessions — that's an application with a
datastore, not a skill. So each duty document splits the same way:

- **Judgment-and-drafting tasks** — given a described situation, assess it against
  a rubric or set of requirements and produce a structured, reviewable artifact
  (a PIA, a risk-tier classification, a model card, an incident triage note). This
  is bounded, judgment-based work that produces one artifact per run — exactly
  what a skill does well.
- **Program-administration tasks** — maintaining registers, monitoring external
  sources, tracking deadlines over time, sending notifications, reconciling
  records across systems. No skill in this repo does this today, and one skill
  built once wouldn't either. Out of scope for this endeavor as currently planned,
  in both domains.

**Recommendation, unchanged from the original plan:** build this as a *project*
housing a small **family of standalone skills** — now two sibling sub-families,
one per domain — plus a **router skill**, named after the project itself, as the
front door for a generic invocation ("use catholic-privacy-and-ai-governance," or
a generic request for privacy or AI-governance help). See §6 for the router and
§8 for both domains' skill tables.

---

## 2. Hard rules for every skill in this family

Two rules govern every skill in this family, permanently, across **both**
domains, and apply at all times — neither gets revisited or relaxed per-skill,
and neither is a style preference. They're folded together here as subsections
of one section, rather than each claiming its own top-level number, specifically
so a future rule like this slots in as §2.3 without forcing a renumber of
everything below it.

### 2.1 Catholic language is additive, never substitutive

**The compliance/regulatory content this family produces is never translated,
softened, reframed, or diluted into Catholic vocabulary. Catholic Social Teaching
language is layered alongside the compliance content, never used in place of it.**
Whatever a regulator, opposing counsel, or an auditor would need to see — the exact
term of art, the citation, the statutory verb — stays exactly as they'd expect to
find it, unedited by the theological framing sitting next to it. This applies
identically whether the "compliance content" is a GDPR finding or an EU AI Act
risk-tier determination — the AI-governance skills don't get a lighter version of
this rule just because the field is newer.

Why this is non-negotiable rather than a preference: the whole reason this family
is useful to an actual DPO, AI governance lead, general counsel, or compliance
team is that its output has to survive being read by someone who does not
share — and doesn't need to share — the theology underneath it. The moment a
report says "rightly ordered stewardship of information" where a regulator expects
"lawful basis," or "solidarity with the vulnerable" where an EU AI Act conformity
file expects "high-risk system," the artifact stops being usable as what it
actually is: a real compliance work product, not a devotional gloss on one.
`docs/standards/architecture.md` already states this relationship for the whole
repo — a project "argues from what the foundation implies... rather than from the
foundation itself" for a secular audience. This rule is that principle made
concrete and mechanical for a project where the cost of getting it wrong isn't a
bad essay, it's a document a lawyer can't cite.

### How this gets enforced, not just stated

A written instruction alone isn't reliable enough — instructions get deprioritized
in a long `SKILL.md`, or drift as skills get edited over time. So this is enforced
structurally — by the schema and a validator, not by hoping the model remembers
on every run:

- **Every report this family produces has two structurally separate parts**, never
  interleaved: a `compliance` (or `regulatory_findings`) section, written strictly
  in the regulatory register — the exact terms of art, citations (article/section
  or clause numbers), and statutory verbs (`must`, `shall`, `required`) the
  applicable framework itself uses — followed by a clearly separate
  `cst_reflection` section carrying the Catholic grounding (principle citations,
  magisterial sources, the dignity-of-the-person framing). A reader who wants only
  the compliance content can act on the first section in full without reading the
  second at all.
- **The compliance section is never paraphrased into CST vocabulary or softened in
  register.** It's authored the same way `CONTRIBUTING.md`'s citation-integrity
  rule already requires for this whole repo — quoted and cited accurately from the
  primary source, not reconstructed from what it "usually means."
  `frameworks/**/*.yaml` (§3) is the single authored place regulatory/standards
  language lives; skills read it and cite it, they don't re-word it into
  something else.
- **A validator blocklist.** The shared validator (`scripts/assessment.py` in each
  skill, backed by `src/privacy_and_ai_governance/` in the owning project) rejects an
  assessment if CST-only vocabulary — a maintained list starting with
  `personalism`, `solidarity`, `subsidiarity`, `common good`, `Magnifica
  Humanitas`, `imago dei`, `dignity of the human person` — appears inside the
  `compliance` field. This is the same validate-then-render split used everywhere
  in this family: the model does the judgment, the script catches the specific
  failure mode of language bleeding across the boundary.
- **Applies to every skill in the family, including the router** (§6) and every
  future specialist skill in either domain's table in §8 — it's part of what a
  skill in this family *is*, not a one-off requirement scoped to the flagship.
  It's a go-live item in `CHECKLIST.md`, alongside citation integrity, before any
  skill in this family ships.

**Amendment, added at build sequence step 20:** the rubric-scored shape
(`render_markdown` — `draft-privacy-impact-assessment`, `draft-privacy-notice-
update`, `assess-ai-system-risk-tier`, `draft-model-card`) now renders
`cst_reflection` *first*, right after the title, functioning as a Catholic
Social Teaching executive summary of what the assessment found — not last,
as originally described above and as every other shape (triage, incident,
review, retention, regulatory-change) still does. The two-structurally-
separate-parts rule this section states is about vocabulary, not reading
order: nothing here required compliance to render before the CST content,
only that the two never interleave or bleed into each other's register —
the blocklist enforces that regardless of which section comes first. The
"reader who wants only the compliance content can act on it without reading
past it" benefit this section originally described for reading order still
holds for the rubric-scored shape too, just inverted: the Compliance and
Rubric ratings sections that follow the CST summary are still exactly what
a DPO or AI-governance-lead reader needs, unchanged and unsoftened, whether
or not they read the section above them first.

This rule governs volume, not register: every artifact this family produces — a
rendered report, a rationale, a mitigation, a CST reflection, the router's own
conversational replies — is as long as the specific task actually requires and no
longer.

Why this matters as more than a style nicety: the audience for this family's
output is a professional — a DPO, general counsel, an AI governance lead — who
reads a lot of real compliance documents and can tell padding from substance
immediately. A twelve-page DPIA that buries three load-bearing findings in
restated context and boilerplate is worse than a tight one, and it actively works
against §2.1: a compliance section that isn't scannable in a few minutes stops
being usable by the person it's for. It's also the same discipline
agentskills.io's best-practice guidance already applies to a skill's own
instructions ("add what the agent lacks, omit what it knows"), moved up one
level to what the *generated report* tells its reader — don't restate what the
reader already supplied at intake, and don't re-explain a framework concept a
compliance-literate reader already knows.

**This is not permission to skip required coverage.** Every rubric dimension is
still scored, every applicable framework is still addressed, every mitigation
below threshold is still written — §2.2 never overrides what §7 (or a future
skill's own procedure) requires to be present. What gets cut is the padding
*around* each required element: a restated rubric description, a redundant
transition sentence, a boilerplate disclaimer repeated per-principle instead of
stated once. Completeness and concision are separate axes; this rule targets only
the second, and a future contributor should never read "be concise" as license to
drop something the rubric requires.

#### How this gets enforced

- **Field-level guidance, written once and shared across every skill's
  `SKILL.md`** (the same "write once, paste into each skill" pattern as the Human
  Escalation paragraph in §8): a rationale or mitigation states the specific fact
  that drove the finding and the specific fix, in one to three sentences — never
  restates the rubric criterion's own description back at the reader, never opens
  with a throat-clearing sentence before getting to the point.
- **A framework that doesn't apply gets one line** in the report ("Not
  applicable: `<the specific disqualifying fact>`"), not a full subsection
  explaining why at length.
- **A tighten-before-render pass**, added as a step between drafting the
  assessment JSON and rendering it: reread each field once and cut anything that
  repeats something already stated elsewhere in the same report — the same
  validate-then-fix discipline agentskills.io recommends for correctness,
  applied here to concision instead.
- **A non-fatal verbosity lint** in the shared validator, matching the freshness
  check's "nudge, not hard fail" pattern from §3: flags, without blocking, any
  field well past a generous length for what it is, or a total report length
  unusually long relative to how many dimensions and frameworks were actually in
  scope. A signal to reconsider before finalizing, not automatic truncation —
  auto-cutting a compliance document risks removing something genuinely needed,
  which is a worse failure than a slightly long one.
- **Applies to the router's own conversational replies too**, not only rendered
  reports: the urgency triage and the single clarifying question in §6.3 are
  meant to stay short; this rule is what makes that a standing constraint rather
  than an incidental choice.
- A go-live item in `CHECKLIST.md`, alongside §2.1's: a sampled report reads as
  tight, not merely correct.

---

## 3. Pluggable frameworks: how laws and standards get added or removed

This is the fix the original plan needed before more got built on top of it. As
drafted, the flagship skill named GDPR/CCPA/HIPAA/FERPA directly inside its own
`SKILL.md` — adding ISO/IEC 27701 or the NIST Privacy Framework later would have
meant hand-editing that file, and the same problem would repeat for every
AI-governance skill added against NIST AI RMF/ISO 42001/EU AI Act. The fix reuses
a pattern this plan already established for the router's own menu (§6.2):
a synced, tested manifest, never framework names hard-coded into skill prose.

### Structure

```
frameworks/
├── index.yaml                       # AUTHORED — the only file that has to change
│                                     #   to add or retire a framework anywhere
├── schema.yaml                      # the shape every framework file must conform to
├── privacy/
│   ├── gdpr-dpia.yaml
│   ├── ccpa-cpra.yaml
│   ├── hipaa.yaml
│   ├── ferpa.yaml
│   ├── iso-27701.yaml               # voluntary standard, not a law
│   └── nist-privacy-framework.yaml  # voluntary framework, not a law
├── ai-governance/
│   ├── eu-ai-act.yaml
│   ├── nist-ai-rmf.yaml
│   └── iso-42001.yaml
└── known-conflicts.md               # cross-framework tensions — see below
```

`index.yaml` is a flat registry, one entry per framework file:

```yaml
frameworks:
  - id: gdpr-dpia
    name: "GDPR Art. 35 — Data Protection Impact Assessment"
    type: law                # law | standard — see below
    domain: privacy          # privacy | ai-governance
    file: privacy/gdpr-dpia.yaml
    version: "2016/679, as amended"
    last_reviewed: 2026-08-11
    status: active           # active | retired
  - id: iso-27701
    name: "ISO/IEC 27701 — Privacy Information Management"
    type: standard
    domain: privacy
    file: privacy/iso-27701.yaml
    version: "2019"
    last_reviewed: 2026-08-11
    status: active
  - id: eu-ai-act
    name: "EU AI Act — Risk Tiers & Obligations"
    type: law
    domain: ai-governance
    file: ai-governance/eu-ai-act.yaml
    version: "2024/1689"
    last_reviewed: 2026-08-11
    status: active
```

### Why `type: law | standard` matters, not just bookkeeping

A law is binding and jurisdiction-triggered — the applicability question is "do
the facts (data handled, jurisdiction, sector) bring this into scope." A standard
like ISO/IEC 27701 or the NIST Privacy Framework is voluntary and conformance-
based — the applicability question is "does the institution want to be assessed
against this." These get asked differently in every skill's intake step, and per
§2.1 they get *written up* differently too: a law's finding uses regulatory verbs
(`must`, `shall`, `required`); a standard's finding uses conformance language
("satisfies," "partially satisfies," or "does not satisfy" clause X) — different
registers, but both still exact terms of art from the source, never CST
vocabulary.

### How a skill actually consumes this

Every specialist skill's `SKILL.md` reads generically — never naming a fixed
framework list — something like:

> Read `references/frameworks/index.md`. For every entry where `domain` matches
> this skill's domain and `status: active`: if `type: law`, ask or infer whether
> the triggering jurisdiction or facts apply; if `type: standard`, ask whether the
> user wants to be assessed against it. Then read the specific file(s) that apply
> in full before scoring — don't score from memory of what a framework "usually"
> requires.

Adding ISO/IEC 27701 becomes: author `privacy/iso-27701.yaml` against
`schema.yaml`, add one line to `index.yaml`, run the sync. No `SKILL.md` in either
domain needs to change. Retiring a framework is `status: retired` in `index.yaml`
— the file stays as an audit record, but the sync stops offering it, and a test
asserts every skill's bundled index reflects `status`, not just file presence.

This is also what makes the AI-governance domain a clean addition rather than a
second architecture: the AI-governance flagship skill planned in §8 consumes the
exact same `index.yaml`, filtered to `domain: ai-governance`. Same mechanism, new
data — nothing about the pattern changes to support a second domain.

### Freshness and cross-framework conflicts

- `last_reviewed` on every entry, checked by a `make check-framework-freshness`
  target that lists anything past a threshold (18 months is a reasonable
  default). This is a nudge for a periodic human review, not a hard CI failure —
  a framework not changing isn't itself an error, but it's worth eyeballing on a
  cadence rather than trusting a file indefinitely.
- `frameworks/known-conflicts.md` documents cases where two frameworks in the
  registry pull in different directions for the same fact pattern (a retention
  mandate under one regime against a minimization mandate under another; an EU AI
  Act transparency obligation against a trade-secret protection elsewhere) — same
  `contested: true`, route-to-a-person discipline `rubric/known-tensions.md`
  already gives CST-principle tensions. A skill that finds a genuine conflict
  flags it as a finding requiring human resolution, not something to silently
  average away.

---

## 4. What "standalone" means here, concretely

You asked that this not reference other projects in the repo, and that these
projects not relate to one another at all — not as a runtime dependency, not as a
design precedent, not as a comparison. Concretely, that means:

- No skill here reads, imports, or cites files from any other project in this
  repository, even where subject matter legitimately overlaps with something
  built elsewhere. If a skill here needs a specific legal citation (e.g. GDPR
  Art. 22), it's authored fresh, independently, inside this project's own
  `frameworks/` — never pointed at another project's copy of the same citation.
- Every skill's own directory never reaches outside itself at judgment or run
  time, per `docs/standards/skills.md` § "Distributing a skill outside this
  repo." Grounding content lives in this project's own authored source
  directories (`frameworks/`, `rubric/`) and gets synced into each skill's own
  `references/`.
- This applies to the *router* too, and it's the one place the constraint bites:
  the router's job is to point at its sibling skills, but if someone installs only
  the router (a standalone plugin install or a Claude.ai zip of just that one
  folder), those siblings may not be present. §6.3 covers the fallback.
- The project's README, when written, won't compare itself to or name any other
  project in the repo (matches your existing standing preference on this).

---

## 5. Project structure

Following `docs/standards/architecture.md`'s code-project layout, with the
skill-distribution mechanics from `docs/standards/skills.md`:

```
catholic-privacy-and-ai-governance/
├── README.md                          # filled from docs/project-template/README.template.md
├── Makefile                           # setup, test, lint, sync-skill-bundle, check-framework-freshness
├── pyproject.toml
├── CHECKLIST.md                       # go-live checklist, extended per §2 and this project's data-handling nature
├── jobduties.md                       # privacy duty source — kept as-is
├── ai-gov-duties.md                   # AI-governance duty source
├── family-manifest.yaml               # AUTHORED: which skills exist, one-line trigger, status, domain — see §6.2
├── frameworks/                        # AUTHORED: see §3 in full
│   ├── index.yaml
│   ├── schema.yaml
│   ├── known-conflicts.md
│   ├── privacy/
│   │   ├── gdpr-dpia.yaml
│   │   ├── ccpa-cpra.yaml
│   │   ├── hipaa.yaml
│   │   ├── ferpa.yaml
│   │   ├── iso-27701.yaml
│   │   └── nist-privacy-framework.yaml
│   └── ai-governance/
│       ├── eu-ai-act.yaml
│       ├── nist-ai-rmf.yaml
│       └── iso-42001.yaml
├── rubric/                            # AUTHORED: the privacy-by-design scoring rubric (v1 domain),
│   │                                   #   rubric-only by design — no bright-line gate, see §7.2
│   ├── criteria.md                    #   the dimensions scored (see §7) and how to score them
│   └── known-tensions.md              #   worked cases where two good privacy goods conflict
├── src/privacy_and_ai_governance/      # shared validation/report-rendering logic, stdlib-only —
│                                       #   includes the §2.1 compliance/CST-language boundary check,
│                                       #   the §2.2 verbosity lint, and the §3 framework-index consumer,
│                                       #   all shared by both domains
├── eval/
│   └── sync_skill_bundle.py           # generates every skill's references/ from frameworks/, rubric/,
│                                       #   and family-manifest.yaml
├── tests/                             # TDD: schema validation, rubric logic, sync-bundle drift,
│                                       #   manifest-accuracy, framework-index drift, the §2.1 language
│                                       #   test, and the §2.2 verbosity-lint test
└── .claude/skills/
    ├── catholic-privacy-and-ai-governance/  # the router — see §6
    │   ├── SKILL.md
    │   ├── .claude-plugin/plugin.json
    │   └── references/family-manifest.md
    ├── draft-privacy-impact-assessment/     # v1 flagship, privacy domain — see §7
    │   ├── SKILL.md
    │   ├── .claude-plugin/plugin.json
    │   ├── references/                       # synced: rubric/ + frameworks/ filtered to domain: privacy
    │   └── scripts/
    └── (later: assess-ai-system-risk-tier/, triage-privacy-rights-request/, ...)
```

`eval/sync_skill_bundle.py` generates every skill's `references/` (and
`scripts/`, where applicable) from this project's own authored source, including
`frameworks/index.yaml` (filtered per skill's domain) and `family-manifest.yaml`
(into the router) alongside `rubric/`. A test in `tests/`
regenerates every skill's bundle and asserts it matches what's committed, so CI
fails the moment someone edits `frameworks/`, `rubric/`, or `family-manifest.yaml`
without re-syncing.

In-repo (or in any full checkout), all family members sit as sibling folders under
`catholic-privacy-and-ai-governance/.claude/skills/` and Claude Code discovers them
together — the router always has its siblings available in that context. Register
each skill, including the router, as its own entry in the repo-root
`.claude-plugin/marketplace.json` — one marketplace, several plugins, so the
whole family is one `/plugin marketplace add` away, while each skill stays
independently installable per the spec.

---

## 6. The router skill: `catholic-privacy-and-ai-governance`

Named identically to the project itself: project name → skill folder name →
skill `name` field, all identical. That's deliberate: it's what makes "use
catholic-privacy-and-ai-governance" resolve to
something real by name, not just by description-matching. Its description
triggers on the task — a generic request for privacy or AI-governance help —
not on a persona: this project doesn't present itself as a person holding an
office, so nothing in its trigger language should either.

### 6.1 Frontmatter (draft)

```yaml
---
name: catholic-privacy-and-ai-governance
description: >
  Acts as the front door to the Catholic Privacy and AI Governance skill family.
  Use when someone invokes this project by name, or asks for privacy or
  AI-governance help generically, without enough detail to identify which
  specific task they need — or describes a situation (a new project touching
  personal data, a new AI system or feature, a rights request, a breach, a
  vendor review) broadly enough that it's unclear which specialized skill or
  domain applies. Asks one or two questions to identify the right task and
  domain, then hands off to the matching skill (e.g.
  draft-privacy-impact-assessment, assess-ai-system-risk-tier) rather than
  performing the specialized assessment itself. Do not use this for a request
  that already clearly names a specific privacy or AI-governance task — the
  matching specialized skill should trigger directly instead.
---
```

The last sentence matters as much as the rest: without it, the router risks
false-triggering ahead of a specialist skill even when the user's first message is
already specific enough (agentskills.io's description-optimization guidance calls
this out directly — a should-not-trigger case is only a useful test when it's a
near-miss, and a router that eats every request is exactly that kind of near-miss
risk for its own siblings).

### 6.2 The manifest, so the menu can't drift

`family-manifest.yaml` at the project root is the authored source of truth, now
carrying a `domain` field so the router can also disambiguate *which half* of the
family a vague request belongs to:

```yaml
skills:
  - name: draft-privacy-impact-assessment
    domain: privacy
    status: built
    trigger: "starting something new that will collect or process personal data"
  - name: assess-ai-system-risk-tier
    domain: ai-governance
    status: planned
    trigger: "deploying, building, or procuring a new AI system or feature"
  - name: triage-privacy-rights-request
    domain: privacy
    status: planned
    trigger: "an access, deletion, correction, or portability request came in"
  # ... one entry per row in either table in §8
```

`eval/sync_skill_bundle.py` renders this into the router's own
`references/family-manifest.md`, and a test asserts every `status: built` entry has
a matching folder under `.claude/skills/` — so the router's menu is generated, not
maintained by memory, and CI catches the day someone builds a new skill and forgets
to flip its status.

### 6.3 Procedure

1. **Check if routing is even needed.** If the first message already names a
   specific task clearly enough that a specialist skill's own description would
   match it, don't interpose — say so briefly and let that skill trigger (or invoke
   it directly if you're already certain which one applies).
2. **Triage urgency first, menu second.** If intake suggests something
   time-sensitive — an active breach or AI-safety incident, a regulator inquiry, a
   legal notice, a request nearing its statutory deadline — say so and prioritize
   it plainly, rather than treating it as a routine menu selection.
3. **If genuinely ambiguous**, read `references/family-manifest.md`, present the
   `built` entries as options (mention a `planned` one only if the user's need
   clearly matches it, and say plainly it isn't built yet rather than attempting it
   yourself), and ask one clarifying question — including, where relevant, which
   domain the need falls under.
4. **Hand off.** Once the task is identified, invoke the matching skill by name
   rather than attempting the specialized task yourself — the rubric/framework
   rigor lives in that skill's own bundled references, not in the router's head.
   If the target skill isn't available in the current environment (the standalone-
   install edge case from §4), say so plainly, name what it would have done from
   the manifest's `trigger` line, and point the user to install it — don't improvise
   the task from general knowledge as a substitute.
5. **If the need spans multiple duty areas or both domains** (e.g. a new feature
   that's both an AI system and a new personal-data processing activity), name the
   order, invoke the first, and note the rest as follow-up rather than trying to
   do both in one pass.

The same standing "Human Escalation & Control" paragraph referenced in §8 belongs
in the router's `SKILL.md` too — it may be the first point of contact for something
urgent, and should flag that immediately rather than only after a specialist skill
gets involved. It also carries §2.1's discipline whenever it relays a specialist
skill's finding in its own words: it doesn't get to loosen the compliance/CST
boundary just because it's summarizing rather than drafting. And per §2.2, its
own replies stay short on their own terms — a routing conversation is not the
place for a restated explanation of what the target skill is about to do.

---

## 7. The v1 flagship skill: `draft-privacy-impact-assessment`

Chosen as the first specialist skill to build because it produces one bounded,
structured advisory finding per run, it maps to a real legal requirement in
multiple jurisdictions (so it's judgeable,
not vague), and it covers the *Privacy Assessments & Data Governance* section of
`jobduties.md`, which is arguably the highest-value single duty area — most other
privacy work (rights requests, vendor review, incident response) ultimately gets
measured against whether the underlying processing was properly assessed in the
first place. It's also the router's only real target until a second skill lands
(see §11's build sequence for why the router is still worth building at that
point) — and it's the skill that proves out §3's pluggable-framework mechanism
before the AI-governance domain reuses it.

### 7.1 Frontmatter (draft, tune per §"Description quality" in `docs/standards/skills.md`)

```yaml
---
name: draft-privacy-impact-assessment
description: >
  Drafts a structured Data Protection/Privacy Impact Assessment (DPIA/PIA) for a
  described data-processing activity, new project, product, vendor relationship, or
  AI/technology use. Identifies which frameworks apply from the current registry
  (GDPR Art. 35, CCPA/CPRA, HIPAA, FERPA, or a voluntary standard like ISO/IEC
  27701, plus whatever else is registered), scores the activity against a
  privacy-by-design rubric — necessity and proportionality, data minimization,
  lawful basis and consent, retention, security controls, third-party sharing, and
  human oversight of automated decisions. Produces a report that requires DPO
  or legal review before being relied on. Use when someone is starting
  something that will collect or
  process personal data and wants the privacy risk assessed, or asks for a
  PIA/DPIA/privacy impact assessment by name.
---
```

### 7.2 Procedure

1. **Intake the processing activity.** Ask what's being built or changed, what
   personal data it collects or touches, who it's about, the purpose, which systems
   are involved, who receives the data (internal teams, vendors, other
   institutions), where it's stored, and how long it's kept. Stop asking once
   there's enough to reason about every rubric dimension — not a fixed
   questionnaire run to exhaustion.
2. **Identify applicable frameworks — generically, per §3.** Read
   `references/frameworks/index.md`, filtered to `domain: privacy` entries. For
   each `type: law` entry, ask or infer whether the triggering jurisdiction/facts
   apply (a diocese handling EU parishioner data → GDPR; a US Catholic hospital →
   HIPAA; a university housing or enrollment system → FERPA; a business serving
   California residents → CCPA/CPRA). For each `type: standard` entry, ask whether
   the user wants to be assessed against it. Read the matching file(s) in full
   before scoring — don't score from memory of what a framework "usually" requires,
   and never hard-code a framework name into this procedure itself.
3. **Score the rubric.** Read `references/rubric/criteria.md` in full and score
   each dimension: a real rationale grounded in what the activity actually does, a
   concrete mitigation for anything below the passing threshold, an `ideal` beyond
   the floor, and a `contested` flag for genuine value tensions (e.g. minimization
   vs. fraud-prevention retention, or a cross-framework conflict from
   `frameworks/known-conflicts.md`) rather than averaging them away. This skill is
   rubric-only, deliberately — no bright-line gate that short-circuits scoring for
   a fixed list of disqualifying uses. Every activity gets scored on its own facts.
4. **Write the assessment and render the report**, via
   `scripts/assessment.py --input <json> --out-dir <reports-dir>`: the model does
   the judgment, the script only checks the judgment is internally consistent (real
   framework ids drawn from the current index, no missing mitigation below
   threshold, retention field non-empty) **and enforces §2.1**: the `compliance`
   field holds the regulatory findings in regulatory register only, the
   `cst_reflection` field holds the Catholic grounding separately, and the script
   rejects the assessment if CST vocabulary has leaked into `compliance`. Before
   rendering, run the §2.2 tighten-before-render pass and the verbosity lint — cut
   anything restated, flag anything unusually long for a reviewer to double-check.
   Then it renders Markdown with the two sections clearly separated, compliance
   first.
5. **Report back in plain language, briefly**: this is an advisory draft grounded
   in a working interpretation of the named frameworks, not a legal opinion, and
   requires DPO or legal review before the underlying activity proceeds — matching
   `jobduties.md`'s own instruction to "route material risks for human review."
   Per §2.2, this summary states the verdict and what's weakest, not a restatement
   of the full report. Flag anything that met a high-risk threshold
   (special-category data, children's data, large-scale profiling, automated
   decisions with legal or similarly significant effect) as needing escalation
   before proceeding, not just noted in the report.

### 7.3 Grounding

- **CST:** personalism and the dignity of the human person as the ground for
  informational self-determination — a person's data is an extension of the
  person, not a resource to be optimized; subsidiarity, applied concretely as
  keeping data-handling decisions and consent as close as possible to the person
  concerned; solidarity, protecting those least able to contest how their data is
  used. *Magnifica Humanitas*'s claim about the primacy of human judgment over
  automated determination — already load-bearing in
  `docs/standards/security-and-privacy.md`'s "human oversight of consequential
  decisions" requirement — grounds the automated-decision dimension of the rubric
  directly, and will do the same double duty for the AI-governance domain's own
  human-oversight requirements.
- **Secular frameworks:** whatever is `active` and `domain: privacy` in
  `frameworks/index.yaml` — GDPR Art. 35, CCPA/CPRA, HIPAA, FERPA, ISO/IEC 27701,
  and the NIST Privacy Framework to start (§3). Extend the registry as real use
  surfaces more, rather than front-loading every framework that might someday be
  relevant.
- Note the direction of travel required by §2.1: the rubric dimensions above
  (minimization, lawful basis, retention, security, third-party sharing, human
  oversight) are themselves already the regulatory terms of art, on purpose. CST
  grounding explains *why* each dimension matters and sits in the `cst_reflection`
  section; it is never what the `compliance` section is scored or written in.

---

## 8. The rest of the family — both domains, for later

Each row is a candidate specialist skill, same architecture as §7
(rubric/framework-grounded via §3's registry, schema-validated, report-rendering,
and bound by §2's hard rules the same way), and a future entry in
the router's `family-manifest.yaml`. None of these are built in v1; listing them
here so both duty documents' full scope has a landing spot and nothing gets lost.

### Privacy domain — from `jobduties.md`

| Skill name | `jobduties.md` section | What it does |
|---|---|---|
| `triage-privacy-rights-request` | Privacy Rights Requests | Classifies an incoming DSAR by type/jurisdiction, calculates the statutory deadline, and drafts an intake record plus a checklist of missing information or identity-verification gaps. |
| `triage-privacy-incident` | Privacy Incident Management | Intakes a reported incident, runs a preliminary impact assessment against defined severity criteria, flags applicable notification triggers (which jurisdictions/contracts require notice and by when), and states plainly whether it meets the threshold for escalation. |
| `review-vendor-privacy-assessment` | Third-Party Privacy Management | Reviews a vendor's privacy questionnaire/DPA/certifications against a baseline requirement set and flags missing documentation or control gaps. |
| `review-data-retention-entry` | Privacy Assessments & Data Governance | Checks one data-inventory entry against the retention baseline and flags whether it needs deletion, review, or an updated retention justification. |
| `map-regulatory-change` | Regulatory Monitoring | Given a regulatory development pasted in by the user (this project doesn't monitor feeds itself), summarizes it and maps which existing policies/controls it likely affects. |
| `draft-privacy-notice-update` | Policy & Documentation Management | Drafts a proposed revision to a privacy notice or policy section given a stated change in practice, checked against the same rubric as §7. |

### AI-governance domain — from `ai-gov-duties.md`

| Skill name | `ai-gov-duties.md` section | What it does |
|---|---|---|
| `assess-ai-system-risk-tier` | AI System Inventory & Risk Classification | The AI-governance flagship, recommended as the first skill built once the privacy flagship proves out §3: classifies a described AI system against the EU AI Act's risk tiers, maps it to NIST AI RMF's Govern/Map/Measure/Manage functions, and flags which obligations attach — same shape as §7, different registry filter. |
| ~~`draft-ai-risk-impact-assessment`~~ | AI Risk & Impact Assessments | **Retired at step 17, never built.** As originally described this would duplicate `assess-ai-system-risk-tier`, which already produces a full seven-dimension rubric-scored assessment (bias/fairness, robustness, human-oversight, etc.) against the same registry — not the narrower classification-only tool this row assumed. See step 17's write-up. |
| `draft-model-card` | Model & System Documentation | Produces a model/system documentation record grounded in ISO/IEC 42001's documented-information requirements and the EU AI Act's Annex IV technical documentation — name matches the example already given in `docs/standards/skills.md`. |
| `review-ai-vendor-governance` | Third-Party & Vendor AI Governance | Reviews a vendor's or foundation-model provider's AI governance documentation against a baseline requirement set and flags missing documentation or control gaps. |
| `triage-ai-incident` | AI Incident Management | Intakes a reported AI safety, bias, or reliability incident, runs a preliminary impact assessment, and flags applicable notification thresholds — the AI-governance sibling of `triage-privacy-incident`. |
| `map-ai-regulatory-change` | Regulatory & Standards Monitoring | Given an AI-specific regulatory or standards development pasted in by the user, summarizes it and maps which existing AI governance controls or policies it likely affects — the AI-governance sibling of `map-regulatory-change`. |
| `review-ai-system-reassessment` | Testing, Validation & Performance Monitoring | Checks one inventoried AI system against its defined re-evaluation interval and flags whether it's overdue for reassessment, due for documentation update, or current — the AI-governance analog to `review-data-retention-entry`. |

**Correction, added at build sequence step 16:** the two rows above were
missing from this table since the original build plan, even though both
duties are directly stated in `ai-gov-duties.md` — "Regulatory & Standards
Monitoring" is a near-mirror of `jobduties.md`'s "Regulatory Monitoring"
section, and "Testing, Validation & Performance Monitoring"'s "Identify
systems overdue for re-evaluation given their risk tier and the interval
defined for it" is the AI-governance analog of a retention check, even
though it isn't phrased in retention terms. Found by rereading
`ai-gov-duties.md` directly rather than trusting an earlier summary of it
— the same discipline this project asks of every citation, applied to its
own planning document. `review-ai-system-reassessment`'s grounding is
looser than `map-ai-regulatory-change`'s (a real paraphrase, not a
near-identical section), so treat its exact shape as less settled until
it's actually designed.

**Status as of step 18: every row above is built.** `draft-ai-risk-
impact-assessment` is the sole exception, retired rather than built (step
17). Both backlog tables — every skill from both duty documents that this
project judged actually fits a stateless skill (see §1 and the "not
planned" note below) — are now complete.

Explicitly **not planned** as skills, in either domain, because they're
program-administration work a stateless skill can't do (see §1): the compliance
calendar, recurring-task scheduling, training-completion tracking, sending
notifications, and reconciling records across systems from *Administrative &
Operational Tasks*, *Training & Awareness*, and *Reporting & Executive Support* in
both duty documents. If any of these become worth solving later, it'd be as an
actual application (a CLI + a datastore, in this repo's usual Python-project
shape) that a skill could optionally sit in front of — not as a skill by itself.

*Human Escalation & Control* (the last section of both duty documents) isn't a
skill at all in either domain — it's a standing behavioral contract that belongs
in every skill in this family, including the router (see §6.3): never send a
legally significant communication, never make a final compliance or
risk-classification determination, always require human approval for exceptions,
and always document rationale and disposition for material decisions. Recommend
writing this once as a short shared paragraph and pasting it into each skill's
`SKILL.md` as its standing disclosure — and note that this paragraph, too, is
compliance-critical language under §2.1: it stays in precise
regulatory/procedural register, not folded into CST phrasing — and under §2.2,
it stays a paragraph, not a page.

---

## 9. Testing & CI

Following `docs/standards/architecture.md` and `docs/standards/python.md`:

- TDD throughout: schema validation, rubric-scoring logic, framework-file parsing,
  the sync-bundle drift check, and both §2 checks are all written test-first.
- `tests/test_skill_bundle_sync.py` regenerates every skill's `references/`
  (and `scripts/`, where applicable) from
  `frameworks/`, `rubric/`, `family-manifest.yaml`, and `src/`, and asserts no
  drift — including the check from §6.2 that every `built` manifest entry has a
  real skill folder, and the check from §3 that every skill's bundled framework
  index matches `frameworks/index.yaml` filtered to that skill's own domain.
- `tests/test_language.py` and `tests/test_assessment.py`'s
  `TestValidateAssessmentComplianceBoundary` (backing §2.1): feed the
  validator a clean assessment and a deliberately-poisoned one (CST
  vocabulary injected into `compliance`) and assert the second is rejected.
- `tests/test_concision.py` (backing §2.2): asserts the verbosity lint fires
  on a deliberately padded assessment (restated rubric text, a repeated
  disclaimer) and stays quiet on a tight one.
- `make check-framework-freshness` (backing §3, via
  `tests/test_frameworks.py`'s `TestStaleFrameworks` and
  `eval/check_framework_freshness.py`): non-fatal report of any framework
  entry whose `last_reviewed` exceeds the staleness threshold — a
  periodic-review nudge, run manually or on a schedule, not a
  merge-blocking check.
- `agentskills validate ./.claude/skills/<name>` (the CLI the `skills-ref`
  package installs — see step 6) for every skill in the family before
  merge, and picked up automatically by `.github/workflows/ci.yml`.
- `Makefile` exposes `setup`, `test`, `lint` so CI picks the project up with no
  special-casing, per `docs/standards/architecture.md`.

---

## 10. Security & privacy notes (for the eventual README)

This project's own conduct has to model exactly what it prescribes — the standard
already states this explicitly for anything with this project's profile
("a governance project that is careless with data protection in its own
recommendations has no standing to prescribe it to anyone else"). The
AI-governance domain doesn't get a lighter version of this: a project telling
institutions to govern their AI systems responsibly has to be equally careful
about how it documents and reasons about the (fabricated, per below) AI systems in
its own examples and tests.

- **Test fixtures:** every example processing activity, DSAR, incident, or AI
  system described in tests or documentation is fabricated — no real person's data
  and no real institution's actual deployed system, ever, per
  `docs/standards/security-and-privacy.md`. Worth being extra careful here given
  the subject matter is literally personal-data and AI-system governance.
- **Data minimization / lawful basis / retention / human oversight:** the privacy
  domain's own work product (§7) exists specifically to make institutions address
  these four things for *their* processing — the README should say so and point at
  §7 rather than restate it. The AI-governance domain's human-oversight
  requirement is the same claim applied to automated decisions specifically — see
  §7.3's note on `Magnifica Humanitas` doing double duty across both domains.
- **Compliance-language integrity:** see §2. This is also a README-worthy point —
  it's the specific thing that lets this project's output be handed to a lawyer,
  regulator, or auditor as-is, not just a design detail buried in this plan.
- **No secrets, dependencies pinned, CI least-privilege:** same baseline as every
  other project in this repo.

---

## 11. Build sequence

1. ~~**Rename the directory** and scaffold per §5~~ — **done.** The directory
   moved (carrying `jobduties.md`, `ai-gov-duties.md`, and this plan file with
   it), and `README.md`, `CHECKLIST.md`, `Makefile`, `pyproject.toml`, and an
   empty `src/privacy_and_ai_governance/` + `tests/` skeleton are in place, matching
   `docs/project-template/python-starter/`.
2. ~~**Author `frameworks/schema.yaml` and `frameworks/index.yaml`** with a
   single entry~~ — **done.** `frameworks/schema.yaml` (the shape every
   framework file must validate against), `frameworks/index.yaml` (one entry:
   `gdpr-dpia`), and `frameworks/privacy/gdpr-dpia.yaml` (the authored
   content — GDPR Art. 35's trigger, ten required elements, nine terms of
   art, each with a citation) are in place. Content is verified against a
   secondary source but marked `review_status: unreviewed` — it still needs a
   real GDPR-competent legal check before this skill ships (§ Testing & CI,
   CHECKLIST.md's citation item). The rest of the registry (CCPA/CPRA, HIPAA,
   FERPA, ISO/IEC 27701, NIST Privacy Framework) waits for step 7.
3. ~~**Author `rubric/criteria.md`**~~ — **done.** Seven framework-agnostic
   dimensions (necessity-and-proportionality, data-minimization,
   lawful-basis-and-consent, retention, security-controls,
   third-party-sharing, human-oversight), each with a 5/3/1 scoring anchor, a
   CST rationale, and mitigation/`ideal` guidance stated once in the shared
   scoring instructions rather than repeated per dimension. Rubric-only, no
   bright-line gate. `rubric/known-tensions.md` stays a forward reference
   until a real contested case surfaces one worth recording.
4. ~~**Write `src/privacy_and_ai_governance/` validation + rendering logic,
   test-first**~~ — **done.** Six modules, 66 tests, 97% coverage, clean
   under `ruff` and `mypy --strict`: `frameworks.py` (§3 — loads and
   validates the registry against `schema.yaml`, a small stdlib-only
   JSON-Schema-subset validator, no `jsonschema` dependency), `rubric.py`
   (reads dimension ids and the passing threshold straight out of
   `rubric/criteria.md` rather than duplicating them as a Python constant),
   `language.py` (§2.1 — the CST-vocabulary blocklist check),
   `concision.py` (§2.2 — the non-fatal verbosity lint, thresholds scaled by
   how many frameworks/dimensions are actually in scope), `assessment.py`
   (ties the above together to validate a full DPIA assessment JSON — real
   framework ids, complete rubric coverage, mitigation required below
   threshold, the compliance/CST boundary enforced), and `report.py`
   (renders Markdown with compliance before the CST reflection, per §2.1).
   Needed a Python 3.12 interpreter found separately from the machine's
   default `python3` (3.9) — `README.md`'s Setup section now says so.
5. ~~**Write `eval/sync_skill_bundle.py` and the drift test**~~ — **done.**
   A real sequencing wrinkle surfaced here: the plan's design has
   `family-manifest.yaml` (step 9) as the source of which skill has which
   domain, but a single skill needs syncing as soon as it exists (step 6) —
   before the manifest does. Resolved with two entry points rather than one:
   `sync_skill_references(skill_dir, domain, ...)` syncs one skill directly
   given its domain explicitly (what step 6 uses), and `sync_all(...)` reads
   `family-manifest.yaml` and bulk-syncs every `status: built` entry plus the
   router (what step 9 onward, and CI, use) — tested now against synthetic
   fixtures rather than waiting on the manifest to exist for real. Both are
   proven against the real `frameworks/` and `rubric/` content, not just
   fixtures. 11 more tests (77 total), still 97% coverage, clean under
   `ruff` and `mypy --strict`. `make sync-skill-bundle` now runs it; run
   against the real project today, it correctly does nothing (no manifest
   yet). Added a `py.typed` marker to the package so `eval/`'s own imports
   from `src/` type-check too, even though `make lint` only enforces
   `mypy src` per the repo standard.
6. ~~**Write `.claude/skills/draft-privacy-impact-assessment/SKILL.md`, run
   the sync, validate**~~ — **done.** A second real constraint surfaced
   here, on top of step 5's sequencing one: `docs/standards/skills.md`
   requires a skill's own `scripts/` to be dependency-free stdlib-only, but
   `src/`'s modules use PyYAML for everything that touches the framework
   registry. Resolved by checking which src/ modules actually need PyYAML —
   only `frameworks.py` (and `assessment.py`, which imports it) — so
   `sync_skill_bundle.py` now also copies `concision.py`, `language.py`,
   `report.py`, and `rubric.py` byte-for-byte into a skill's `scripts/`
   (they were already stdlib-only) and writes a new
   `references/frameworks/index.json` (machine-readable, stdlib `json`-
   loadable) alongside the existing Markdown index. Only `scripts/
   assessment.py` needed a genuinely separate implementation, hand-authored
   directly in the skill (not synced, since nothing upstream renders it) —
   it reads that JSON instead of parsing YAML, and is otherwise the same
   validation logic as `src/assessment.py`.

   Proved this actually works, not just in theory: ran the skill's own
   `scripts/assessment.py` against a fabricated parish bulletin sign-up
   scenario using a bare `python3.12` interpreter with no packages
   installed at all (not the project's own venv) — full DPIA report
   rendered correctly, compliance section before the CST reflection, both
   failure paths (empty `retention`, CST vocabulary leaked into
   `compliance`) rejected with every problem listed at once. Added an
   automated static check (`tests/test_flagship_skill.py`) that parses every
   file in `scripts/` with `ast` and asserts no import falls outside the
   standard library or a sibling script — so "dependency-free" is a tested
   property of this skill, not a claim about it. 90 tests total, still 97%
   coverage.

   `skills-ref` (the PyPI package name) installs a CLI called `agentskills`,
   not `skills-ref` — `docs/standards/skills.md`'s own command name is the
   package, not the binary. `agentskills validate
   .claude/skills/draft-privacy-impact-assessment` passes. Added `skills-ref`
   to this project's own dev dependencies so `make setup` provides it going
   forward, for this skill and every one after it.
7. ~~**Add the remaining privacy frameworks**~~ — **done.** Four laws
   (CCPA/CPRA, HIPAA, FERPA) plus GDPR already registered, and two voluntary
   standards (ISO/IEC 27701, the NIST Privacy Framework), six total. Each
   citation verified against a primary or authoritative secondary source
   before writing it down — Cornell LII for HIPAA and FERPA's CFR text
   (HHS.gov and eCFR both blocked the fetch), the CA AG's site plus general
   knowledge for CCPA/CPRA's statutory sections, NIST's own published Core.
   ISO/IEC 27701 is the one real exception: it's a paywalled commercial
   standard, not a public legal text, so that file carries a stronger
   caveat than this project's usual "unreviewed" status — its clause
   citations are indicative, authored from the standard's well-documented
   public structure, not a fetch of the purchased text, and it says so
   directly in the file.

   Confirmed the pluggability claim in §3 is real, not aspirational: each
   framework was added to `frameworks/index.yaml` and re-synced
   individually, and `SKILL.md` never needed a single edit across all five
   additions — only `references/frameworks/` grew. Proved the flagship
   skill actually reasons correctly over the larger registry, not just that
   the files exist: ran `scripts/assessment.py` with the bare
   dependency-free interpreter again, this time on a fabricated hospital
   patient-portal scenario citing HIPAA and explicitly recording GDPR as
   *considered but inapplicable* — exactly the `frameworks_considered`
   discipline §7.2 step 2 requires. Found and fixed two tests that had
   quietly hardcoded "exactly one framework" from step 2's original state;
   both now assert against the registry by id rather than by count, so they
   won't need touching again as the registry keeps growing. 91 tests, still
   97% coverage, clean under `ruff`, `mypy --strict`, and `agentskills
   validate`.
8. ~~**Dry-run the flagship skill on fabricated scenarios and refine from
   what goes wrong**~~ — **done.** Ran all three planned scenarios for real —
   fabricated intake, real applicability reasoning, all seven dimensions
   scored, assessment JSON validated and rendered with the bare
   dependency-free interpreter each time — not just structurally exercised.

   One scenario each did a different job. The biometric dormitory-access
   scenario surfaced a genuine rubric gap: `human-oversight`'s wording
   assumed a *pre-decision* review point ("before that decision is acted
   on"), which fits a scored recommendation but not a real-time system
   where the decision and the action are the same instant — a biometric
   lock either opens or doesn't. Scoring it required stretching the
   dimension rather than applying it directly, so `rubric/criteria.md` §7
   now explicitly covers both shapes: a pre-action review where that's
   possible, or a genuinely reachable human fallback immediately after for
   a real-time system — with the 5/3/1 anchors updated to match. Re-synced
   and re-rendered the same scenario against the updated wording to confirm
   nothing broke. The parish-bulletin scenario (deliberately low-risk, and
   testing whether the skill correctly reasons about CCPA's nonprofit
   exclusion under Civ. Code 1798.140(d)) surfaced no gaps — a useful
   negative result: the skill doesn't invent problems where a well-run,
   already-compliant activity doesn't have any, and produces an
   appropriately short report when nothing applies. The hospital
   scheduling/AI-triage scenario stress-tested a sub-processor chain and
   the CCPA/HIPAA PHI exemption (Civ. Code 1798.145(c)) and found the
   existing rubric wording already handled it well — no change needed
   there.

   All three reports read clean by eye against both hard rules: no CST
   vocabulary drift into `compliance` in any of them, and no field ran long
   enough to trip the concision lint — a signal the §2.2 thresholds are
   calibrated reasonably, not just theoretically. 91 tests still pass, 97%
   coverage, clean under `ruff`, `mypy --strict`, and `agentskills
   validate` after the rubric change.
9. ~~**Write `family-manifest.yaml`, build the router skill, test
   routing**~~ — **mostly done, one honest gap.** `family-manifest.yaml`
   has all twelve skills from §8's tables: `draft-privacy-impact-assessment`
   `built`, the other eleven `planned`. The router skill
   (`.claude/skills/catholic-privacy-and-ai-governance/`) is built per §6 —
   frontmatter, `.claude-plugin/plugin.json`, and a `SKILL.md` under the
   repo's 500-line size discipline. Ran `sync_all` against the real project
   for the first time (it only existed against synthetic fixtures before,
   since the manifest didn't exist yet) — it synced the router's
   `references/family-manifest.md` and re-synced the flagship in one pass,
   with no `ManifestDriftError`. `agentskills validate` passes on both
   skills. 100 tests, 97% coverage, clean under `ruff` and `mypy --strict`.

   The gap: "test that a bare invocation routes correctly and an
   already-specific DPIA request skips the router" is a property of a live
   agent reading the description and deciding whether to invoke the Skill
   tool — not something a unit test can mechanically prove, and not
   something checkable in *this* session either, since a newly-created
   skill isn't picked up until a fresh scan (the same reason `cst-finding`
   was only ever available here because it was indexed at this session's
   start, before any of this build's own edits). What's actually
   achievable now: the description follows agentskills.io's
   description-optimization guidance directly (imperative "use when," and
   the explicit "do not use this for a request that already clearly names
   a specific task" near-miss guard), and `tests/test_router_skill.py`
   asserts that guard clause is actually present in the shipped
   frontmatter, not just in this plan's draft. Real triggering behavior
   needs a fresh Claude Code session pointed at this project — try, once
   one's available: "use catholic-privacy-and-ai-governance" or "I need
   help with privacy" (should route), "draft a DPIA for a new email
   sign-up form" (should skip straight to the flagship), and something
   unrelated (should trigger neither).
10. ~~**Register both skills, work through `CHECKLIST.md`, flip status**~~ —
    **done, with one deliberate deviation from the literal instruction.**
    Both skills are registered in the repo-root `.claude-plugin/marketplace.json`
    alongside the existing `cst-finding` entry. Working through
    `CHECKLIST.md` honestly surfaced two real gaps that got fixed rather
    than glossed over:
    - `make check-framework-freshness` was specified back in §3 but never
      actually built — implemented now (`stale_frameworks()` in
      `frameworks.py`, `eval/check_framework_freshness.py`, a Makefile
      target, and tests), confirmed via a real run against the registry.
    - §9's own text referenced test filenames
      (`test_compliance_language_boundary.py`, `test_report_concision.py`)
      that were never what actually got written — corrected to the real
      names (`test_language.py`, `test_assessment.py`'s compliance-boundary
      test class, `test_concision.py`).

    The deviation: **README status stays `draft`, not `active`.** The
    checklist's citation-integrity item can't honestly be checked — every
    framework file is explicitly `review_status: unreviewed`, and ISO/IEC
    27701 more so, since it's a paywalled standard whose text was never
    directly fetched. That item is also not "not applicable" (citations
    obviously apply here), so per the checklist's own rule — active only
    once every item is checked *or* explicitly marked not applicable — this
    project doesn't yet qualify, regardless of how much else works. Rather
    than flip the status anyway to match this step's literal wording, or
    silently leave it as the stale scaffold-era "draft" with no
    explanation, the README's Status section now says specifically what's
    done, what the one open item is, and what closes it — a real legal or
    standards expert reviewing `frameworks/*/*.yaml` and flipping each
    `review_status`. 105 tests, 97% coverage, clean under `ruff`,
    `mypy --strict`, and `agentskills validate` for both skills.
11. ~~**v1.1 — prove the second domain**~~ — **done, with one honest
    exception to the "don't touch anything outside frameworks/, rubric/,
    and one SKILL.md" test this step set for itself.**

    `frameworks/ai-governance/eu-ai-act.yaml` and `nist-ai-rmf.yaml` are
    registered (EU AI Act verified against artificialintelligenceact.eu's
    article/annex text directly — Art. 5 prohibited practices, Annex III's
    eight high-risk categories, Articles 9-15's obligations, Art. 50
    transparency; NIST AI RMF's four function names confirmed against
    NIST's own site, though its knowledge-base pages and PDF were
    unreachable for more than that, same honest-gap pattern as HIPAA/FERPA
    before it). `rubric/ai-criteria.md` has its own seven dimensions —
    risk classification, governance and accountability, data governance,
    transparency and documentation, accuracy/robustness/security, bias and
    fairness, human oversight — genuinely different content from the
    privacy rubric, not a renamed copy, with the EU AI Act risk-tier
    determination deliberately kept out of the JSON schema as a separate
    structured field and folded into `compliance` instead, exactly where a
    regulatory finding belongs. `assess-ai-system-risk-tier` is built,
    registered, and validated.

    The exception: `eval/sync_skill_bundle.py`'s `sync_all` assumed every
    skill shared one global rubric path — true when there was only one
    skill, false the moment a second rubric existed. Fixed by adding a
    `rubric` field to each `family-manifest.yaml` entry (the natural place,
    since it's already the single source of truth for what a skill needs)
    and reading it per-entry, falling back to the old global default for
    any entry that doesn't specify one. This is exactly the kind of gap the
    plan's own warning was designed to catch — a real, narrow, well-
    motivated fix to the bulk-sync convenience wrapper's unstated
    assumption, not a sign the underlying pluggable-framework architecture
    itself wasn't domain-agnostic. Everything else genuinely required zero
    changes: `frameworks.py`, `assessment.py`, `language.py`,
    `concision.py`, `report.py`, and `rubric.py` in `src/` never needed to
    know a second domain existed.

    Two more real findings, both fixed: `scripts/assessment.py` hardcoded
    `"criteria.md"` as its rubric filename — harmless with one skill,
    wrong with two. Generalized to discover its rubric file by name
    (`references/rubric/*.md`, expects exactly one), and a test now asserts
    the two skills' `assessment.py` files are structurally identical
    (`ast`-normalized) except for the domain-naming strings — proving the
    genericization actually took, not just asserting it. Separately,
    `report.py`'s standing disclosure hardcoded "DPO," accurate for privacy
    but domain-mismatched for AI governance; made generic ("an accountable
    person") since `report.py` is shared, byte-for-byte, across every
    domain's skills — the domain-specific role name belongs in each skill's
    own `SKILL.md` prose, not in shared code.

    Proved both flagships work end-to-end with the bare dependency-free
    interpreter on fresh fabricated scenarios (a diocesan volunteer
    background-check risk-scoring tool, for this domain), and that the new
    skill's validator genuinely rejects the other domain's dimension and
    framework ids rather than silently accepting them. 118 tests, 97%
    coverage, clean under `ruff`, `mypy --strict`, and `agentskills
    validate` for all three skills. Registered in
    `.claude-plugin/marketplace.json`; `README.md` and `CHECKLIST.md`
    updated to match.
12. From there: pick the next specialist skill from either table in §8 — building
    one mostly means adding a framework entry, a rubric, a manifest row, and a
    `SKILL.md`; the shared machinery already exists by this point.

    **First one built: `draft-privacy-notice-update`** — chosen deliberately
    as the lowest-risk next pick, since §8's own table describes it as
    reusing "the same rubric as §7": zero new framework research, zero new
    rubric authoring, just a new `SKILL.md` whose only genuinely new
    procedural step (step 5: drafting the actual notice language) happens
    directly in conversation and is never written into or validated by
    `scripts/assessment.py` — a notice is prose for a person to approve,
    not a structured record with a schema to enforce, so it deliberately
    stays outside the hard-rule-enforced JSON contract.

    This proved the one thing not yet tested: two `built` skills in the
    *same* domain sharing the *exact same* rubric and framework set via
    `family-manifest.yaml`'s per-entry `rubric` field, with no
    special-casing anywhere in `sync_all`. It held up completely —
    `draft-privacy-notice-update`'s bundled rubric, framework registry,
    and `scripts/assessment.py` are byte-for-byte identical to its
    sibling's own copies, confirmed by tests, not just assumed. 127 tests,
    97% coverage, clean under `ruff`, `mypy --strict`, and `agentskills
    validate` for all four skills. Registered in
    `.claude-plugin/marketplace.json`; `README.md` and `CHECKLIST.md`
    updated to match. Next: any of the remaining eight backlog skills in
    §8 — `triage-privacy-rights-request` and `triage-privacy-incident` in
    particular will be the first real test of a task shape that doesn't
    fit "assess an ongoing activity/system" as naturally (a point-in-time
    incident or a request doesn't map onto `subject.purpose` and
    `subject.retention` the way a processing activity or an AI system
    does) — worth designing deliberately rather than force-fitting the
    existing schema when that day comes.
13. **Built `triage-privacy-rights-request` — the first genuinely different
    task shape.** As step 12 flagged, a rights request doesn't map onto
    "score seven ongoing-quality dimensions" — designed a separate shape
    instead of stretching the existing one: `src/privacy_and_ai_governance/
    triage.py` validates `title`, `request` (description, type, a real
    ISO `received_date`), `frameworks_considered` (same discipline as the
    assessment shape — every framework considered, including inapplicable
    ones, each with a stated basis), a single `governing_deadline`
    (framework id must be marked applicable, `response_due` calculated
    from `received_date`, never earlier than it), a `gaps` checklist (each
    with a `blocking` boolean), `compliance`, and `cst_reflection`.
    `concision.lint_triage` and `report.render_triage_markdown` are new;
    `report.write_report` was generalized to take a `render_fn` parameter
    (default `render_markdown`, so every existing call site is unchanged)
    rather than duplicating the file-writing logic for a second shape.

    Added GDPR's own data-subject-rights framework
    (`frameworks/privacy/gdpr-data-subject-rights.yaml`, Arts. 12-22,
    verified against gdpr-info.eu's article text directly) — distinct from
    `gdpr-dpia`, since Art. 35's impact-assessment duty and Chapter III's
    response obligations are genuinely different duties, and a request
    should never cite the DPIA entry. Added a `response-deadline`
    required element to the existing `ccpa-cpra.yaml` (Civ. Code §
    1798.130(a)(2), 45+45 days) and `hipaa.yaml` (45 CFR 164.524(b)(2),
    30+30 days) — both already registered, both missing their own
    response-deadline citation until this step needed one.

    The one new piece of plumbing this shape required: a rubric-less
    skill. `sync_skill_references`'s `rubric_path` parameter is now
    `Path | None`, skipping the rubric-sync block entirely when `None`;
    `sync_all` now distinguishes three states per manifest entry — an
    explicit string path (sync it), no `rubric` key at all (fall back to
    the project default, unchanged behavior for every existing entry), and
    an explicit `rubric: null` (sync no rubric — this skill).
    `sync_skill_scripts` gained an optional `modules` parameter so
    `sync_all` can exclude `rubric.py` for a rubric-less entry — copying a
    parser for a file that doesn't exist would misleadingly suggest the
    skill scores something. `family-manifest.yaml`'s
    `triage-privacy-rights-request` entry is `rubric: null`, with a comment
    explaining why, and now flipped to `status: built`.

    `scripts/triage.py` is hand-authored, dependency-free, and structurally
    the same validation logic as `src/privacy_and_ai_governance/triage.py`
    (same pattern as `scripts/assessment.py`'s relationship to its own
    `src/` counterpart) — it reads `references/frameworks/index.json`
    instead of parsing YAML, and has no `rubric.py` sibling or
    `references/rubric/` directory to read, since there's nothing here to
    parse. Proved end-to-end with the bare dependency-free `python3.12`
    interpreter (no venv, no site-packages) on a fabricated former-employee
    deletion request citing CCPA/CPRA's 45-day deadline with a payroll-
    retention gap flagged as blocking — rendered correctly, governing
    deadline stated prominently, compliance before the CST reflection.

    177 tests, 97% coverage, clean under `ruff`, `mypy --strict`, and
    `agentskills validate` for all five skills. Registered in
    `.claude-plugin/marketplace.json`; `README.md` and `CHECKLIST.md`
    updated to match. Next: any of the remaining seven backlog skills in
    §8 — `triage-privacy-incident` can now reuse this same triage shape
    directly rather than designing a third one.
14. **Built `triage-privacy-incident` — and step 13's own closing note
    turned out to be wrong.** Started from the assumption that
    `triage-privacy-incident` could reuse `triage.py`'s shape directly.
    Designing it for real surfaced a genuine mismatch, not a superficial
    one: `triage.py`'s `governing_deadline` is singular by design — a
    rights request has one requester, and when multiple frameworks apply,
    exactly one deadline actually governs the response to them. An
    incident is structurally different — it can trigger several
    **independent, simultaneous** notification obligations to different
    audiences at once (a supervisory authority under one framework,
    affected individuals under another, a state attorney general under a
    third), none of which "governs" over the others. Force-fitting that
    into one `governing_deadline` field would have silently dropped
    every obligation but one. Caught this before writing any code, not
    after — worth recording as the honest correction to step 13's
    prediction that it was.

    Built a third module instead, `src/privacy_and_ai_governance/
    incident.py`, sharing `triage.py`'s helpers and discipline
    (`_nonempty`, `_parse_date`, the same `frameworks_considered`
    pattern, the same compliance/CST boundary) but with its own shape:
    `incident` (facts: description, `discovered_date`, affected systems,
    data types, an estimate of individuals affected), `severity` (one of
    `low`/`moderate`/`high`/`critical`, with a rationale — the one place
    in this project's schemas that validates against a fixed enum rather
    than free text, because "how bad is this" needs to sort and compare
    across incidents in a way a rights-request classification doesn't),
    `notification_obligations` (a **list**, each with its own
    `framework_id`, `audience`, `citation`, `due_date`, and `basis` — the
    structural fix), `gaps`, and `escalation` (`required` plus a
    rationale, directly matching `jobduties.md`'s "Escalate incidents
    that meet predefined severity, notification, legal, or
    executive-reporting thresholds"). `concision.lint_incident` and
    `report.render_incident_markdown` are new siblings of their
    `triage`-shaped counterparts; `report.py`'s existing `render_fn`
    parameter on `write_report` needed no change at all — this is exactly
    what it was generalized for in step 12.

    Three new frameworks needed for this skill to have anything to
    reason over, each citation verified against a primary source before
    writing it down: `gdpr-breach-notification` (Arts. 33-34, verified
    against gdpr-info.eu's article text — 72 hours to the supervisory
    authority, without-undue-delay to data subjects when high-risk,
    split into two required elements since the two audiences have
    different deadlines and different exception conditions);
    `ca-breach-notification` (Civ. Code § 1798.82, verified directly
    against leginfo.legislature.ca.gov's statutory text through two
    successive fetches — the first fetch's own paraphrase claimed a
    30-day deadline, which didn't match this author's prior general
    knowledge of the older "most expedient time possible" standard, so a
    second fetch pulled the literal text of (a)(2)(A)-(B) to resolve the
    discrepancy directly rather than either trusting the paraphrase or
    silently reverting to memory — the statute genuinely was amended to
    add the 30-day standard, confirmed from its own words, not
    reconciled by guessing). `hipaa.yaml` already had a `breach-
    notification` required element from step 7 and needed no changes.
    Registered `ca-breach-notification` and `gdpr-breach-notification` as
    separate framework files from `ccpa-cpra` and `gdpr-dpia`/`gdpr-
    data-subject-rights` respectively, matching this registry's existing
    pattern of splitting by citation root and applicability trigger, not
    by statute family — a breach-notification duty and a consumer/
    data-subject-rights duty are genuinely different obligations even
    under the same code title.

    `family-manifest.yaml`'s `triage-privacy-incident` entry is now
    `rubric: null`, `status: built` — no sync-layer changes were needed
    this time, since step 13 already built rubric-less-skill support
    generically. `scripts/incident.py` is hand-authored, dependency-free,
    structurally the same validation logic as `src/privacy_and_ai_
    governance/incident.py`. Proved end-to-end with the bare
    dependency-free `python3.12` interpreter on a fabricated stolen-
    laptop scenario spanning California and EU donors — three
    independent notification obligations (California residents, the EU
    supervisory authority, EU data subjects) all rendered as separate,
    correctly dated line items, not collapsed into one.

    238 tests, 98% coverage, clean under `ruff`, `mypy --strict`, and
    `agentskills validate` for all six skills. Registered in
    `.claude-plugin/marketplace.json`; `README.md` and `CHECKLIST.md`
    updated to match. Next: any of the remaining six backlog skills in
    §8 — `triage-ai-incident` is this skill's AI-governance sibling and
    can likely reuse the `incident.py` shape (severity + parallel
    notification/reporting obligations) directly, the same way this step
    reused step 13's rubric-less sync-layer plumbing.
15. **Built `triage-ai-incident` — and this time the reuse prediction held.**
    Unlike step 14's correction of step 13's own prediction, `incident.py`
    turned out to be genuinely domain-agnostic: nothing in its schema
    (`incident`, `frameworks_considered`, `severity`,
    `notification_obligations`, `gaps`, `escalation`, `compliance`,
    `cst_reflection`) is privacy-specific — the same reason `assessment.py`
    carried across domains unchanged at step 11. No new `src/` module was
    needed; `triage-ai-incident/scripts/incident.py` is the exact same
    validation logic as its privacy sibling's copy, hand-authored again
    (not synced, matching every other skill's own `scripts/{assessment,
    triage,incident}.py`) with only the module docstring and argparse
    description string naming the domain — proven structurally identical
    via the same `ast`-normalized comparison test step 11 introduced for
    `assessment.py`.

    Added Art. 73's serious-incident reporting duty to `eu-ai-act.yaml`
    (previously covering only the pre-deployment Chapter III obligations,
    nothing about an incident after deployment) — verified against
    artificialintelligenceact.eu's article text directly, including the
    "serious incident" definition itself (Art. 3(49): death or serious
    harm to health, critical-infrastructure disruption, a fundamental-
    rights-obligation infringement, or serious harm to property/
    environment) and all three reporting-deadline tiers (15 days general,
    2 days for a widespread infringement or critical-infrastructure
    disruption, 10 days for a death). `nist-ai-rmf.yaml` needed no
    changes — its MANAGE function already covered incident response
    generically from when the framework was first registered at step 11,
    and as a voluntary framework it has no statutory deadline of its own;
    `SKILL.md` step 3 says explicitly to record an institution's own
    adopted internal target here rather than inventing a regulatory one
    where none exists.

    `family-manifest.yaml`'s `triage-ai-incident` entry is `rubric: null`,
    `status: built` — no sync-layer or manifest-resolution changes needed,
    since steps 13-14 already built that plumbing generically. Proved
    end-to-end with the bare dependency-free `python3.12` interpreter on a
    fabricated emergency-call-triage misclassification scenario meeting
    the EU AI Act's own "serious incident" definition — two independent
    obligations (a 15-day statutory filing to the EU market surveillance
    authority, a next-business-day internal governance-committee report
    under an adopted NIST AI RMF target) both rendered correctly with
    their own dates and citations, not collapsed into one.

    251 tests, 98% coverage, clean under `ruff`, `mypy --strict`, and
    `agentskills validate` for all seven skills. Registered in
    `.claude-plugin/marketplace.json`; `README.md` and `CHECKLIST.md`
    updated to match. Next: any of the remaining five backlog skills in
    §8 — `review-vendor-privacy-assessment` and `review-ai-vendor-
    governance` are a similar same-shape-across-domains pair waiting to
    happen, this time for a "review a document against a baseline and
    flag gaps" task shape that doesn't yet exist in this project.
16. **Built `review-vendor-privacy-assessment` and `review-ai-vendor-
    governance` together — the fourth task shape, and the first time a
    new shape was built for both domains in one step rather than one
    then the other.** A vendor review doesn't fit any of the three
    existing shapes: it isn't scored 1-5 (there's no "3 out of 5" for
    whether a DPA exists), and it isn't anchored to a single event with a
    deadline the way a rights request or an incident is. It's a fixed
    checklist, each item independently `satisfied`/`partial`/`missing`
    against what a vendor's documentation actually shows — closer in
    spirit to the rubric shape's "one entry per known id" discipline than
    to the triage/incident shapes' date arithmetic, but scored as a
    status enum with conditional required fields (`evidence` for
    `satisfied`/`partial`, `gap` for `partial`/`missing`) rather than 1-5.

    This meant a genuinely new authored-content type, not just a new
    module: `baselines/privacy-vendor.md` (eight items: written
    data-processing terms, sub-processor disclosure, security-controls
    evidence, breach-notification commitment, data return/deletion, audit
    rights, international transfer mechanism, minimum-necessary access
    scope) and `baselines/ai-vendor.md` (seven items: model documentation,
    evaluation results, incident-notification commitment, upstream
    dependency disclosure, human-oversight support, model-update
    notification, training-data governance) — same heading format as
    `rubric/criteria.md` (`## N. Name — \`id\``) so a new stdlib-only
    `src/privacy_and_ai_governance/baseline.py` could parse item ids with
    the identical regex `rubric.py` already used, rather than inventing a
    second parsing convention. Both baseline documents are professional-
    judgment checklists, not verbatim statutory text, the same way
    `rubric/criteria.md` is — grounded in specific citations already
    verified earlier in this project (GDPR Art. 28 processor terms, Art.
    32 security, Art. 33(2) processor-to-controller notice, Chapter V
    transfers; EU AI Act Arts. 10/11/14/15/73) where a specific provision
    backs an item, general vendor-diligence best practice where one
    doesn't — exactly like a rubric dimension's own mix.

    `src/privacy_and_ai_governance/review.py` is the fourth validation
    module, sharing the `frameworks_considered` discipline with its three
    siblings but otherwise its own shape: `vendor`, `baseline_items`
    (exactly one per known baseline id, the same missing/unknown/
    duplicate checks `assessment.py` runs for rubric dimensions),
    `remediation_commitments`, `reassessment_due`, `overall_risk`
    (reusing the same four-level severity enum `incident.py` introduced,
    for consistency across shapes rather than a fifth naming scheme).
    `concision.lint_review` and `report.render_review_markdown` are new
    siblings of their `incident`-shaped counterparts, needing no changes
    to `write_report`'s `render_fn` parameter — the second shape in a row
    to need zero changes there, confirming step 12's generalization was
    the right level of abstraction.

    The sync layer needed one real extension, not a rebuild: a `baseline`
    field alongside `rubric` in `family-manifest.yaml`, with only two
    states (present or absent) rather than `rubric`'s three, since no
    entry predates this field and there's no historical default to fall
    back to. `sync_skill_references` gained a `baseline_path: Path | None
    = None` parameter mirroring the `rubric_path` block exactly;
    `sync_all`'s `scripts_to_sync` list-building was generalized from a
    single rubric-conditional branch to two independent conditionals
    (append `rubric.py` if a rubric exists, `baseline.py` if a baseline
    exists) rather than hard-coding every combination.

    Built both skills together rather than sequentially, since the second
    was zero-marginal-cost the same way `triage-ai-incident` was: hand-
    authored `scripts/review.py` copied verbatim between them with only
    the module docstring and argparse description string changed,
    confirmed structurally identical by the same `ast`-normalized
    comparison test every prior cross-domain reuse has used. Proved both
    end-to-end with the bare dependency-free `python3.12` interpreter —
    a diocesan cloud-backup vendor with a missing sub-processor
    disclosure and an unstated deletion timeframe (privacy), and a
    hospital's emergency-triage AI vendor with a missing model-update-
    notification commitment (AI governance) — both rendering the full
    baseline-item table, remediation commitments with dates, and overall
    risk correctly.

    325 tests, 98% coverage, clean under `ruff`, `mypy --strict`, and
    `agentskills validate` for all nine skills. Registered in
    `.claude-plugin/marketplace.json`; `README.md` and `CHECKLIST.md`
    updated to match. Next: any of the remaining four backlog skills in
    §8. `draft-ai-risk-impact-assessment` and `draft-model-card` read as
    assessment-shaped and should need no new task shape. The other two
    are less certain from the table description alone:
    `review-data-retention-entry` ("flags whether it needs deletion,
    review, or an updated retention justification") may fit the review
    shape's per-item check loosely but outputs one verdict rather than a
    checklist, and `map-regulatory-change` ("summarizes a pasted
    development and maps affected policies") doesn't obviously fit any
    of the four shapes built so far — both worth designing deliberately
    when picked up, per this project's own recurring lesson, rather than
    assumed to fit in advance.

    **§8 correction, added before this step's own work:** rereading
    `ai-gov-duties.md` directly (rather than trusting the earlier summary
    of it §8 was originally drafted from) surfaced two AI-governance
    duties with no corresponding backlog row: "Regulatory & Standards
    Monitoring" (a near-mirror of `jobduties.md`'s "Regulatory
    Monitoring," which `map-regulatory-change` already comes from) and
    "Testing, Validation & Performance Monitoring"'s overdue-reassessment
    language (a looser analog of `review-data-retention-entry`). Added
    `map-ai-regulatory-change` and `review-ai-system-reassessment` to
    §8's AI-governance table as `planned`, and corrected
    `family-manifest.yaml`'s existing `review-data-retention-entry` and
    `map-regulatory-change` entries — both previously still listed
    `rubric: rubric/criteria.md`, which misleadingly implied they'd be
    rubric-scored after this very step concluded they probably aren't;
    both now `rubric: null` with a comment pointing at the open design
    question. The same discipline this project asks of every citation —
    verify against the primary source, don't trust a prior summary —
    applied here to its own planning document.
17. **Built `draft-model-card` — the fifth skill sharing an already-proven
    shape, and a check for accidental duplication before building.**
    Before writing anything, compared `draft-ai-risk-impact-assessment`
    and `draft-model-card` against what `assess-ai-system-risk-tier`
    actually became at step 11: the built skill already produces a full
    seven-dimension rubric-scored assessment (`risk-classification`
    through `human-oversight`) against the same framework registry —
    not the narrower "inventory classification only" tool §8's original
    duty-document split implied. `draft-ai-risk-impact-assessment`'s own
    row description ("bias/fairness, explainability, robustness, and
    human-oversight design") maps onto that same rubric almost exactly,
    which means building it as literally described right now would
    produce a near-duplicate of an already-built skill, not a new one.
    Flagged this to the user rather than either building the duplicate
    or unilaterally deciding how to differentiate it — a real product-
    scope call, not a citation or architecture question this project's
    own conventions could resolve alone. Deferred; not built this step.

    `draft-model-card` had no such conflict — "Model & System
    Documentation" is a duty section nothing else built so far covers —
    so it proceeded the same way `draft-privacy-notice-update` did at
    step 12: shares `assess-ai-system-risk-tier`'s exact rubric
    (`rubric/ai-criteria.md`) and framework registry, byte-for-byte
    identical `scripts/assessment.py`, with the only new work being
    step 5 of its own `SKILL.md` (drafting the card content itself,
    outside the validated JSON schema, the same way notice language sits
    outside `draft-privacy-notice-update`'s).

    Registered `iso-42001` (ISO/IEC 42001:2023, the AI management system
    standard) in `frameworks/ai-governance/` first, since Annex A.8
    ("information for interested parties") is this skill's most direct
    grounding and no AI-governance documentation standard was registered
    yet. Paywalled like `iso-27701`, so sourced the same way: its clause
    4-10 high-level structure and ten-category Annex A control set
    (A.2-A.10) came from a secondary source (isms.online) summarizing
    the standard's publicly known structure — ISO's own site returned
    403 on direct fetch, the same blocking pattern HHS.gov and eCFR
    showed earlier in this project — not a fetch of the purchased
    standard's own text, flagged with the same stronger caveat
    `iso-27701`'s file carries.

    Registering a framework in an *existing, already-built* domain
    surfaced something the pluggable-framework tests never exercised
    directly: every other built skill in that domain picks up the new
    entry on the next sync too, not just the skill being built. Three
    tests (`test_ai_governance_skill.py`, `test_ai_incident_skill.py`,
    `test_ai_vendor_review_skill.py`) had hardcoded their bundled-
    framework assertions as an exact set of two ids; all three now assert
    by membership plus a wrong-domain exclusion instead — the same
    "registry grew, assert by id not by count" fix step 7 already made
    once for the privacy domain, now needed for the AI-governance one
    too.

    Proved end-to-end with the bare dependency-free `python3.12`
    interpreter on a fabricated diocesan volunteer background-check
    risk-scoring tool, citing ISO/IEC 42001 Annex A.8 directly in the
    compliance finding. 335 tests, 98% coverage, clean under `ruff`,
    `mypy --strict`, and `agentskills validate` for all ten skills.
    Registered in `.claude-plugin/marketplace.json`; `README.md` and
    `CHECKLIST.md` updated to match. Next: `draft-ai-risk-impact-
    assessment` needs its differentiation from `assess-ai-system-risk-
    tier` resolved with the user before it can be built; the citation-
    review checklist item (§9/`CHECKLIST.md`) needs the user's own
    input on what "closing" it can actually mean, since it was written
    to require a qualified human reviewer this project's own agent
    can't stand in for.

    **Resolved:** the user chose to retire `draft-ai-risk-impact-
    assessment` outright rather than fold the gap into
    `assess-ai-system-risk-tier` or build a narrower re-assessment-
    triggered variant. `family-manifest.yaml`'s entry is now `status:
    retired` (a new third status, alongside `built`/`planned`, kept
    rather than deleted for the same audit-trail reason
    `frameworks/index.yaml` never deletes a retired framework) and §8's
    table row above is struck through with the reason recorded inline.

    The citation-review checklist item stayed open, honestly — a
    generated review document (all twelve frameworks' citations,
    organized by domain, with the two paywalled standards flagged
    distinctly) was published for the user's own pass, since a genuine
    legal/standards review needs a qualified human reviewer this
    project's own agent structurally cannot stand in for. Progress on
    that item happens in conversation, not in this file.
18. **Built the fifth and sixth task shapes, and closed out the entire
    remaining backlog in one step.** The two skills §8's correction left
    open — `review-data-retention-entry`/`review-ai-system-reassessment`
    and `map-regulatory-change`/`map-ai-regulatory-change` — turned out
    to need two genuinely different new shapes, not one, confirming the
    honest uncertainty flagged when they were added to the backlog table.

    **The retention/reassessment shape** (`src/privacy_and_ai_governance/
    retention.py`) is deliberately the smallest in the family: one
    inventory entry, `frameworks_considered` (the same discipline every
    prior shape uses), and a single `verdict` — `current`, `needs-
    review`, `needs-update`, or `retire` — with a `target_date` required
    whenever the action isn't `current`. No score, no list, no checklist;
    resisted padding it to match its siblings' size. The four-value
    action enum was built as the union of both duty documents' own stated
    outcomes (privacy: delete/review/updated-justification; AI
    governance: overdue-reassessment/documentation-update/current) plus
    the logically-necessary "no action needed" state neither document
    spelled out for the other domain — not fabricated, just generalized
    honestly from what both actually said.

    **The regulatory-change shape** (`src/privacy_and_ai_governance/
    regulatory_change.py`) is the first in this project that doesn't
    evaluate an institution's own activity, system, vendor, or entry at
    all — it ingests an external input (a pasted regulatory or standards
    development) and maps its impact against this project's *own*
    `frameworks/index.yaml`. Its `frameworks_considered` deliberately
    uses a different field name, `impacted` rather than `applicable`,
    since the question being asked is genuinely different ("does this
    development change what an already-registered framework requires,"
    not "does this framework apply to the institution") — reusing
    `applicable` would have quietly blurred that distinction.
    `recommended_actions` is the actual deliverable: a typed diff against
    the registry (`register-new-framework`, `update-required-element`,
    `retire-framework`, `no-action`), with `framework_id` conditionally
    required or forbidden depending on the action type, the same
    conditional-requirement discipline `review.py`'s `evidence`/`gap`
    fields already established. The shared `_lint_compliance_and_cst_
    reflection` helper in `concision.py` needed one small, honest
    generalization here: it previously only recognized `applicable` when
    scaling the compliance-length allowance, which would have silently
    floored every regulatory-change record's allowance at the minimum
    regardless of how many frameworks were actually impacted — now checks
    `applicable` *or* `impacted`.

    Both shapes needed no sync-layer changes at all: a skill using
    neither `rubric` nor `baseline` already resolves to the core
    three-module `scripts_to_sync` list from step 16's generalization,
    which is exactly what these four skills need. Built all four
    together rather than two-then-two, since each domain pair is the
    same zero-marginal-cost reuse step 15/16/17 already established —
    `scripts/retention.py` and `scripts/regulatory_change.py` are
    hand-authored once per shape and copied verbatim into each pair's
    second skill with only the docstring, argparse description, and (for
    `retention.py`, since "retention entry" read oddly for an AI system)
    the error-message wording differing — confirmed structurally
    identical by the same `ast`-normalized comparison test every prior
    cross-domain reuse has used.

    Proved all four end-to-end with the bare dependency-free `python3.12`
    interpreter: a diocesan volunteer-archive entry correctly verdicted
    `retire` after its stated purpose lapsed; an emergency-triage AI
    system correctly verdicted `needs-review` against its own EU AI Act
    Art. 9-grounded re-evaluation interval; a new Texas privacy statute
    correctly recommending `register-new-framework` with no existing
    entry referenced; and a NIST AI RMF companion profile correctly
    recommending `update-required-element` against the already-registered
    `nist-ai-rmf` entry.

    441 tests, 98% coverage, clean under `ruff`, `mypy --strict`, and
    `agentskills validate` for all thirteen skills. Registered all four in
    `.claude-plugin/marketplace.json`; `README.md`, `CHECKLIST.md`, and
    §8's own table updated to match. With this step, every skill in both
    backlog tables is built except the one deliberately retired duplicate
    — the only work left on this project is the citation-review checklist
    item, and it can only close with the user's own domain expertise, not
    another build step.
19. **Closed the citation-review checklist item — the project's last open
    go-live item.** The user (this project's own DPO) reviewed the step
    18 artifact and confirmed all twelve frameworks, across both domains.
    Confirmed the scope explicitly before acting on it — the user's DPO
    role plausibly covers the nine privacy frameworks without question,
    but the three AI-governance ones (EU AI Act, NIST AI RMF, ISO/IEC
    42001) are a different expertise, and the review artifact's own
    instructions had explicitly said those three could honestly stay
    `unreviewed` if out of scope. Asked rather than assumed a blanket
    "I reviewed it" covered all twelve; confirmed it did.

    Flipped `review_status: unreviewed` → `review_status: reviewed` in
    all twelve `frameworks/*.yaml` files — nothing else in those files
    changed, including the paywalled-standard sourcing caveats on
    `iso-27701` and `iso-42001`, which remain accurate historical
    statements about how those two files were authored regardless of
    review status. Re-ran the sync so every skill's bundled framework
    copies reflect the new status; re-ran the full test suite, `ruff`,
    `mypy --strict`, `agentskills validate`, and
    `check-framework-freshness` to confirm nothing depended on the old
    value — nothing did. `CHECKLIST.md`'s citation-review item is now
    checked, with the review history recorded rather than the box simply
    flipped silently. `README.md`'s Status section moves from `draft` to
    `active` — the one condition that section named for the move,
    reached honestly rather than declared early.

    This closes every remaining item from `build-plan.md` §8 and
    `CHECKLIST.md`. The project has no further open work of its own
    unless new duty-document scope, a new framework, or a new regulatory
    development gives it some.
20. **Moved `cst_reflection` to lead the rubric-scored report shape, as a
    Catholic executive summary — user-requested, scoped to the four skills
    that share `render_markdown`.** The user asked, for the DPIA skill
    specifically, whether `cst_reflection` would read better as a brief
    presence in every section or as a single reflection at the end (the
    existing design, per §2.1). Recommended keeping a single section
    rather than interleaving — interleaving risks the exact vocabulary
    bleed §2.1's blocklist exists to prevent — but the user redirected:
    not the end, the *top*, functioning as a Catholic executive summary
    that explains the assessment's findings in CST terms before the
    compliance detail. Confirmed scope explicitly before acting on it,
    since `render_markdown` is shared verbatim by four skills, not just
    the one named: applying this to all four, to keep this family's
    "same shape, reused unchanged" discipline intact, rather than forking
    `draft-privacy-impact-assessment` alone into a one-off layout.

    §2.1 amended in place (see the amendment note above its enforcement
    bullets) to state the ordering exception and why it doesn't weaken the
    underlying rule: §2.1's real requirement was always about vocabulary
    never crossing the compliance/CST boundary, not about which section a
    reader sees first. `render_markdown`'s heading also changed, from
    "Catholic Social Teaching reflection" to "Catholic Social Teaching
    summary," to name what it now does — summarize specific findings for a
    reader who may stop there, not close with an unattached meditation.
    The other five renderers (`render_triage_markdown`,
    `render_incident_markdown`, `render_review_markdown`,
    `render_retention_markdown`, `render_regulatory_change_markdown`) are
    untouched: compliance still precedes `cst_reflection` in every shape
    but this one.

    Updated `src/privacy_and_ai_governance/report.py` (the one hand-edited
    source; `make sync-skill-bundle` propagated it byte-for-byte into all
    thirteen skills' `scripts/report.py`, including the nine whose own
    renderer didn't change), the ordering assertions in `test_report.py`,
    `test_flagship_skill.py`, and `test_ai_governance_skill.py`, and the
    four affected skills' own `SKILL.md` `## Grounding` sections, so the
    instruction to write `cst_reflection` now says what it's actually for:
    naming what the rubric found, not staying in the abstract, since a
    reader who stops after the summary should still learn something true
    and specific about this assessment. Full suite, `ruff`, `mypy --strict`,
    and `agentskills validate` all clean afterward.
