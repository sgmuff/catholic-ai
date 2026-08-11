# AI-governance rubric

Seven dimensions, scored independently, for every AI system this skill
assesses. Framework-agnostic on purpose, the same discipline as the privacy
rubric: it defines *what* to evaluate in terms any responsible-AI practice
would recognize, not in one law's vocabulary. Which framework's exact
citation and terms of art back up a given score is decided at assessment
time, from whatever is `active` in `frameworks/index.yaml` — read those
files fresh for each assessment rather than citing anything from memory or
from this document.

This rubric assumes the system's EU AI Act risk tier has already been
determined as part of intake (prohibited, high-risk, limited-risk, or
minimal-risk) — that determination and its basis belong in the `compliance`
section directly, as the specific regulatory finding it is, not as a
separate structured field. The seven dimensions below score how well the
system's actual governance practices meet what its tier requires, not
whether the tier itself was assigned correctly — a wrong tier assignment is
itself a compliance finding, stated plainly in `compliance` before any
dimension gets scored.

## How to score

- **Scale: 1-5.** 1 = clearly fails this dimension; 5 = clearly upholds it.
  Each dimension below gives anchors at 5, 3, and 1 — interpolate 2 and 4
  rather than treating the scale as five hard categories.
- **Passing threshold: 4.** A score of 3 or below requires a **mitigation**:
  a specific change to the system or its governance itself, not a promise
  to "be more careful" or a request for information that should already
  have been gathered at intake.
- **Every dimension gets an `ideal`, regardless of score.** A mitigation is
  the floor that makes a low score acceptable; `ideal` describes fuller
  conformity beyond that floor — what this dimension would look like at its
  best for this specific system, not a generic aspiration.
- **Mark `contested: true`** when two dimensions genuinely pull against each
  other for this system (e.g. a transparency obligation against a
  trade-secret or security concern about disclosing model internals) rather
  than one simply scoring low. State the tension in the rationale instead
  of averaging it away — this is a signal for human judgment, not something
  the rubric resolves for you.
- **Score what the system actually does**, not what a better version of it
  would do. A mitigation describes the gap; it isn't credited until it's
  actually adopted.
- **Calibrate to the system's actual tier.** A minimal-risk system scoring
  well on `governance-and-accountability` doesn't need the same
  documentation depth a high-risk system does — score against what's
  proportionate to the tier, not a single fixed bar applied uniformly
  regardless of risk.

## 1. Risk classification — `risk-classification`

Whether the system's risk tier was determined honestly and specifically —
matched against the actual Annex III categories or prohibited-practice
list, not assumed, and not minimized to avoid the obligations a higher tier
would trigger.

*Why it matters beyond the law:* an institution that quietly classifies its
own system as lower-risk than the facts support isn't managing risk, it's
managing exposure to the rules that manage risk — and the people the system
actually affects bear the difference.

- **5:** The tier was determined by checking the system's actual function
  against the specific categories in the framework, with the reasoning
  documented, not asserted.
- **3:** A tier was assigned, but the reasoning is thin or the system sits
  close enough to a higher-tier category that the classification deserves a
  second look.
- **1:** No tier determination was made, or the system was classified lower
  than its actual function supports.

## 2. Governance and accountability — `governance-and-accountability`

Whether a named, accountable structure exists for this system's risk
management across its lifecycle — not a policy document, a person or team
with actual authority to change the system, halt its use, or escalate a
concern.

*Why it matters beyond the law:* a risk management process without an
owner is a description of what should happen, not something that actually
governs anything. Subsidiarity applied to AI governance means the person
closest to the system's actual operation has real standing to act, not
just to report upward.

- **5:** A named owner or team is accountable for this system's risk
  management throughout its lifecycle, with the authority to halt or
  modify its use, and a defined escalation path that has actually been
  used.
- **3:** Accountability is assigned on paper, but the owner lacks the
  authority to act on a finding, or the escalation path has never been
  exercised even when warranted.
- **1:** No one is specifically accountable for this system's ongoing risk
  management.

