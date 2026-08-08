# Theological review log

A dated record of substantive changes to `principles/` or `rubric/`, and the reasoning behind them — the direct fix for "who has interpretive authority" over a working (not canonical) interpretation of CST, now that no single named reviewer holds that role. See `../CODEOWNERS` and `../CONTRIBUTING.md` "Beta status" for the current review model: ordinary technical review plus this log, not a standing theological sign-off.

No content reviews by a named theological reviewer have occurred. This is a process log entry, not a content review:

## 2026-08-07 — sign-off requirement paused for beta
Decision by: project maintainer (sgmuff)
Change: `CODEOWNERS`'s theological-reviewer requirement for `principles/` and `rubric/` is paused for this project's beta phase, to be reimposed before the project leaves beta — see `../CONTRIBUTING.md` "Beta status".
Notes: any principle or rubric content written before this is lifted is unreviewed and must be marked as such. This entry exists so the pause itself is dated and visible, not just the requirement it suspends.

## 2026-08-08 — named theological-reviewer requirement retired, not just paused
Decision by: project maintainer (sgmuff)
Change: `CODEOWNERS` no longer names a placeholder theological-reviewer slot for `principles/` and `rubric/`; both now fall under the same technical-maintainer review as `eval/` and `integrations/`. In its place, `eval/report.py`'s rendered report now always recommends that a parish using a finding route it to their own pastor or someone else there well versed in Catholic theology before acting on it, and states its unreviewed/beta status without pointing to this project's internal files by name.
Notes: this moves "who has interpretive authority" from a single named project-level reviewer (never recruited in practice) to the person actually accountable for how a finding gets used at each parish. Content is no less unreviewed than before; this log and dated entries for substantive `principles/`/`rubric/` changes remain the record of what changed and why, per `../CHECKLIST.md`.

