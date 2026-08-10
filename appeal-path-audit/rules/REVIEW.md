# Rule corpus review

Not a legal opinion. This is a non-expert technical read of `rules/*.yaml`
against the cited statutes, prepared to make an actual legal review faster —
not to substitute for one. Every open question below needs to be closed by
someone with GDPR/EU AI Act expertise before the corpus can be considered
reviewed (see the repo README's Definition of Done). Confidence is noted
per item; low-confidence claims are flagged as things to verify against the
statutory text directly, not asserted as fact.

## GDPR Art. 22(3)

### `gdpr-art22-automation-disclosure`
**Claim:** notice must disclose the decision was automated.
**Read:** likely mis-cited. Art. 22(3) itself is about safeguards (human
intervention, expressing a viewpoint, contesting the decision) — the
obligation to *disclose that automated processing occurred* comes from
Art. 13(2)(f) / 14(2)(g) (information to be provided at collection) and
Art. 15(1)(h) (right of access), not Art. 22(3).
**Open question:** should `framework` be corrected to cite 13(2)(f)/14(2)(g)
instead of / in addition to 22(3)? (Confidence: medium — the general
structure of Arts. 13–15 vs. 22 is well established; worth confirming
against current consolidated text.)

### `gdpr-art22-human-review-right`
**Claim:** notice must state the right to human intervention and to
contest the decision.
**Read:** matches the statutory text well — Art. 22(3) grants "at least"
human intervention, expressing a point of view, and contesting the
decision, as three distinct entitlements.
**Open question:** the check passes if *any one* of the four listed
phrases is present — it doesn't verify all three statutory entitlements
(intervention, express viewpoint, contest) are actually communicated, only
that review-type language appears somewhere. Is a single generic phrase
sufficient, or should this become three separate rules, one per
entitlement? (Confidence: high that the statute lists three distinct
rights; open question is a design choice, not a citation error.)

### `gdpr-art22-contact-method`
**Claim:** notice must give a specific way to exercise the right.
**Read:** not drawn from Art. 22(3)'s text directly — it's a reasonable
inference (an undisclosed right isn't actionable) rather than a literal
requirement of the article.
**Open question:** should `framework` be relabeled e.g. "GDPR Art. 22(3),
implied" to distinguish inferred good-practice rules from directly-cited
ones, so a reader doesn't assume every rule here is a quoted requirement?

### `gdpr-art22-not-final-language`
**Claim:** notice must not describe the decision as final/unappealable.
**Read:** same as above — a sound anti-pattern check, not literal
statutory text. Same relabeling question applies.

## EU AI Act, human-oversight obligations for high-risk systems

The `framework` label across all three rules in this file is vague enough
to cover several distinct obligations that live in different articles.
Worth splitting out before review rather than leaving as one bucket.

### `eu-ai-act-system-identification`
**Claim:** notice must identify that an AI system was involved.
**Read:** the more precise anchor for an *individual's* notice/explanation
right is likely Art. 86 (right to explanation of individual
decision-making) for Annex III high-risk systems, which is distinct from
Art. 14 (human oversight — a deployer-side capability requirement, not
itself a notice-to-the-individual obligation).
**Open question:** confirm Art. 86 is the correct citation and that this
project's target systems (credit, employment) fall under the Annex III
categories Art. 86 covers. (Confidence: low-medium — EU AI Act article
numbering has shifted across drafts/trilogue and is easy to misremember;
verify against the current consolidated text rather than trusting this.)

### `eu-ai-act-timeframe-given`
**Claim:** notice must give a timeframe within which *the individual* can
request a review.
**Read:** possible direction error. My recollection is that any ~30-day
figure in the Act's explanation-right provisions concerns the *deployer's*
deadline to respond to a request, not a deadline imposed on the individual
to make one. If that's right, this rule is checking for the wrong thing —
a notice that never mentions a request deadline (because there isn't one)
could correctly omit the phrases this rule requires, and the rule would
wrongly fail it.
**Open question:** verify against Art. 86 text directly — does it impose
any individual-side deadline at all, or only a deployer-side response
deadline? If only the latter, this rule needs to be rewritten to check for
disclosure of the *response* timeframe, not a request deadline.
(Confidence: low — flagged for verification, not asserted.)

### `eu-ai-act-no-sole-authority-claim`
**Claim:** notice must not claim the system's output is binding/authoritative
on its own.
**Read:** consistent with the general purpose of Art. 14 (human oversight
must be genuine, not nominal), but not itself quoted statutory language —
an inferred anti-pattern check, same category as the two GDPR anti-pattern
rules above.
**Open question:** same relabeling question — distinguish this from a
directly-cited requirement.

## Cross-cutting issues (not per-rule)

- **Citation granularity.** Every rule currently cites either "GDPR Art.
  22(3)" or the same one EU AI Act description string. Splitting rules by
  their actual source article (13/14/15/22 for GDPR; 14/86 for the AI Act)
  would make it possible to audit citation accuracy per rule instead of in
  bulk, and would make future rule additions self-documenting.
- **"Directly required" vs. "inferred good practice."** Several rules here
  encode sound practice (a contact method, no false-finality language) that
  isn't literal statutory text. Worth a `basis: statutory | inferred` field
  on each rule so a reader — or an auditee pushing back on a finding — can
  tell the difference at a glance.
- **Multi-jurisdiction scope.** The corpus only covers EU frameworks. The
  README's audience (lending, hiring, benefits, insurance) is broader than
  the EU; a US-facing organization would need an equivalent for e.g. ECOA/
  Reg B adverse-action notice requirements. Out of scope for this review
  pass, but worth noting as a known gap rather than a silent one.
