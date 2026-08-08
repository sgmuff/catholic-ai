# Catechism of the Catholic Church (and other newly-added sources) — citation map

This file has grown beyond just the Catechism — it now also covers the
"Tier A" USCCB foundational-document encyclicals added 2026-08-08 (see
`../CHANGELOG.md`). Kept as one file rather than splitting, since both
additions were verified and landed together and reference each other (e.g.
Gaudium et Spes §26 is the source both the Compendium's and the CCC's
common-good definitions draw from).

A reference for whoever fills in `principles/*.yaml`'s `magisterial_citations`
or `principles/non-negotiables.yaml`'s `grounding` — not itself a citation.
Follows the same discipline as `compendium-citation-map.md`: every paragraph
number below was checked directly against the primary text at the cited URL,
not reconstructed from memory or a secondary summary. Where that wasn't
possible in one pass (noted explicitly below), the citation is held out of
`principles/` until it is.

Source: [Catechism of the Catholic Church](https://www.vatican.va/archive/ENG0015/_INDEX.HTM)
(the Holy See's reference edition; individual paragraphs also linked below at
their stable `vatican.va/content/catechism/en/...` URLs).

## Structure (the parts relevant to this project)

- **Part Three: Life in Christ**
  - **Section One: Man's Vocation — Life in the Spirit**
    - Chapter One: The Dignity of the Human Person (1699-1876) — includes
      Article 8 "Sin" (1846-1876), where 1867 falls
    - Chapter Two: The Human Communion (1877-1948) — the common good,
      equality and differences among people, human solidarity
  - **Section Two: The Ten Commandments**
    - Fifth Commandment (2258-2330) — respect for human life, abortion,
      euthanasia
    - Seventh Commandment (2401-2463) — respect for persons and their
      goods, the Church's social doctrine, economic activity, justice and
      solidarity among nations, love for the poor

## Landed: the bright-line gate (2026-08-08)

| `non-negotiables.yaml` item | CCC / other citation | Verification |
|---|---|---|
| `direct-killing-of-the-innocent` (citation added, item pre-existing) | CCC §1867 ([Part Three, Section One, Chapter One, Article 8, §V "The Proliferation of Sin"](https://www.vatican.va/content/catechism/en/part_three/section_one/chapter_one/article_8/v_the_proliferation_of_sin.html)) — "the blood of Abel," first of the "sins that cry to heaven" | Verified directly against the cited page |
| `systemic-wage-theft-by-design` (new item) | CCC §1867, "injustice to the wage earner"; Evangelium Vitae [§3](https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_25031995_evangelium-vitae.html) (quoting *Gaudium et Spes* §27) — "disgraceful working conditions, where people are treated as mere instruments of gain rather than as free and responsible persons" | Both verified directly against the cited pages |
| `facilitation-of-trafficking-or-sexual-exploitation` (new item) | CCC §1867, "the sin of the Sodomites" (see note below); Evangelium Vitae §3 (quoting *Gaudium et Spes* §27) — "the selling of women and children," "prostitution" | Both verified directly against the cited pages |

**Note on "the sin of the Sodomites":** the Genesis 19 / Ezekiel 16:49-50
narrative tradition supports more than one reading — sexual sin, or (per
Ezekiel's own gloss) violent inhospitality and exploitation of the
vulnerable. Per project decision 2026-08-08, the `facilitation-of-trafficking-or-sexual-exploitation`
item is written to the reading both interpretations agree is gravely wrong
(trafficking, sexual exploitation, CSAM) rather than taking a position on
the contested part. This is the one item in `non-negotiables.yaml` without
a clean, uncontested translation into an AI-use bright line — flagged for
explicit attention once a named theological reviewer exists (see
`../CHECKLIST.md`).

**Not pursued as bright-line items:** CCC 1867 also names "the cry of the
oppressed in Egypt" and "the cry of the foreigner, the widow, and the
orphan." Unlike the items above, oppression of the poor or the stranger
admits of degree and mitigation — it doesn't have the gate's "the AI use
itself facilitates the act, full stop" shape. That material belongs in the
graded principles instead: see `preferential-option-for-the-poor.yaml`,
`social-justice.yaml`, `solidarity.yaml`, and (once written)
`../rubric/known-tensions.md`'s worked cases.

## Landed: CCC citations into the eight graded principles (2026-08-08)

Each range below was checked directly against its primary-source
`vatican.va/content/catechism/en/...` page (found via the Catechism's own
part/section/chapter/article URL structure — see each principle file's
`magisterial_citations` for the exact reference text and page-level
detail), not reconstructed from memory or a secondary summary.

| Principle | CCC range | Location |
|---|---|---|
| `personalism` | §1701-1709 | Part Three, §1, Ch. 1, Art. 1, "Man: The Image of God" |
| `common-good` | §1905-1912 | Part Three, §1, Ch. 2, Art. 2, §II "The Common Good" |
| `subsidiarity` | §1883-1885 | Part Three, §1, Ch. 2, Art. 1, "The Person and Society" |
| `solidarity` | §1939-1942 | Part Three, §1, Ch. 2, Art. 3, §III "Human Solidarity" |
| `universal-destination-of-goods` | §2402-2406 | Part Three, §2, Ch. 2, Art. 7, §I |
| `preferential-option-for-the-poor` | §2443-2449 | Part Three, §2, Ch. 2, Art. 7, §VI "Love for the Poor" |
| `dignity-and-inviolability-of-life` | §2258 (opening), §2270-2275 (abortion), §2276-2279 (euthanasia) | Part Three, §2, Ch. 2, Art. 5 |
| `social-justice` | §1928-1942 | Part Three, §1, Ch. 2, Art. 3, "Social Justice" (whole article; §III overlaps `solidarity`'s own citation — CCC nests solidarity inside social justice, unlike the Compendium/MH, which treat them as separate principles) |

Note: `social-justice` and `solidarity`'s CCC ranges overlap (1939-1942 is
both Article 3's closing subsection and solidarity's own citation). This is
a real structural fact about the Catechism, not a citation error — see each
file's `magisterial_citations` comment for how it's explained in place.

## Landed: USCCB foundational-documents list, Tier A (2026-08-08)

The USCCB's [foundational documents of Catholic Social Teaching](https://www.usccb.org/beliefs-and-teachings/what-we-believe/catholic-social-teaching/foundational-documents)
page lists 29 papal/Vatican documents and ~52 USCCB pastoral statements —
too many to cite with this project's citation-integrity discipline in one
pass. Curated into three tiers rather than attempted flat:

- **Tier A** (this section): one well-matched encyclical per principle,
  each paragraph checked against primary source.
- **Tier B**: USCCB pastoral statements, used to write new
  `../rubric/known-tensions.md` worked cases — landed, see below.
- **Tier C**: the remaining ~70 documents, catalogued but not cited or
  verified — see `usccb-foundational-documents-index.md`.

| Principle | Encyclical citation | Verification |
|---|---|---|
| `personalism` | Gaudium et Spes §22 | Verified directly against the primary text |
| `common-good` | Gaudium et Spes §26 | Verified directly against the primary text |
| `subsidiarity` | Quadragesimo Anno §79-80 | Verified directly against the primary text |
| `social-justice` | Quadragesimo Anno §57-58 | Verified directly against the primary text |
| `solidarity` | Sollicitudo Rei Socialis §38 | Verified directly against the primary text |
| `preferential-option-for-the-poor` | Sollicitudo Rei Socialis §42 | Verified directly against vatican.va's official text, via IntraText's paginated mirror — vatican.va's own single-page encyclical text was too long for a direct fetch to reach paragraph 42 |
| `universal-destination-of-goods` | Populorum Progressio §22-23 | Verified directly against the primary text |
| `dignity-and-inviolability-of-life` | Evangelium Vitae §57 | Verified 2026-08-08 directly against vatican.va's official text, via IntraText's paginated mirror (`ENG0594/_P27.HTM`) — vatican.va's own page was too long to reach §57 directly. Originally landed on secondary-source corroboration only; this entry updates that once the direct check succeeded, per the "Next" item this table used to carry. |

## Resolved: Compendium §302 (just wage)

Noted during Phase 1 (see `../CHANGELOG.md`'s wage-theft entry) as a
promising citation for `principles/non-negotiables.yaml`'s
`systemic-wage-theft-by-design` item, but left out at the time —
vatican.va's single-page Compendium text was too long for a direct fetch
to reach §300+. **Verified 2026-08-08** via a direct fetch of Catholic
Culture's chaptered mirror of the Compendium's official English text
(Chapter Six, "Human Work"): §301 grounds workers' rights in "the nature
of the human person and ... his transcendent dignity"; §302 states "they
commit grave injustice who refuse to pay a just wage or who do not give
it in due time and in proportion to the work done." Added to
`non-negotiables.yaml`'s `systemic-wage-theft-by-design` item.

## Landed: Tier B (2026-08-08, extended 2026-08-08)

`../rubric/known-tensions.md` now has five fully worked cases plus one
addendum, four of them grounded in USCCB pastoral statements or the CCC
beyond what Tier A already covers:

| Case | Grounding | Verification |
|---|---|---|
| 2. Immigration enforcement prioritization | CCC 2241; *Welcoming the Stranger Among Us* (2000) | CCC 2241 verified directly; USCCB statement verified directly |
| 3. Recidivism-risk scoring | *Responsibility, Rehabilitation, and Restoration* (2000) | Secondary-source corroborated (USCCB page blocked the direct fetch) |
| 3, addendum. Capital sentencing (sharper, less-contested instance) | CCC 2267; *A Culture of Life and the Penalty of Death* (2005) | CCC 2267 verified directly against vatican.va; the USCCB statement is secondary-source corroborated only — its primary PDF has no extractable text layer and no HTML mirror was found |
| 4. AI-driven workforce automation | *Economic Justice for All* (1986) | Verified directly, via a plain-text mirror (the USCCB's own PDF also has no extractable text layer) |
| 5. AI-generated voter guides | *Forming Consciences for Faithful Citizenship* (2015/2023) | Verified directly, via a diocesan PDF mirror that yielded an exact paragraph number (§34) |

See `../rubric/known-tensions.md` directly for full citations and
reasoning on each case; see `usccb-foundational-documents-index.md` for
what's still Tier C.

## Next

- Two items remain secondary-corroborated only (case 3's own
  *Responsibility, Rehabilitation, and Restoration* citation, and the
  capital-sentencing addendum's *A Culture of Life and the Penalty of
  Death* citation) — both blocked by non-text-extractable USCCB PDFs
  rather than page-length limits. Worth a follow-up if a working mirror
  turns up.
- Once a named theological reviewer is confirmed in `../CODEOWNERS`, all of
  the above needs their sign-off — verified paragraph numbers aren't the
  same as theological review.