## 3. Data governance — `data-governance`

Whether the data used to train, validate, test, or operate this system is
subject to quality, relevance, and bias-mitigation practices proportionate
to its risk tier.

*Why it matters beyond the law:* a system is only as trustworthy as what it
learned from or operates on — data governance is where a downstream harm
(a biased outcome, an unreliable prediction) is most cheaply caught, before
it reaches a person the system affects.

- **5:** Training, validation, and operational data are examined for
  relevance, representativeness, and known bias risks, with specific
  mitigation applied where gaps are found.
- **3:** Some data-quality practice exists, but bias examination is
  informal or hasn't been applied to this system specifically.
- **1:** No documented data-governance practice covers this system's data.

## 4. Transparency and documentation — `transparency-and-documentation`

Whether the system's technical documentation and the information given to
whoever deploys, operates, or is subject to it, is adequate for its risk
tier — including, where applicable, disclosure that a person is interacting
with an AI system or AI-generated content at all.

*Why it matters beyond the law:* a person is owed the chance to understand
what's making a decision that affects them, or that they're looking at
something a machine produced — transparency is what makes every other
protection in this rubric something a person can actually invoke.

- **5:** Technical documentation describes the system's design, intended
  purpose, and known limitations; anyone who deploys it or is subject to
  it receives clear, timely disclosure appropriate to the tier.
- **3:** Documentation exists but is incomplete or stale, or disclosure to
  affected individuals is inconsistent.
- **1:** No meaningful technical documentation exists, or a person
  interacting with the system has no way to know an AI system is involved.

## 5. Accuracy, robustness, and security — `accuracy-robustness-security`

Whether the system's accuracy has been tested, its behavior is robust to
the inputs it will actually encounter, and it's protected against
manipulation, unauthorized access, or the specific failure modes an AI
system introduces (e.g. data poisoning, adversarial inputs).

*Why it matters beyond the law:* a system deployed on a promise of
accuracy it hasn't actually demonstrated externalizes that risk onto
whoever relies on its output.

- **5:** Accuracy and robustness are tested against realistic conditions
  before deployment and monitored afterward, with security controls
  addressing AI-specific attack surfaces.
- **3:** Some testing occurred, but not against realistic deployment
  conditions, or ongoing monitoring after deployment doesn't exist.
- **1:** No accuracy or robustness testing has been done, or a known
  security gap has gone unaddressed.

## 6. Bias and fairness — `bias-and-fairness`

Whether the system has been evaluated for disparate impact or unfair bias
against people it's likely to affect differently, with mitigation applied
where a real gap is found — not assumed away because the system doesn't
use a protected characteristic as an explicit input.

*Why it matters beyond the law:* a system can produce a discriminatory
outcome without ever seeing the characteristic that outcome tracks —
solidarity asks whether the institution went looking for that possibility,
not just whether it avoided the obvious version of it.

- **5:** The system has been tested for disparate outcomes across groups
  it's likely to affect differently, with a defined process for
  mitigating a finding.
- **3:** Fairness was considered in general terms during design, but no
  specific testing for disparate impact has been done on this system.
- **1:** No fairness or bias evaluation has been done at all.

## 7. Human oversight — `human-oversight`

Whether a qualified person can meaningfully understand this system's
output, monitor its operation, and intervene — including stopping or
overriding it — appropriate to its risk tier and the significance of what
it decides or recommends.

*Why it matters beyond the law:* this is where the primacy of human
judgment over automated determination is most directly at stake — a person
affected by this system is owed a decision made, reviewed, or correctable
by someone who can be held accountable for it, not one that simply issues
from a system no one is positioned to question.

- **5:** A named, qualified person can understand the system's output well
  enough to catch a wrong or harmful result, has real authority to
  intervene, and does so often enough to show the oversight is real.
- **3:** An oversight role exists but is a rubber stamp in practice, or the
  person filling it lacks the information or standing to actually
  intervene.
- **1:** No person meaningfully oversees this system's operation, or none
  is positioned to intervene when its output is wrong.
