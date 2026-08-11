# Privacy-by-design rubric

Seven dimensions, scored independently, for every processing activity a DPIA
covers. This rubric is framework-agnostic on purpose: it defines *what* to
evaluate in terms any privacy-by-design discipline would recognize, not in one
law's vocabulary. Which framework's exact citation and terms of art back up a
given score is decided at assessment time, from whatever is `active` in
`frameworks/index.yaml` — read those files fresh for each assessment rather
than citing anything from memory or from this document.

## How to score

- **Scale: 1-5.** 1 = clearly fails this dimension; 5 = clearly upholds it.
  Each dimension below gives anchors at 5, 3, and 1 — interpolate 2 and 4
  rather than treating the scale as five hard categories.
- **Passing threshold: 4.** A score of 3 or below requires a **mitigation**: a
  specific change to the processing activity itself that would raise the
  score, not a promise to "be more careful" or a request for information that
  should already have been gathered at intake.
- **Every dimension gets an `ideal`, regardless of score.** A mitigation is
  the floor that makes a low score acceptable; `ideal` describes fuller
  conformity beyond that floor — what this dimension would look like at its
  best for this specific activity, not a generic aspiration.
- **Mark `contested: true`** when two dimensions genuinely pull against each
  other for this activity (e.g. minimization vs. a retention period a fraud
  or safety control actually needs) rather than one simply scoring low. State
  the tension in the rationale instead of averaging it away — this is a
  signal for human judgment, not something the rubric resolves for you.
  `rubric/known-tensions.md` (once authored) will hold worked cases; until
  then, reason each contested case from its own facts.
- **Score what the activity actually does**, not what a better version of it
  would do. A mitigation describes the gap; it isn't credited until it's
  actually adopted.

## 1. Necessity and proportionality — `necessity-and-proportionality`

Whether the processing is genuinely necessary to achieve its stated purpose,
and no more than proportionate to it. A processing activity can be lawful and
still fail this dimension if the same purpose is achievable with less.

*Why it matters beyond the law:* a person is never merely a means to an
institution's convenience. Treating "might be useful" as sufficient
justification for collecting or processing someone's data collapses the
distinction between what an institution needs from a person and what it
merely wants — the same distinction personalism draws between engaging
someone as a subject and using them as a resource.

- **5:** The processing is the least invasive means available to a clearly
  stated, legitimate purpose, and a less invasive alternative was actually
  considered and rejected for a stated reason.
- **3:** The processing achieves its purpose, but a materially less invasive
  alternative appears available and wasn't considered.
- **1:** The stated purpose is vague, or the processing's scope has no
  evident limit tied to any specific purpose ("might be useful later").

## 2. Data minimization — `data-minimization`

Whether only the data actually needed for the stated purpose is collected or
processed — a narrower question than necessity: necessity asks whether the
*processing* is justified; minimization asks whether every *field and
record* within it is.

*Why it matters beyond the law:* subsidiarity, applied to data, means a
person's information stays as close to them and as untouched by
institutional reach as the purpose allows. Every field collected "just in
case" is a small transfer of control away from the person it describes.

- **5:** Every data element collected maps to a specific, stated use; fields
  that would be convenient but aren't required are explicitly excluded.
- **3:** Most data collected is necessary, but at least one field or record
  type has no clear tie to the stated purpose.
- **1:** Collection is broader than the purpose by design (a form, intake
  process, or system field set copied from elsewhere without review), or new
  fields get added without asking whether they're needed.

## 3. Lawful basis and consent — `lawful-basis-and-consent`

Whether the activity has an identifiable legal basis for processing, and,
where consent is the basis (or is otherwise required — e.g. for a minor, or
for special-category data), whether that consent is genuinely informed,
specific, and freely given rather than assumed, bundled, or buried.

*Why it matters beyond the law:* consent done honestly is subsidiarity in its
most direct form — the decision about whether an institution may act on a
person's data staying with that person, not presumed on their behalf.
Personalism adds the sharper edge: consent obtained through a dark pattern or
a coerced bundle isn't really consent, whatever a checkbox claims.

- **5:** A specific lawful basis is identified and fits the actual
  processing; where consent applies, it's a clear, freely given, specific,
  and revocable choice, separate from any bundled agreement to unrelated
  terms.
- **3:** A lawful basis is identified, but it's a poor fit for what's
  actually being done (e.g. "legitimate interest" claimed for something that
  needs explicit consent), or consent is technically present but not clearly
  separable from other agreements.
