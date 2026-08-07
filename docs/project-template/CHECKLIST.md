<!--
  Copy this file to projects/<track>/<project-name>/CHECKLIST.md if the project needs its own
  (e.g. a non-code deliverable's review checklist). Code projects can point to this file directly
  from their README instead of copying it, provided they don't need to extend it.
-->

# Go-live checklist

A project's README status moves from `draft` to `active` only once every item here is either
checked or explicitly marked not applicable, with a one-line reason, in the project's README.

## Correctness

- [ ] Tests pass (`make test`), or, for a non-code deliverable, every item in its own review has
      been resolved
- [ ] Lint is clean (`make lint`)
- [ ] Every citation — magisterial, CST, or a secular framework (NIST AI RMF, ISO/IEC 42001,
      EU AI Act) — has been checked against its primary source, not reconstructed from memory

## Security & privacy

- [ ] No secrets are committed anywhere in the project
- [ ] Dependencies are current and pinned deliberately, not floating
- [ ] Any CI access this project needs is scoped to the minimum required
- [ ] If this project's work product touches personal data: data minimization, lawful basis,
      retention, and human oversight of consequential decisions are each addressed in the
      README's security & privacy section
- [ ] If this project's work product does not touch personal data: the README says so, with a
      one-line reason

## Fit for audience

- [ ] The README's Audience and Grounding sections are filled in and specific — not a placeholder
- [ ] The project reads like the work of a practitioner addressing its stated audience, not a
      generic AI-ethics essay
- [ ] Any bundled Skills validate cleanly (`skills-ref validate`) and follow
      [`docs/standards/skills.md`](../standards/skills.md)
