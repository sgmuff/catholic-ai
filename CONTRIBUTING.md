# Contributing

This repository is a home for independent projects, added one at a time, that help institutions put Responsible AI into practice from a Catholic perspective. There is no single application here to build up incrementally; there is a standard to hold every project to, so that the tenth project reads with the same discipline as the first.

## One voice, not two tracks

Projects live as directories at the repository root — no separate paths for confessional and secular audiences. Every project is grounded explicitly in Catholic Social Teaching — citing *Magnifica Humanitas*, the Catechism, papal teaching, and the wider CST tradition directly — but written so that a diocese, a Catholic hospital, and a secular compliance officer or board can each act on it without first being persuaded of the theology beneath it. The lineage is stated plainly, never hidden and never diluted; what changes across audiences is emphasis, not the underlying claim.

## Adding a project

1. Copy `docs/project-template/README.template.md` into a new directory at the repository root and fill it in completely — a project without a clear audience, status, and grounding isn't ready to add.
2. Follow `docs/standards/architecture.md` for how the project is laid out and tested, `docs/standards/security-and-privacy.md` for the baseline it must meet, and `docs/standards/skills.md` if it introduces any Claude Skills. If it's Python — the default for anything executable in this repository — follow `docs/standards/python.md`, or just copy `docs/project-template/python-starter/` and start from a skeleton that already satisfies it.
3. Give the project a `Makefile` (or `justfile`) with at least `setup`, `test`, and `lint` targets, so it picks up CI automatically — see `.github/workflows/ci.yml`.
4. Run `pre-commit install` once (config is at `.pre-commit-config.yaml`) so lint, formatting, and secret-scan checks run before you commit rather than after CI catches them.
5. Work through `docs/project-template/CHECKLIST.md` before marking the project's status as active.

## Citation integrity

This work rests on primary sources — magisterial documents, conciliar and papal texts, Catholic Social Teaching encyclicals, and the recognized secular frameworks (NIST AI RMF, ISO/IEC 42001, the EU AI Act) it maps against. Quote and cite these accurately. Do not paraphrase a document into a claim it doesn't make, attribute a line to the wrong source, or invent a citation to fill a gap — if a claim can't be sourced, say so, or leave it out.

## Tone

Write as a practitioner, not a promoter. The audience for every project here is someone who has to actually govern an AI system — a compliance officer, a diocesan chancellor, a hospital's ethics board. They need clear reasoning and usable artifacts, not enthusiasm about AI's potential or generic hedging about its risks. If a sentence would read the same in a vendor's marketing deck, rewrite it.
