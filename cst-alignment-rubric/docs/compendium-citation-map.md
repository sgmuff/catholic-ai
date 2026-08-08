# Compendium of the Social Doctrine of the Church — citation map

A reference for whoever fills in `principles/*.yaml`'s `magisterial_citations` — not itself a citation. Paragraph numbers below were verified directly against the primary text (superseding an earlier version of this table drawn from an AI-summarized read of the page, which had the wrong numbers — a live example of why `../CONTRIBUTING.md`'s citation-integrity rule insists on checking the primary source).

Source: [Compendium of the Social Doctrine of the Church](https://www.vatican.va/roman_curia/pontifical_councils/justpeace/documents/rc_pc_justpeace_doc_20060526_compendio-dott-soc_en.html) (Pontifical Council for Justice and Peace, 2004/2006).

## Structure

- Part One (Ch. 1–4): foundational theology
- Part Two (Ch. 5–11): application to specific sectors
- Part Three (Ch. 12): ecclesial implementation

## Mapping to this project's eight principles

| Principle (`principles/*.yaml` id) | Compendium location | Notes |
|---|---|---|
| `personalism` | Ch. 3, §I "Social Doctrine and the Personalist Principle," §105-107 | §108 covers the person as *imago Dei*, immediately following |
| `common-good` | Ch. 4, §II "The Principle of the Common Good," §164-170 | |
| `subsidiarity` | Ch. 4, §IV "The Principle of Subsidiarity," §185-188 | §189 begins a separate "Participation" section |
| `solidarity` | Ch. 4, §VI "The Principle of Solidarity," §192-196 | |
| `universal-destination-of-goods` | Ch. 4, §III "The Universal Destination of Goods," §171 (origin/meaning), §176-178 (private property) | |
| `preferential-option-for-the-poor` | Within Ch. 4, §III.c, §182 | Not its own section — a subsection of universal destination of goods |
| `dignity-and-inviolability-of-life` | §108 (*imago Dei*); §155 (Ch. 3, §IV, right to life "from conception to its natural end") | |
| `social-justice` | Not covered by a distinct heading in the Compendium | Sourced from *Magnifica Humanitas* only — see `magnifica-humanitas-findings.md` |

## Non-negotiables (bright-line gate, not a graded principle)

`principles/non-negotiables.yaml` isn't one of the eight above — it's checked
first, before any of them get scored (see `../rubric/criteria.md`, Stage 1).

| Item (`non-negotiables.yaml` item id) | Compendium location | Magnifica Humanitas location |
|---|---|---|
| `direct-abortion`, `euthanasia-or-assisted-suicide`, `direct-killing-of-the-innocent` | Ch. 3, §II, §155 — "the illicitness of every form of procured abortion and of euthanasia," within the right-to-life discussion | §55 (Ch. 2, within "The supreme value of human rights") — names "induced abortion, killing of the innocent and euthanasia" explicitly as denials of the right to life the Church considers gravely wrong |

## Next step

Once a named theological reviewer is confirmed in `../CODEOWNERS`, these citations need their sign-off — verified paragraph numbers aren't the same as theological review.
