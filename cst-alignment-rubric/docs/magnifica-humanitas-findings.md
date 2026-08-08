# Magnifica Humanitas — findings

What came out of reading *Magnifica Humanitas* (Leo XIV, 15 May 2026, "On Safeguarding the Human Person in the Time of Artificial Intelligence") against this project's existing seven principles. Paragraph numbers were verified directly against the primary text.

Source: [Magnifica Humanitas](https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html).

## Structure (Chapter Two: "Foundations and Principles of the Social Doctrine of the Church")

- **Foundations** (§48-58): the human person as image of the Triune God (§48), equal dignity of all human beings (§51), the supreme value of human rights (§54-58, including the right to life "from conception to its natural end" at §55-56).
- **"The principles of Social Doctrine"** — MH's own heading lists exactly five: the common good (§59-64), the universal destination of goods (§65-67), subsidiarity (§68-72), solidarity (§73-76), and **social justice** (§77-81).
- **Integral human development** (§82-83+): a distinct section following the five principles, drawing on *Populorum Progressio*.

## Where this matches this project's seven, and where it doesn't

| This project's principle | MH's treatment |
|---|---|
| Common good, universal destination of goods, subsidiarity, solidarity | Each has its own "principle of..." heading in MH, matching the Compendium's structure closely |
| Personalism | MH never uses the term "personalist principle." It grounds the same claim — the person as starting point — under "the human person: image of the Triune God" (§48), as a *foundation* rather than one of the five listed principles. Not a contradiction, but a real terminology gap. |
| Dignity and inviolability of life | Also a *foundation* in MH (§51, §54-56), not one of the five listed principles — same structural pattern as personalism. |
| Preferential option for the poor | **Not its own heading in MH.** It's discussed at §78, inside the social justice section, as one expression of social justice — not a standalone principle the way the Compendium (§182, under universal destination of goods) and this project treat it. |

## New: social justice

MH names **"the principle of social justice"** (§77-81) as one of its five headline principles — something this project's current seven don't include by that name. Per §77-79: social justice is the capacity of a social, economic, and political order to let everyone — particularly the weakest — live a genuinely dignified life; it's what the preferential option for the poor gets folded into; and it explicitly includes structural injustice ("structures, mechanisms and economic and cultural systems that produce inequality almost automatically," §79), not just individual wrongdoing.

**Resolved 2026-08-07: added as an eighth principle**, `principles/social-justice.yaml`, cited to MH §77-81. The "seven principles" framing in this project's README, CHECKLIST, and Definition of Done has been updated to "eight" accordingly. `preferential-option-for-the-poor.yaml` now cross-references it rather than only noting the gap.

## AI-specific material worth having on hand

Two passages in MH speak to this project's subject matter more directly than anything in the Compendium, because MH addresses AI by name where the Compendium (2004) predates it:

- **§67** (universal destination of goods) names "patents, algorithms, digital platforms, technological infrastructure and data" explicitly as goods this principle covers — already folded into `principles/universal-destination-of-goods.yaml`.
- **§71** (subsidiarity) argues that in the digital era, the "highest level" subsidiarity has to reckon with isn't only the state, but the technology companies and platforms that hold de facto power over data and the conditions of everyday digital life — already folded into `principles/subsidiarity.yaml`.
- **Chapter Three** ("Technology and Dominance") — not yet mined for citations: covers the technocratic paradigm (§92, citing *Laudato Si'*) and a critique of transhumanism/posthumanism (§115). Neither is folded into a principle file yet.

## Decided: added as an eighth principle

2026-08-07 — `principles/social-justice.yaml` added, cited to MH §77-81 only (no distinct Compendium heading exists for it; see `compendium-citation-map.md`). This project's principle count moved from seven to eight; README, CHECKLIST, and Definition of Done were updated accordingly. `preferential-option-for-the-poor.yaml` now cross-references it as a tension/overlap rather than flagging it as a gap.

Not yet done: a pass through Chapter Three's technocratic-paradigm and transhumanism material above, to see whether it belongs as citations within existing principles or points to something not yet covered at all.
