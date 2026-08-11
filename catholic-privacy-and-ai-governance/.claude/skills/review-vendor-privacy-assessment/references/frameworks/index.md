# Framework registry

## gdpr-dpia — GDPR Art. 35 — Data Protection Impact Assessment

- **Type:** law
- **Citation root:** GDPR Art. 35
- **Review status:** reviewed
- **Source:** https://gdpr-info.eu/art-35-gdpr/
- **Trigger:** A DPIA is required before processing begins whenever a type of processing — particularly one using new technologies, and given its nature, scope, context, and purposes — is likely to result in a high risk to the rights and freedoms of natural persons (Art. 35(1)). Three specific cases are always in scope regardless of that general judgment (Art. 35(3)): automated decision-making or profiling that produces legal or similarly significant effects, large-scale processing of special categories of data, and large-scale systematic monitoring of a publicly accessible area.

- **Jurisdiction:** European Union, European Economic Area, Any controller or processor outside the EU/EEA processing EU/EEA data subjects' personal data under GDPR's extraterritorial scope (Art. 3)
- **File:** `frameworks/privacy/gdpr-dpia.yaml`

## gdpr-data-subject-rights — GDPR Chapter III — Rights of the Data Subject

- **Type:** law
- **Citation root:** GDPR Arts. 12-22
- **Review status:** reviewed
- **Source:** https://gdpr-info.eu/chapter-3/
- **Trigger:** Applies whenever a controller receives a request from a data subject to exercise a right under GDPR Chapter III, regarding personal data the controller processes about them. Distinct from `gdpr-dpia` in this registry, which covers Art. 35's impact-assessment obligation, not the data-subject-rights response obligations here — a request-triage task should cite this entry, not that one.

- **Jurisdiction:** European Union, European Economic Area, Any controller or processor outside the EU/EEA processing EU/EEA data subjects' personal data under GDPR's extraterritorial scope (Art. 3)
- **File:** `frameworks/privacy/gdpr-data-subject-rights.yaml`

## ccpa-cpra — CCPA/CPRA — California Consumer Privacy Act, as amended by the California Privacy Rights Act

- **Type:** law
- **Citation root:** Cal. Civ. Code § 1798.100 et seq.
- **Review status:** reviewed
- **Source:** https://oag.ca.gov/privacy/ccpa
- **Trigger:** Applies to a for-profit "business" doing business in California that collects California residents' personal information and meets at least one threshold: (a) annual gross revenue over $25 million, (b) buys, sells, or shares the personal information of 100,000 or more California consumers or households annually, or (c) derives 50% or more of annual revenue from selling or sharing California consumers' personal information. Separately, a business whose processing presents significant risk to consumers' privacy or security must conduct and submit a risk assessment under CPPA regulations adopted pursuant to Civ. Code § 1798.185(a)(15) — the closest CCPA/CPRA analog to a DPIA, with regulations taking effect January 1, 2026.

- **Jurisdiction:** California
- **File:** `frameworks/privacy/ccpa-cpra.yaml`

## gdpr-breach-notification — GDPR Arts. 33-34 — Notification of a Personal Data Breach

- **Type:** law
- **Citation root:** GDPR Arts. 33-34
- **Review status:** reviewed
- **Source:** https://gdpr-info.eu/art-33-gdpr/
- **Trigger:** Applies whenever a controller becomes aware of a personal data breach — a breach of security leading to the accidental or unlawful destruction, loss, alteration, unauthorized disclosure of, or access to, personal data. Distinct from `gdpr-dpia` (Art. 35's pre-processing impact assessment) and `gdpr-data-subject-rights` (Chapter III's response obligations to a rights request) in this registry — an incident-triage task should cite this entry, not those.

- **Jurisdiction:** European Union, European Economic Area, Any controller or processor outside the EU/EEA processing EU/EEA data subjects' personal data under GDPR's extraterritorial scope (Art. 3)
- **File:** `frameworks/privacy/gdpr-breach-notification.yaml`

