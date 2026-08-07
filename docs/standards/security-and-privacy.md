# Security and privacy standard

Security and privacy matter here in two distinct ways, and a project has to satisfy both. One is about how this repository is engineered. The other is about what its projects tell institutions to do — and a governance project that is careless with data protection in its own recommendations has no standing to prescribe it to anyone else.

## Engineering the repository itself

- **No secrets are committed.** Credentials, API keys, and tokens belong in environment variables or a secrets manager, never in source, fixtures, or example output. If one lands in history anyway, treat it as compromised and rotate it — do not just delete the file.
- **Dependencies are kept current.** A project's `setup` target should pin versions deliberately, not float on `latest`, and dependency updates should be reviewed rather than merged blind.
- **CI tokens are least-privilege.** A workflow gets only the scope it needs to do its job — read access by default, write access only where a step genuinely writes.
- **Test fixtures contain no real personal data.** Sample records, example forms, and demonstration inputs are fabricated or drawn from genuinely public sources, never lifted from a real person's file.

## What a project's work product must address

Most projects in this repository will, sooner or later, produce something that touches how an institution handles people's data — a risk-assessment template, an intake form, a policy an HR office adopts wholesale. Any such deliverable has to address, explicitly rather than by omission:

- **Data minimization** — what the deliverable actually needs to collect or process, and a clear statement of what it deliberately does not.
- **Lawful basis and consent**, where the audience's jurisdiction requires it — a template written for a European diocese cannot be silent on GDPR any more than one written for a US hospital can be silent on HIPAA.
- **Retention** — how long the data a process generates is kept, and what happens to it after.
- **Human oversight of consequential decisions** — no template or tool produced here should let an automated system make a determination about a person — admission, employment, pastoral care, eligibility for assistance — without a human who can be held accountable for it. This is not a compliance nicety; it is *Magnifica Humanitas*'s central claim about the primacy of the human person over automated judgment, applied to the concrete mechanics of a workflow.

A project that doesn't touch personal data at all — a piece of theological writing, an internal talking-points document — can say so plainly in its README and skip the rest of this section. What it cannot do is skip the question.

## Before a project goes active

A project's README status moves to "active" only once:

- the engineering baseline above is met (no secrets, dependencies current, CI scoped correctly), and
- the work-product baseline above is either satisfied and documented in the README's security & privacy notes, or explicitly marked not applicable with a one-line reason.

This is the security half of `docs/project-template/CHECKLIST.md`; that checklist is the operational form of this document.
