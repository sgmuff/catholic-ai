# Catholic AI

## Purpose

Every technology carries within it a judgment about what human beings are for, and artificial intelligence is no exception. This repository exists to articulate and defend a distinctly Catholic account of that judgment; it refuses to treat intelligence, work, and dignity as commodities to be optimized, and insists instead that the human person, made in the image of God, the *imago dei*, is never merely a means to efficiency.

The starting point for this work is *Magnifica Humanitas*, in which Pope Leo XIV takes up the questions that his predecessors first raised for the industrial age and presses them into our own: what does a technology owe to the people it displaces, augments, or serves? Who bears responsibility when a machine's judgment stands in for a human one? And how does a society preserve the dignity of labor and the primacy of the person when the tools at hand can think, in some diminished sense, for themselves? These are not new questions dressed in new language. They are the same questions Leo XIII asked of capital and labor in *Rerum Novarum*, inherited and renewed for an age of algorithms.

This project holds, with the whole of Catholic Social Teaching, that the measure of any technology is the human good it serves — not merely the wealth it generates or the convenience it offers. Subsidiarity teaches that decisions belong as close as possible to the people they affect, a principle too easily forgotten when systems are built to centralize judgment in code that few can see and fewer still can question. Solidarity teaches that the benefits of innovation cannot be hoarded by the few who build it while its costs fall on the many who did not choose it. And the dignity of the human person — prior to any market, any state, and any machine — remains the fixed point against which every application of artificial intelligence must be tested, and by which it must, if necessary, be refused.

None of this is written in opposition to the tools themselves. The Church has never been a stranger to craft, and intelligence rightly ordered can serve the poor, extend the reach of the healer and the teacher, and free human beings for the work that only they can do. But a tool rightly used is a tool understood, and understanding it rightly requires more than an engineer's fluency — it requires the wisdom of a tradition that has spent two thousand years asking what human flourishing actually demands. That is the work undertaken here: to think clearly, and in fidelity to the Church, about what we are building, and to what end.

## How this repository works

This is not one application but a home for several, added one at a time as they're ready. Each is a self-contained project that helps a real institution govern its use of AI responsibly, and each answers to the same standards regardless of what it's built with — the discipline is meant to feel the same in the tenth project as in the first.

Every project sits on one of two tracks:

- **[`projects/catholic-institutions/`](projects/catholic-institutions/)** — work for dioceses, religious orders, Catholic universities, hospitals, and charities. These projects can speak in explicitly confessional terms, citing the Catechism, papal teaching, and canon law directly, because their audience already shares the Church's account of the human person.
- **[`projects/secular-institutions/`](projects/secular-institutions/)** — work for institutions that don't start from that premise but end up in much the same place. These argue from the same commitments — subsidiarity, solidarity, the common good, a dignity no automated system may override — in terms a secular compliance officer or board can act on without first being persuaded of the theology underneath them.

Both tracks are scaffolded and empty right now. Projects land here as the person maintaining this repository is ready to add them; there's nothing to browse yet beyond the standards that will govern what arrives.

## Repository layout

```
catholic-ai/
├── README.md                        — this file
├── CONTRIBUTING.md                  — the two tracks, how to add a project, citation and tone rules
├── SECURITY.md                      — vulnerability disclosure
├── .gitignore / .env.example        — what never gets committed, and what local setup looks like
├── .pre-commit-config.yaml          — lint, formatting, and secret-scan checks run before a commit
├── .github/workflows/ci.yml         — secret scan, Skill validation, per-project lint & test
├── docs/
│   ├── standards/
│   │   ├── architecture.md          — TDD discipline, the standard setup/lint/test surface, project layout
│   │   ├── security-and-privacy.md  — the engineering baseline, and what a deliverable must address
│   │   ├── skills.md                — this repo's conventions on top of the agentskills.io spec
│   │   └── python.md                — the Python toolchain: pytest, ruff, mypy, a coverage floor
│   └── project-template/
│       ├── README.template.md       — the sections a new project's README must fill in
│       ├── CHECKLIST.md             — the go-live checklist before a project is marked active
│       └── python-starter/          — a working Python project skeleton, ready to copy
├── skills/                          — Claude Skills shared across every project
└── projects/
    ├── catholic-institutions/       — explicitly confessional work
    └── secular-institutions/        — the same principles, argued in secular-compatible terms
```

## Standards

Every project — whatever it's written in, whichever track it's on — is held to four documents in [`docs/standards/`](docs/standards/):

| Standard | Covers |
|---|---|
| [`architecture.md`](docs/standards/architecture.md) | Test-driven development as the default discipline, the `setup`/`lint`/`test` command surface every project exposes, and how a project's directory is laid out |
| [`security-and-privacy.md`](docs/standards/security-and-privacy.md) | Securing the repository's own engineering practice, and what any deliverable touching personal data has to address — minimization, lawful basis, retention, human oversight |
| [`skills.md`](docs/standards/skills.md) | The [agentskills.io](https://agentskills.io) spec, plus this repository's conventions for where a Skill lives, how it's named, and how it's validated |
| [`python.md`](docs/standards/python.md) | The concrete toolchain — pytest, ruff, mypy, an 80% coverage floor — for Python, the default language here |

## Contributing

[`CONTRIBUTING.md`](CONTRIBUTING.md) walks through adding a project end to end: which track it belongs on, what its README has to say before it's ready, and the checklist it clears before going active. Read it before opening a project directory of your own.