## ca-breach-notification — California data breach notification law

- **Type:** law
- **Citation root:** Cal. Civ. Code § 1798.82
- **Review status:** reviewed
- **Source:** https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.82.&lawCode=CIV
- **Trigger:** Applies to any individual or business that conducts business in California and owns or licenses computerized data including personal information, on discovering a breach of the security of the system — unauthorized acquisition of computerized data that compromises the security, confidentiality, or integrity of personal information. A materially broader trigger than `ccpa-cpra` in this registry: no revenue or data-volume threshold applies here, unlike CCPA/CPRA's "business" definition — this is a separate, older statute in the same Civil Code title, not a CCPA/CPRA provision.

- **Jurisdiction:** California
- **File:** `frameworks/privacy/ca-breach-notification.yaml`

## hipaa — HIPAA — Health Insurance Portability and Accountability Act (Privacy, Security, and Breach Notification Rules)

- **Type:** law
- **Citation root:** 45 CFR Parts 160, 164
- **Review status:** reviewed
- **Source:** https://www.law.cornell.edu/cfr/text/45/164.308
- **Trigger:** Applies to "covered entities" (health plans, health care clearinghouses, and health care providers who transmit health information electronically in connection with a covered transaction) and their "business associates" who create, receive, maintain, or transmit protected health information (PHI) on a covered entity's behalf. The Security Rule's risk analysis requirement (45 CFR 164.308(a)(1)(ii)(A)) — the closest HIPAA analog to a DPIA — applies to electronic PHI specifically.

- **Jurisdiction:** United States
- **File:** `frameworks/privacy/hipaa.yaml`

## ferpa — FERPA — Family Educational Rights and Privacy Act

- **Type:** law
- **Citation root:** 20 U.S.C. § 1232g; 34 CFR Part 99
- **Review status:** reviewed
- **Source:** https://www.law.cornell.edu/cfr/text/34/99.31
- **Trigger:** Applies to any educational agency or institution that receives funding under a program administered by the U.S. Department of Education — covering most U.S. schools, school districts, and postsecondary institutions (including a Catholic university, college, or K-12 school participating in federal funding or student aid programs). Governs "education records": records directly related to a student and maintained by the institution or a party acting for it. FERPA has no DPIA-style impact-assessment requirement of its own; the closest functional analog here is the disclosure-exception analysis under 34 CFR 99.31 — whether a planned disclosure fits a recognized exception or requires consent.

- **Jurisdiction:** United States
- **File:** `frameworks/privacy/ferpa.yaml`

## iso-27701 — ISO/IEC 27701:2019 — Privacy Information Management System (PIMS)

- **Type:** standard
- **Citation root:** ISO/IEC 27701:2019
- **Review status:** reviewed
- **Source:** https://www.iso.org/standard/71670.html
- **Trigger:** Voluntary — an institution opts into assessment against this standard, typically to extend an existing ISO/IEC 27001 information security management system (ISMS) into a full privacy information management system (PIMS), or to demonstrate privacy-by-design maturity to partners, regulators, or auditors. Applies distinctly to PII controllers (Annex A-style requirements) and PII processors (Annex B-style requirements) — an institution assessed against this standard should state which role, or both, it holds for the activity in scope.

- **Jurisdiction:** any
- **File:** `frameworks/privacy/iso-27701.yaml`

## nist-privacy-framework — NIST Privacy Framework v1.0

- **Type:** standard
- **Citation root:** NIST Privacy Framework v1.0
- **Review status:** reviewed
- **Source:** https://www.nist.gov/privacy-framework/privacy-framework
- **Trigger:** Voluntary — an institution opts into assessment against this framework to structure its privacy risk management using a common vocabulary, often alongside the NIST Cybersecurity Framework. Not a checklist of binding requirements; each Function/Category is a risk-management outcome an institution can adopt, adapt, or explicitly decide not to prioritize, documenting why.

- **Jurisdiction:** any
- **File:** `frameworks/privacy/nist-privacy-framework.yaml`