## 2026-08-08 — bright-line gate expanded with two items from CCC 1867
Decision by: project maintainer (sgmuff), during the beta pause — **unreviewed**, logged per the pause terms above.
Change: `principles/non-negotiables.yaml` grew from three items to five. Added `systemic-wage-theft-by-design` and `facilitation-of-trafficking-or-sexual-exploitation`, both grounded in CCC 1867's "sins that cry to heaven" and Evangelium Vitae §3 (quoting *Gaudium et Spes* §27); added a CCC 1867 citation to the existing `direct-killing-of-the-innocent` item. See `../docs/ccc-citation-map.md` for full citations and verification notes.
Notes: CCC 1867 names five things ("the blood of Abel," "the sin of the Sodomites," "the cry of the oppressed in Egypt," "the cry of the foreigner, the widow, and the orphan," "injustice to the wage earner"). Only two became new gate items — oppression of the poor/foreigner was judged to belong in the graded principles instead, since (unlike the gate's other items) it admits of mitigation rather than being a flat stop. The `facilitation-of-trafficking-or-sexual-exploitation` item's grounding in "the sin of the Sodomites" is the single most interpretively contested citation in this file — the underlying narrative (Genesis 19, Ezekiel 16:49-50) supports more than one reading, and the item was deliberately written to the reading both agree on (trafficking, sexual exploitation, CSAM) rather than the contested part. This needs explicit attention from the named theological reviewer once one exists, not just a routine sign-off — see `../CHECKLIST.md`.

## 2026-08-08 — bright-line citations restructured from file-wide to per-item
Decision by: project maintainer (sgmuff), during the beta pause — logged per the pause terms above.
Change: `principles/non-negotiables.yaml`'s citations moved from a single top-level `grounding` list to a `citations` list per item; `eval/principles.py` and `eval/assessment.py` updated to match.
Notes: not a theological content change — no citation was added, removed, or reworded in substance, only rescoped to the item it actually grounds. Logged here anyway for a complete audit trail of this file's history, per this project's general practice of dating every change to `principles/` or `rubric/`, not because it needs the theological reviewer's sign-off.

## 2026-08-08 — Catechism of the Catholic Church citations added to all eight graded principles
Decision by: project maintainer (sgmuff), during the beta pause — **unreviewed**, logged per the pause terms above.
Change: each of the eight `principles/*.yaml` files gained a CCC `magisterial_citations` entry. See `../docs/ccc-citation-map.md` for the full mapping; every paragraph range was checked directly against its primary-source page.
Notes: no existing Compendium or Magnifica Humanitas citation was changed. `social-justice.yaml` and `solidarity.yaml` cite an overlapping CCC range (1939-1942) because the Catechism itself nests "Human Solidarity" inside its "Social Justice" article — flagged in both files' citation comments so it doesn't read as a duplication error.

## 2026-08-08 — USCCB foundational-documents list, Tier A: one encyclical citation added per graded principle
Decision by: project maintainer (sgmuff), during the beta pause — **unreviewed**, logged per the pause terms above.
Change: each of the eight `principles/*.yaml` files gained one additional `magisterial_citations` entry from the USCCB's foundational-documents list. See `../docs/ccc-citation-map.md` for the full mapping and per-citation verification notes.
Notes: seven of the eight citations were checked by direct fetch against vatican.va (one, Sollicitudo Rei Socialis §42, via a paginated mirror of the same official translation after vatican.va's own page proved too long to fetch that far). The eighth, Evangelium Vitae §57 on `dignity-and-inviolability-of-life.yaml`, could not be directly fetched at all — vatican.va's page was too long and no working paginated mirror was found. It is included on the strength of five-plus independent secondary sources quoting the same paragraph number and near-identical wording, explicitly flagged as a lower-confidence verification in `docs/ccc-citation-map.md` rather than presented as equivalent to the other seven. A named theological reviewer should treat this one as needing its own direct-fetch check, not just a content sign-off.

## 2026-08-08 — USCCB foundational-documents list, Tier B: two new worked cases in known-tensions.md, plus the seed case written up
Decision by: project maintainer (sgmuff), during the beta pause — **unreviewed**, logged per the pause terms above.
Change: `rubric/known-tensions.md` went from one unwritten TODO seed case to three fully worked cases. This is the most interpretively significant change of this whole session's work — unlike a citation addition, each case is a judgment call about *which two principles are actually in tension* and *why the tension is real rather than one side just being wrong*.
Notes: the immigration-enforcement case leans directly on CCC 2241's own two-sided structure (the paragraph states both a welcome-the-foreigner obligation and a state's-right-to-regulate clause without resolving the tension between them) rather than this project inventing a tension the source text doesn't itself pose — a deliberate choice to stay as close as possible to a case the tradition already frames as unresolved, per this project's stated non-goal of not manufacturing contested cases. The recidivism-risk case is grounded in a well-documented real pattern (proxy variables for race/poverty in deployed risk-scoring tools) rather than a hypothetical. Both need theological-reviewer sign-off on whether the tension is characterized accurately, not just whether the citations check out.

## 2026-08-08 — USCCB foundational-documents list, Tier C: full list catalogued, not cited
Decision by: project maintainer (sgmuff), during the beta pause — logged per the pause terms above.
Change: added `docs/usccb-foundational-documents-index.md`, cataloguing the USCCB's full ~80-document foundational-documents list and marking which are cited (Tier A/B above) versus not (everything else).
Notes: not a theological content change — nothing in this file is used anywhere in `principles/` or `rubric/`; it exists so a future contributor doesn't have to re-derive the list from the USCCB page. No sign-off needed for this entry specifically, logged for completeness.

## 2026-08-08 — follow-up verification closed out; fourth known-tensions.md case added
Decision by: project maintainer (sgmuff), during the beta pause — **unreviewed**, logged per the pause terms above.
Change: (1) Evangelium Vitae §57 and Compendium §301-302, both previously flagged as not directly fetched from vatican.va, are now verified via paginated mirrors of the same official texts (IntraText for EV§57, Catholic Culture's chaptered Compendium for §301-302); Compendium §301-302 added to `non-negotiables.yaml`'s `systemic-wage-theft-by-design` item. (2) A fourth `rubric/known-tensions.md` case added: AI-driven workforce automation, grounded in USCCB's *Economic Justice for All* (1986).
Notes: this closes every open item logged in `docs/ccc-citation-map.md`'s "Next" section as of the previous entry, except the theological reviewer's own sign-off, which stays open until `CODEOWNERS` names one. The workforce-automation case is, like the other three, a judgment call about which principles are genuinely in tension — flagged for the same reviewer attention as the rest of `known-tensions.md`.

## 2026-08-08 — remaining USCCB foundational-documents candidates closed out: capital-sentencing addendum and a fifth known-tensions case
Decision by: project maintainer (sgmuff), during the beta pause — **unreviewed**, logged per the pause terms above.
Change: (1) case 3 of `rubric/known-tensions.md` gained a "sharper instance" addendum on AI risk-scoring feeding capital-sentencing decisions, citing CCC 2267 (verified directly) and USCCB's *A Culture of Life and the Penalty of Death* (secondary-corroborated only — its PDF has no extractable text and no HTML mirror was found). (2) A fifth case added: AI-generated voter guides, citing USCCB's *Forming Consciences for Faithful Citizenship* §34 (verified directly via a diocesan mirror).
Notes: the capital-sentencing addendum makes an explicit, non-obvious judgment call worth flagging for the reviewer specifically: it deliberately does *not* mark that instance `contested: true` the way the rest of the case is, on the reasoning that CCC 2267's 2018 revision substantially resolves which side of the common-good/dignity tension wins once modern detention removes the public-safety justification for execution specifically. This is a stronger claim than any other `known-tensions.md` entry makes (everywhere else, the file's whole point is refusing to resolve the tension) — the reviewer should check specifically whether treating this one instance as resolved rather than contested is the right call, not just whether the citations check out. The voter-guide case is a judgment call about the tension itself, same as the other four.

<!--
Entry format:

## YYYY-MM-DD — <what was reviewed>
Reviewer: <name>
Change: <what changed, or link to the PR>
Notes: <what the reviewer said, including any disagreement or condition>
-->
