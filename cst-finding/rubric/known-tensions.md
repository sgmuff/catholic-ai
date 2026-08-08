# Known tensions

**BETA — unreviewed.** Written during the `CODEOWNERS` sign-off pause (see
`../CONTRIBUTING.md` "Beta status"); no theological reviewer has signed off
on which cases below are genuinely contested versus just under-argued. Any
citation to a magisterial or USCCB source was checked against the primary
text before being written in here — see each case's citations.

The stress-test library: documented conflicts between principles, written
up honestly so future maintainers see this tool's limits instead of
discovering them the hard way. Per `../rubric/criteria.md`, Stage 2: when a
case here matches what an AI use or audited response is actually doing,
the graded principle involved gets `contested: true` in the assessment
rather than a number presented as settled — these cases exist to make that
judgment call recognizable, not to resolve it for good.

Five worked hard cases (plus a sharper, less-contested instance noted
under case 3) — at least three required per `../CHECKLIST.md`.

## 1. Preferential option for the poor vs. subsidiarity — the outreach-ranking case

**Principles in tension:** `preferential-option-for-the-poor`, `subsidiarity`
(see the `tensions` entries in both files, which point here).

**The case:** A diocese or agency uses an AI system to rank two households
for limited outreach capacity — a food pantry slot, a caseworker visit, a
one-time assistance grant. One household is a widow in documented,
visible financial crisis: the system's data shows exactly why she
qualifies. The other is a household that looks stable in the system's
data — steady income on file, no prior case history — but a local
caseworker happens to know they're secretly in crisis (a job loss last
week, a medical bill not yet reflected anywhere the system can see). The
system, working only from the data it has, ranks the widow first.

**Why this is genuinely contested, not just a case to score:**
Preferential option for the poor says priority goes to whoever has the
least power and the fewest resources to contest a bad decision (Compendium
§182; Sollicitudo Rei Socialis §42) — on the visible data, that's the
widow. Subsidiarity says a decision belongs at the most immediate, local
level capable of judging it well (Compendium §185; Quadragesimo Anno §79)
— and the caseworker, not the system, is that level here. These aren't a
correct answer and an incorrect one: the system optimizing purely for its
own visible data actively works against subsidiarity's claim that local,
embodied knowledge should carry weight the data doesn't capture, but
overriding the system on an unverified hunch every time risks reintroducing
exactly the arbitrariness a documented, auditable process was meant to fix.

**What the rubric should do:** Score both principles, but mark
`contested: true` rather than let a high subsidiarity score and a low
preferential-option score (or vice versa) average into a false sense that
one clearly outweighs the other. The concrete mitigation this case
actually points to isn't "pick one principle" — it's a process fix: give
the local caseworker a documented override path with a reason code, so the
system's ranking is a strong default, not a foreclosure of local
knowledge the data doesn't have.

**Citations:** Compendium of the Social Doctrine of the Church §182, §185;
Quadragesimo Anno §79 (Pius XI, 1931); Sollicitudo Rei Socialis §42 (John
Paul II, 1987).

## 2. Immigration enforcement prioritization — solidarity/dignity vs. common good/subsidiarity

