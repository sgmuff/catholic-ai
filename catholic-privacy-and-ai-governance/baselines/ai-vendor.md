# AI vendor-review baseline

Seven items, checked independently, for a vendor supplying an AI system,
model, or AI-enabled feature, including a foundation-model provider.
Framework-agnostic on purpose, the same way `rubric/ai-criteria.md` is: it
defines *what* to check for in terms an AI-governance discipline would
recognize, not one law's vocabulary. Which framework's exact citation
backs up a given item is decided at review time, from whatever is
`active` in `frameworks/index.yaml` — read those files fresh for each
review rather than citing anything from memory or from this document.

## How to review

- **Status: `satisfied`, `partial`, or `missing`.** `satisfied` means the
  vendor's documentation directly evidences the item; `partial` means
  some evidence exists but falls short (e.g. a model card exists but
  omits known limitations); `missing` means no evidence was found.
- **`evidence` is required for `satisfied` or `partial`** — the specific
  document, artifact, or disclosure that supports the status, not a
  restatement of the item itself.
- **`gap` is required for `partial` or `missing`** — the specific thing
  still needed, concrete enough that a vendor could act on it directly.
- **Check what the vendor's documentation actually shows**, not what a
  reputable vendor would probably have. A `satisfied` status is earned by
  evidence in hand, not by inference from the vendor's size or reputation.

## 1. Model documentation provided — `model-documentation-provided`

Technical documentation or a model card describing the system's intended
purpose, training data provenance (to the extent disclosable), and known
limitations — sufficient for the institution to interpret the system's
output and use it within its documented scope.

*Why it matters beyond the law:* an institution that deploys a system it
cannot explain has handed its own judgment to a black box. Documentation
is how the primacy of human judgment over automated determination stays
real rather than nominal — a deployer can't exercise oversight over what
it was never told.

## 2. Evaluation results provided — `evaluation-results-provided`

Testing or evaluation results for the system's accuracy, robustness, and
bias/fairness performance, specific enough to assess fitness for the
institution's own intended use — not a generic marketing claim of "state
of the art" performance.

## 3. Incident and defect notification commitment — `incident-reporting-commitment`

A contractual commitment to notify the institution of a known safety
issue, defect, or incident affecting the system, with a stated timeframe
— the vendor-to-deployer information flow the institution's own incident
response depends on.

## 4. Upstream dependency disclosure — `upstream-dependency-disclosure`

Disclosure of the models, components, or third-party data the vendor's
own system depends on, so risk inherited from an upstream dependency the
institution never chose directly can actually be assessed.

## 5. Human-oversight support — `human-oversight-support`

The system is designed to support the institution's own human-oversight
obligations as a deployer — for example, exposing a confidence score or
similar signal, and allowing a human reviewer to override its output —
rather than presenting only a final answer with no way to interrogate it.

## 6. Model-update notification commitment — `update-notification-commitment`

A contractual commitment to notify the institution before materially
updating or replacing the underlying model, so a prior assessment isn't
silently invalidated by a change the institution never knew happened.

## 7. Training-data governance evidence — `data-governance-evidence`

Where the vendor trains or fine-tunes on data the institution provides,
evidence of data governance practices for that data — how it's used,
retained, and whether it's used to improve the vendor's models for other
customers unless the institution has agreed to that.