- **1:** No identifiable lawful basis, or consent is assumed, pre-checked, or
  effectively required to access something unrelated to what's being
  consented to.

## 4. Retention — `retention`

Whether the activity defines how long the data it generates is kept, ties
that period to a real operational or legal need, and actually enforces
deletion or anonymization once that period ends.

*Why it matters beyond the law:* data that outlives its purpose is a
liability that accrues silently and falls hardest on people least able to
contest it later — an old record surfacing in a breach years after anyone
remembers why it was kept is not a hypothetical. Keeping retention honest is
solidarity practiced administratively, not just declared.

- **5:** A specific, justified retention period is defined and enforced by an
  actual mechanism (scheduled deletion, anonymization job, expiry field) —
  not a policy statement with no corresponding process.
- **3:** A retention period is defined but not automatically enforced, or the
  period is justified by convenience ("we keep everything indefinitely in
  case we need it") rather than a stated need.
- **1:** No retention period is defined, or data is kept indefinitely by
  default with no plan to review or delete it.

## 5. Security controls — `security-controls`

Whether the technical and organizational measures protecting this data are
proportionate to its sensitivity and the harm a breach would cause — access
controls, encryption where warranted, and a defined incident-response path.

*Why it matters beyond the law:* the common good is not served by treating
security as a cost center to minimize; a breach's cost is paid disproportionately
by the people whose data it exposes, not by the institution that under-invested
in protecting it.

- **5:** Access is limited to those who need it for the stated purpose,
  sensitive fields are protected proportionately to their sensitivity, and an
  incident-response path exists and is known to the people who'd use it.
- **3:** Baseline controls exist, but access is broader than necessary, or a
  specific known gap hasn't been addressed (e.g. a sensitive field stored
  without the protection its category warrants).
- **1:** No defined access control for this data, or a known gap has gone
  unaddressed with no plan to close it.

## 6. Third-party sharing — `third-party-sharing`

Whether any disclosure of this data to a vendor, partner, or other
institution is necessary for the stated purpose, is governed by an actual
contractual safeguard, and is disclosed to the people the data is about.

*Why it matters beyond the law:* each hop a person's data takes away from the
relationship that generated it is a hop further from their ability to know
about it, question it, or have it corrected — the same subsidiarity concern
as minimization, extended across an institutional boundary rather than a
database schema.

- **5:** Sharing is necessary for the stated purpose, governed by a contract
  with real data-protection terms (not a boilerplate reference), and
  disclosed to the people affected.
- **3:** Sharing is necessary and contractually governed, but not clearly
  disclosed to the people it concerns.
- **1:** Data is shared with a third party with no contractual data-
  protection terms in place, or sharing goes beyond what the stated purpose
  requires.

## 7. Human oversight of automated decisions — `human-oversight`

Whether any automated or AI-assisted step in this activity that produces a
decision or recommendation about a specific person has a real human check on
it: a review before the decision is acted on wherever that's actually
possible (a loan decision, a triage suggestion), or, for a real-time system
where the decision and the action are the same instant (a biometric lock, an
automated fraud block), a genuinely accessible human fallback the person can
reach immediately after — not a human who could theoretically intervene, but
one who actually does, on a defined basis, with the authority and
information to change the outcome or reverse its effect.

*Why it matters beyond the law:* this is where the primacy of human judgment
over automated determination is most directly at stake — a person is owed a
decision made, reviewed, or correctable by someone who can be held
accountable for it, not one that simply issues from a system no one is
positioned to question. A review step that exists on paper but never
actually changes an outcome does not satisfy this dimension, and neither
does an emergency fallback that exists on paper but isn't actually staffed
or reachable when it's needed.

- **5:** For a system with a review point before acting, a named human
  reviews the output, has the authority and information to change it, and
  does so often enough to show the review is real. For a real-time system
  that acts and decides in the same instant, a human fallback is always
  reachable and empowered to reverse the effect promptly.
- **3:** A review step or fallback exists but is a rubber stamp or a fiction
  in practice (no case has ever been overturned, the reviewer lacks the
  standing to actually change the outcome, or the fallback is nominally
  available but slow, unstaffed, or hard to reach when actually needed).
- **1:** No human reviews the automated output before it affects a person and
  no working fallback exists after, for a decision with a legal or similarly
  significant effect.