**Principles in tension:** `solidarity`, `dignity-and-inviolability-of-life`
(or `personalism`, depending on how the system's function is described),
vs. `common-good`, `subsidiarity`.

**The case:** An AI system used by an immigration enforcement agency
scores or ranks noncitizens by "priority" for detention or removal
proceedings, based on factors like criminal history, length of
unauthorized presence, and family ties. A human officer makes the final
call in each case, but the system's ranking heavily shapes which cases get
attention and which don't.

**Why this is genuinely contested, not just a case to score:** The
Catechism states both halves of this tension in the same paragraph rather
than picking one: "the more prosperous nations are obliged, to the extent
they are able, to welcome the foreigner in search of the security and the
means of livelihood which he cannot find in his country of origin," and in
the very next sentence, "political authorities, for the sake of the common
good for which they are responsible, may make the exercise of the right to
immigrate subject to various juridical conditions" (CCC 2241). Solidarity
(Compendium §192; Sollicitudo Rei Socialis §38) and the USCCB's own
pastoral teaching — *Welcoming the Stranger Among Us: Unity in Diversity*
(2000) calls the faithful to be "traveling companions" to migrants "in
trouble" — pull toward treating a person facing removal as someone owed
solidarity, not a case to be triaged for processing efficiency. Common
good and subsidiarity pull the other way: a nation's political authorities
have a real, CCC-recognized responsibility to regulate immigration, and an
enforcement agency ranking cases for limited resources is, in itself, a
legitimate exercise of that responsibility, not obviously a violation of
anything. Neither side of CCC 2241 cancels the other.

**What the rubric should do:** Score `dignity-and-inviolability-of-life`
(or `personalism`) and `common-good` (or `subsidiarity`) with
`contested: true`, not as a violation on one side and a pass on the other.
The specific thing this rubric can still say without resolving the
underlying policy question: whatever the ranking criteria are, a human
being on the losing end of the ranking is still owed the dignity
protections `personalism` and `dignity-and-inviolability-of-life`
describe elsewhere — a low-confidence or borderline score should not, by
itself, remove the requirement for individualized human review before an
adverse action is taken, the same requirement `dignity-and-inviolability-of-life.yaml`'s
"predictive risk scores feeding directly into safety decisions" scenario
already names for a different context.

**Citations:** Catechism of the Catholic Church §2241; Compendium of the
Social Doctrine of the Church §192; Sollicitudo Rei Socialis §38 (John
Paul II, 1987); USCCB, *Welcoming the Stranger Among Us: Unity in
Diversity* (2000).

## 3. Recidivism-risk scoring in sentencing or parole — common good vs. dignity and preferential option for the poor

**Principles in tension:** `common-good`, vs. `dignity-and-inviolability-of-life`
and `preferential-option-for-the-poor`.

**The case:** A criminal-justice system uses an AI-generated recidivism
risk score as an input to a sentencing or parole decision — a judge or
parole board sees the score and can depart from it, but in practice tends
to follow it. The score is built from factors correlated with, but not
identical to, race and poverty (prior arrests in over-policed
neighborhoods, employment history, zip code), a well-documented pattern in
real deployed tools of this kind.

**Why this is genuinely contested, not just a case to score:** The
USCCB's *Responsibility, Rehabilitation, and Restoration: A Catholic
Perspective on Crime and Criminal Justice* (2000) names three legitimate
purposes of punishment together, not in tension by the bishops' own
account: "the preservation and protection of the common good of society,"
"the restoration of public order," and "the restoration or conversion of
the offender." A risk score genuinely can serve the first two —
common-good has a real claim here, and public safety is not a lesser
value this rubric should wave away. But `dignity-and-inviolability-of-life`
already establishes that this rubric "refuses trade-off logic at the point
where a system's decision could bear on someone's life or basic safety,"
and a sentence or parole outcome is exactly that point; `preferential-option-for-the-poor`
adds that when a score's inputs are structurally correlated with poverty,
the people most likely to be harmed by an inflated score are the ones with
the least power to contest it. Neither the common-good claim nor the
dignity/preferential-option claim is obviously the trump card — the
factors driving accuracy are close to the same factors that make an error
fall hardest on the already-disadvantaged.

**What the rubric should do:** Score `common-good` and
`dignity-and-inviolability-of-life` (and, where the case turns on
disparate impact specifically, `preferential-option-for-the-poor`) with
`contested: true`. This is also a good instance of `social-justice.yaml`'s
own claim: the defect a low `dignity-and-inviolability-of-life` or
`preferential-option-for-the-poor` score would point to here isn't any
individual official's bad intent, it's a structural pattern in what the
score was trained to correlate with — the fix this case actually points
to is disclosure of what the score weighs, a meaningful human-override
path with a documented reason, and disparate-impact testing before
deployment, not simply "use it less."

**Citations:** USCCB, *Responsibility, Rehabilitation, and Restoration: A
Catholic Perspective on Crime and Criminal Justice* (2000); see also
`dignity-and-inviolability-of-life.yaml`'s "predictive risk scores feeding
directly into safety decisions" scenario and `social-justice.yaml`'s
description, both directly relevant to this case.

**Sharper instance, not equally contested: capital sentencing.** If the
same kind of risk score — "future dangerousness," recidivism likelihood —
is used as an input to a *capital* sentencing decision specifically (a
real, documented practice in U.S. death-penalty jurisdictions), the
common-good side of this case's tension is substantially weaker than the
base case above, not just a more extreme version of the same balance. CCC
2267 (revised 2018) now teaches plainly that "the death penalty is
inadmissible because it is an attack on the inviolability and dignity of
the person," specifically because "more effective systems of detention
have been developed, which ensure the due protection of citizens" without
resort to execution — meaning the common-good/public-safety claim this
case's base version treats as real and substantial is, in this specific
instance, a claim current Church teaching says modern detention already
satisfies without needing the death penalty at all. The USCCB's own *A
Culture of Life and the Penalty of Death* (2005) draws the same
conclusion in pastoral terms: "no matter how heinous the crime, if
society can protect itself without ending a human life, it should do
so," urging the country to "reject the tragic illusion that we can
demonstrate respect for life by taking life." An assessment of this
specific instance should still score `dignity-and-inviolability-of-life`
and note the tension explicitly, but should not mark it `contested: true`
on the same footing as the base case — current teaching has substantially
resolved which claim wins here, even though the underlying
risk-scoring-in-sentencing pattern is the same one this case's base
version treats as genuinely undecided.

**Additional citations for the capital-sentencing instance:** Catechism
of the Catholic Church §2267; USCCB, *A Culture of Life and the Penalty
of Death* (2005) (secondary-source corroborated rather than directly
fetched from its primary USCCB source, which is PDF-only with no
extractable text layer — see `../docs/ccc-citation-map.md`).

## 4. AI-driven workforce automation — common good/universal destination of goods vs. personalism/preferential option for the poor

**Principles in tension:** `common-good`, `universal-destination-of-goods`,
vs. `personalism`, `preferential-option-for-the-poor`.

**The case:** A company uses an AI system to identify which job categories
or specific roles to automate away, optimized for cost reduction and
productivity gains. The system's recommendation doesn't account for
whether displaced workers can find comparable work, only for the
efficiency gain to the business. Leadership treats the system's output as
a straightforward business input, the same way it would treat a
cost-of-materials forecast.

**Why this is genuinely contested, not just a case to score:** Technology
replacing labor is not new to CST, and the tradition doesn't treat
automation itself as a violation — the `universal-destination-of-goods`
and `common-good` principles both recognize real value in productive
efficiency that benefits the whole of society, not just a company's
owners: lower costs, freed-up capital, goods and services more widely
available. But the USCCB's *Economic Justice for All* (1986) insists that
"every perspective on economic life that is human, moral, and Christian
must be shaped by three questions: What does the economy do *for* people?
What does it do *to* people? And how do people *participate* in it?" — a
framework that makes a purely productivity-optimized automation decision
incomplete on its own terms, not just harsh. The same letter states "all
people have a right to participate in the economic life of society"
(§15) and "a right to earn a living, which for most people in our economy
is through remunerative employment" (§80) — rights `personalism` and
`preferential-option-for-the-poor` take as a real claim on a decision like
this, not a sentiment to note and move past. Neither side is simply
wrong: a business restrained from ever automating anything isn't what CST
asks for either, and `preferential-option-for-the-poor`'s own file already
notes this principle doesn't have a second "impossible to fix" gate
beyond Stage 1 — a legitimate efficiency gain doesn't stop being one just
because it has a real human cost.

**What the rubric should do:** Score `common-good`/`universal-destination-of-goods`
and `personalism`/`preferential-option-for-the-poor` with `contested: true`
rather than let a business-efficiency framing quietly settle the question
in the common good's favor by default, which is the failure mode this
case is written to catch. The concrete mitigation this case points to
isn't "don't automate" — it's whether the decision process actually asked
Economic Justice for All's three questions before optimizing for the
first one alone: transition support, retraining investment, or a
phase-in timeline are all ways a genuinely contested case can still be
mitigated rather than just flagged.

**Citations:** USCCB, *Economic Justice for All: Catholic Social Teaching
and the U.S. Economy* (1986), Ch. I (the "three questions" framing), §15,
§80.

## 5. AI-generated voter guides and candidate-scoring tools — common good vs. personalism (and subsidiarity)

**Principles in tension:** `common-good`, vs. `personalism` (with a
secondary connection to `subsidiarity`).

**The case:** An organization builds an AI tool that ingests candidates'
public statements, voting records, and platforms, and outputs a single
score or ranked list meant to tell a time-pressed voter which candidate
"best aligns with Catholic values." The tool is transparent about its
methodology and covers a broad range of issues, not just one.

**Why this is genuinely contested, not just a case to score:** The
USCCB's *Forming Consciences for Faithful Citizenship* states plainly
that conscience "is not something that allows us to justify doing
whatever we want, nor is it a mere 'feeling'... [it] always requires
serious attempts to make sound moral judgments" (§34), and separately
that political choices require "the exercise of a well-formed conscience
aided by prudence" — a personal, formed judgment, not a lookup. `common-good`
has a real claim on the other side: broad, organized, multi-issue
information genuinely can help a voter form a *better* conscience than
they would starting from nothing, and FCFC itself exists to inform
consciences, not to leave people uninstructed. The sharper problem this
case raises isn't that scoring candidates is inherently wrong, but that a
single output number risks doing exactly what FCFC separately warns
against: "devotion to a single isolated aspect of the Church's social
doctrine does not exhaust one's responsibility toward the common good" —
a collapsed score can look like comprehensive moral guidance while
actually performing the single-issue reduction the bishops name as a
distinct failure mode, even when its inputs cover many issues, if the
weighting collapses them into one number a voter is meant to defer to
rather than reason through. `subsidiarity` echoes the same worry from a
different angle: conscience formation is supposed to happen at the most
personal level there is, and a tool that outputs a ready-made verdict
does the local, personal work of prudence *for* the voter rather than
equipping them to do it.

**What the rubric should do:** Score `common-good` and `personalism` with
`contested: true` rather than treat "more information, more efficiently
delivered" as an automatic good. The mitigation this case points to is
specific: present the underlying facts and how they map to Catholic
teaching without collapsing to a single output number or ranked verdict,
and make the tool's own weighting and omissions as visible as its
conclusions — the difference between a tool that equips conscience and
one that substitutes for it is usually exactly there.

**Citations:** USCCB, *Forming Consciences for Faithful Citizenship: A
Call to Political Responsibility from the Catholic Bishops of the United
States* (2015, with 2023 introductory note), §34 and surrounding
material on prudential judgment and single-issue reduction.
