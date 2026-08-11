# Privacy vendor-review baseline

Eight items, checked independently, for a vendor or third party that
processes personal data on an institution's behalf. Framework-agnostic on
purpose, the same way `rubric/criteria.md` is: it defines *what* to check
for in terms a privacy-by-design discipline would recognize, not one
law's vocabulary. Which framework's exact citation backs up a given item
is decided at review time, from whatever is `active` in
`frameworks/index.yaml` — read those files fresh for each review rather
than citing anything from memory or from this document.

## How to review

- **Status: `satisfied`, `partial`, or `missing`.** `satisfied` means the
  vendor's documentation directly evidences the item; `partial` means
  some evidence exists but falls short (e.g. a policy exists but doesn't
  cover the specific point); `missing` means no evidence was found.
- **`evidence` is required for `satisfied` or `partial`** — the specific
  document, clause, or certification that supports the status, not a
  restatement of the item itself.
- **`gap` is required for `partial` or `missing`** — the specific thing
  still needed, concrete enough that a vendor could act on it directly.
- **Check what the vendor's documentation actually shows**, not what a
  reputable vendor would probably have. A `satisfied` status is earned by
  evidence in hand, not by inference from the vendor's size or reputation.

## 1. Written data-processing terms — `dpa-in-place`

A written agreement (a standalone Data Processing Agreement, or
processing terms incorporated into the master contract) setting out the
subject matter, duration, nature, and purpose of processing, the type of
personal data and categories of data subjects involved, and the
controller's instructions the vendor must follow.

*Why it matters beyond the law:* a person whose data reaches a vendor
never chose that vendor — the institution did, on their behalf. A written
agreement is how the institution keeps its own obligations to that person
from evaporating the moment their data crosses an organizational
boundary, honoring subsidiarity rather than treating the vendor
relationship as beyond its reach.

## 2. Sub-processor disclosure — `sub-processor-disclosure`

Disclosure of any sub-processor the vendor uses to help perform the
service, with either the institution's prior specific authorization or a
general-authorization mechanism giving the institution the chance to
object before a new sub-processor is engaged.

## 3. Security-controls evidence — `security-controls-evidence`

Evidence of technical and organizational security measures appropriate to
the risk — a current third-party certification (e.g. SOC 2 Type II,
ISO/IEC 27001), an independent penetration-test summary, or a completed
security questionnaire with specific, checkable answers rather than
marketing language.

## 4. Breach-notification commitment — `breach-notification-commitment`

A contractual commitment to notify the institution promptly of a security
incident involving the institution's data, with a stated timeframe — not
merely a general reference to "applicable law" with no vendor-side
deadline of its own.

## 5. Data return or deletion — `data-return-deletion`

A contractual commitment to return or delete the institution's data at
the end of the engagement, within a stated timeframe, with confirmation
provided to the institution.

## 6. Audit or inspection rights — `audit-rights`

A contractual right for the institution to audit the vendor's compliance
with the processing terms, or an equivalent assurance mechanism (e.g. the
vendor makes a current independent audit report available on request).

## 7. International transfer mechanism — `data-transfer-mechanism`

Where personal data is transferred outside the jurisdiction it was
collected in, a lawful transfer mechanism is documented (e.g. Standard
Contractual Clauses, an adequacy determination, or another recognized
safeguard) — not merely a statement that data "may be processed
globally" with no mechanism named.

## 8. Minimum-necessary access scope — `minimum-necessary-scope`

The vendor's actual access — to systems, data fields, and individuals'
records — is scoped to what the contracted service requires, not broader
default access left unconfigured.
