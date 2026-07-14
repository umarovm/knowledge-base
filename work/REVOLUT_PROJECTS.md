# Revolut Projects

A record of Tech Support projects completed at Revolut, covering closure-code analysis, process improvements, documentation, and cross-team escalation work.

Several closure-code analyses were run repeatedly as a standing quarterly audit rather than one-off projects. Those are grouped below by theme, with each quarter's run kept as a sub-entry so the specific numbers and findings aren't lost.

Each project below has a **Tags** line (skills/themes) and a **Resume bullet** (a ready-to-adapt, quantified one-liner). When tailoring a CV to a job posting, match the posting's keywords against the Skills Index below to pick the most relevant projects, then pull and adjust the resume bullets.

## Highlights

**Scope (based on figures recorded in this doc):** 2,000+ support tickets analyzed across six closure-code audits; 21+ Confluence pages created/updated; 3+ bug reports filed and tracked to resolution (BUGS-427401, BUGS-427404, BUGS-425614); 1 recurring GCP-log initiative that shipped 9+ in-app/Back Office messaging fixes; process changes projected to cut duplicate-ticket escalations by up to 60%.

**Recurring themes:** three of the closure-code analyses (GCP Logs, Duplicate of Escalated Ticket, More Information Requested) were run repeatedly over 2023–2025, showing sustained ownership of a standing quality-audit process rather than one-off analysis.

**Skills Index** — quick lookup by theme/keyword, for matching against a job posting:

| Skill / Theme | Projects |
|---|---|
| Data analysis & root cause analysis | #1, #2, #5, #6 |
| SQL / Metabase / Looker | #6, #7 |
| Log analysis (GCP) | #2 |
| Jira / ticket triage & workflow | #1, #5, #6 |
| Confluence / technical documentation | #1, #3, #4 |
| Cross-functional collaboration (Product, Engineering, CXM) | #1, #2, #3 |
| Process design & policy change | #2, #5, #6 |
| Dashboards / data visualization | #5, #6 |
| Bug reporting / QA | #2 |

## Contents

- [Highlights](#highlights)

1. [Re-assignment Requests](#1-re-assignment-requests)
2. [Closure Code Analysis – Clarification Based on GCP Logs (Recurring)](#2-closure-code-analysis--clarification-based-on-gcp-logs-recurring)
   - December 2023
   - Q2 2025
   - Q3 2025
3. [Reducing Incorrectly Raised Tickets – Savings Vault Terminations](#3-reducing-incorrectly-raised-tickets--savings-vault-terminations)
4. [Updating/Creating Confluence Pages](#4-updatingcreating-confluence-pages)
5. [Closure Code Analysis – Duplicate of Already Escalated Ticket (Recurring)](#5-closure-code-analysis--duplicate-of-already-escalated-ticket-recurring)
   - Q1 2024
   - Q4 2024
   - Q3 2025
6. [Closure Code Analysis – More Information Requested (Recurring)](#6-closure-code-analysis--more-information-requested-recurring)
   - Q2 2024
   - Q1 2025
7. [Closure Code Analysis – Clarifications Based on Metabase Findings (Q2 2024)](#7-closure-code-analysis--clarifications-based-on-metabase-findings-q2-2024)


---

## 1. Re-assignment Requests

**Timeline:** 11 October 2023
**Reference:** Re-assignment requests
**Tags:** Process improvement, root cause analysis, documentation, stakeholder management
**Resume bullet:** Diagnosed misrouted escalation tickets by tracking 30+ monthly cases, partnered with the Product Owner to clarify team ownership, and updated internal documentation to correct the routing.

**Problem**
Tickets regarding the account recovery flow were being escalated to the wrong team.

**Context**
Issues related to the account recovery flow were escalated to different teams due to a lack of clarity in internal documentation. After manually checking how agents were reasoning about escalation, I contacted the Product Owner, clarified the team's scope, and updated the documentation.

**My Work**
Tracked every ticket escalated to the wrong team instead of Onboarding to identify patterns.

**Results**
Made a post to inform teammates and updated the team's scope in internal documentation.

**Impact**
From September 1 to October 1, 30 tickets were escalated to the wrong team. The documentation change was made on 11 October; measuring the same length of time afterward (November 1 – December 1), 30 tickets were still escalated. Impact: low to minimal.

---

## 2. Closure Code Analysis – Clarification Based on GCP Logs (Recurring)

Recurring initiative analyzing tickets closed via GCP log review. Started as a push to replace generic in-app error messages with specific, actionable ones; later runs expanded into broader log-pattern analysis to inform Back Office tooling and self-service features — the strategy matured from "propose better copy" to "surface the log data directly."

**Tags:** Log analysis (GCP), data analysis, root cause analysis, cross-functional collaboration (Product/Engineering), UX copywriting, Back Office tooling, bug reporting/QA
**Resume bullet:** Ran a recurring GCP-log analysis (600+ tickets across 3 cycles, 2023–2025), driving 9+ shipped in-app/Back Office messaging fixes and proposals to surface log data directly for CS self-service, cutting reliance on Tech Support escalation.

### December 2023

**Reference:** Closure Codes – GCP Logs

**Problem**
Generic error messages in the app could have been replaced with more specific, actionable error messages.

**My Work**
Analyzed 500+ tickets closed with the "Clarification based on GCP logs" closure code across all product verticals to identify which error messages found in GCP logs could be added to the app instead of the generic "Something went wrong" message.

**Results**
Produced a list of proposals delivered to Product Owners:

- **Internal Transfers** — For "Something went wrong" errors during an internal transfer, proposed checking: user restrictions in the Back Office, KYC status, beneficiary criteria, and whether the user holds a pocket in the sending currency. If a passcode error occurs, guide the user to check/reset their passcode; also check Slack for ongoing outages. Linked the relevant Confluence page (R Transfer to other Revolut accounts P2P – other issues troubleshooter) and proposed a new page, "Troubleshooting before raising ticket to Tech QC."
- **Outbound Transfers** — For transactions with reason code `PENDING_TM_ASSESSMENT` in BO transaction details, escalate to the TM team and include the TM ticket link when raising to Tech Support (linked: ATO CS RAP Onboarding app unified flow). Noted that QAR transfers are unsupported; for QR code issues, check whether it's a Swiss/CH QR code and refer to the relevant Confluence page; also check the currency being sent.
- **Backoffice** — Filed bug reports (BUGS-427401, BUGS-427404) requesting the BackOffice team update the limits section to display correct data.
- **Verification code error** — Filed a bug report (BUGS-425614, example ticket BUGS-418016) highlighting that the "verification code you entered is incorrect" message causes confusion, since it could refer to an SMS/verification code rather than the Revolut app passcode.

### Q2 2025

**Reference:** GCP – Clarification based on logs – Closure Code Analysis (March 2025 tickets)
**Context:** Tickets closed after checking GCP logs.

**Problem**
Users frequently saw generic "Something went wrong" messages or other unclear error notifications in the Revolut App, driving confusion and support volume. Tech Support agents also lacked sufficiently detailed information in the Back Office to resolve complex issues efficiently.

**My Work**
Analyzed logs and user-facing messages to identify pain points, then collaborated with Product and Engineering to propose and implement improvements: clearer, more descriptive in-app error messages; more detailed restriction information in the Back Office for features like Credit, Crypto, and Fincrime; and interface changes to surface user restrictions and their feature impact to agents.

**Results**
Aimed to reduce user frustration and support contact by providing transparent, actionable information, while streamlining troubleshooting, improving first-contact resolution, and increasing operational efficiency for Tech Support.

**Impact — proposed / implemented messaging**

- "Average monthly installment cannot be greater than ****. Please edit to proceed further" — credit applications
- "Invalid address. Please check the details entered" — crypto withdrawals
- "DEPOSIT is not possible. FTM is disabled for topping up" — crypto deposits (unsupported currencies)
- Back Office Fincrime tab updated to show user restrictions and affected features
- "Phone and/or passcode are incorrect. Please try again" — sign-in
- "You can't set up the same passcode as your old one. Please create new passcode" — sign-in
- "Account with entered details already exists. Please sign in to the account" — sign-up
- "Authentication rejected. Please enter correct passcode" — sign-in
- "Promotion used is not available in your country" — sign-up

### Q3 2025

**Reference:** GCP – Clarification based on logs – Closure Code Analysis (July 2025 tickets)
**Context:** Tickets closed after checking GCP logs.

**Problem**
144 tickets analyzed, concentrated in Transfers (57), Retail Products (22), and Wealth & Trading (21), mostly of Minor bug severity. Resolving these required in-depth GCP log investigation, driving reliance on Tech Support for clarification.

**My Work**
Performed detailed GCP log analysis to clarify complex customer issues — notably informing customers about workflow steps (16 instances), identifying fraud suspicions (7), and addressing feature access limits (6) — translating log data into actionable insight for CS and, at times, customers directly.

**Results**
About 51.25% of information retrieved from GCP logs was straightforward enough to consider adding to the Back Office (letting CS resolve without escalating), and 39.02% was suitable for a potential in-app feature enabling customer self-service.

**Impact**
- **Enhanced Back Office tools** — Surface more log-derived information directly (e.g., "adding beneficiary flow," "transaction not logged in BO") to cut Tech Support workload and improve CS first-contact resolution.
- **Proactive customer communication** — In-app messaging for cases like "workflow reached max allowed number of steps" or failed transactions with a stated reason, to reduce inbound contact.
- **Improved log tracking/visibility** — Better logging for beneficiary flows and certain failed transfers, for clearer diagnostics.
- **Automated issue resolution** — Use consistent log patterns to build automated or guided troubleshooting for CS agents.

---

## 3. Reducing Incorrectly Raised Tickets – Savings Vault Terminations

**Timeline:** Q4 2023
**Tags:** Process improvement, documentation, cross-team collaboration (CXM)
**Resume bullet:** Identified a recurring false-escalation pattern around Savings Vault withdrawals and drove Confluence updates across 2 of 3 affected pages, cutting unnecessary investigation time and enabling k-gapping going forward.

**Problem**
Tickets were being incorrectly raised regarding account termination when a user had a pending withdrawal from a Savings Vault.

**Results**
Raised a CXM ticket, resulting in 2 of 3 relevant Confluence pages being updated (the third pending). This reduces tickets that consumed teammates' investigation time in cases where standard tools don't work, and allows k-gaps to be applied on such tickets going forward. Pages updated: [R] Savings – UK Vault, [R] Savings – EEA Vault, and [R] Escalations to the Terminations queue.

---

## 4. Updating/Creating Confluence Pages

**Timeline:** Q4 2023
**Tags:** Technical documentation, knowledge management, process standardization
**Resume bullet:** Audited and rewrote 19 Confluence pages across 8 product verticals, adding step-by-step troubleshooting guides and screenshots to reduce incorrect solutions and speed up issue resolution.

**Problem**
Confluence pages across Retail Account, Card Payments + Chargebacks, Cards, Fincrime, Referrals + Rewards + Stays, Savings, Top-ups, and Transfers contained outdated or missing information, increasing the risk of incorrect solutions and slowing issue resolution. 19 pages required attention in total.

**My Work**
Reviewed and revised existing pages — adding new information, clarifying existing content, and aligning with current processes. Identified pages needing updates, archiving, or renaming. Wrote detailed guides with step-by-step instructions and screenshots for issues such as missing push notifications, email delivery troubleshooting, login investigation, and card order errors.

**Results**
- Clarified Face ID login information for Android users
- Added guides for checking missing push notifications and troubleshooting email delivery
- Revised queries for card payments, STIP, and offline transactions
- Documented detailed investigation steps for login and passcode change issues
- Added notes and references for card order errors
- Updated information for Savings and MMF common issues, Personal Vaults/Pockets/Bills, and Group Vaults

**Impact**
Improved the efficiency and accuracy of customer support with up-to-date, comprehensive knowledge resources; reduced the likelihood of incorrect information reaching customers; streamlined troubleshooting; and ensured consistency across pages. 19 pages updated in total.

---

## 5. Closure Code Analysis – Duplicate of Already Escalated Ticket (Recurring)

Recurring quarterly audit of tickets closed as duplicates of ones already escalated to Product. Customer Support is required to check the Ongoing Issues (OI) page and link their chat to an existing escalation, but duplicates kept recurring — each run dug into root causes (CS mistake vs. process/visibility gap) and pushed fixes. Reported CS-mistake/duplicate rates aren't directly comparable across runs (different measurement bases — by vertical, by week, or overall), but all three consistently point to the same root cause: agents not checking or not finding the Ongoing Issues page.

**Tags:** Data analysis, root cause analysis, Jira, process improvement, quantitative analysis, dashboards/visualization
**Resume bullet:** Owned a recurring quarterly audit (3 cycles, 2024–2025, 650+ tickets reviewed) into duplicate ticket escalations, identifying the root cause and designing an action plan projected to cut duplicate escalations by up to 60%.

### Q1 2024

**Reference:** Q1 2024 – Closure code Duplicate of Escalated Ticket – Linked to Master Ticket

**Context**
When a ticket is already escalated to the Product team, Customer Support is required to check the Ongoing Issues page and link their chat to the existing ticket. However, new tickets kept being raised and closed as duplicates of already-escalated ones. This analysis aimed to find root causes and patterns to prevent duplicate ticket creation on the Jira board.

**My Work**
Checked 500 tickets closed as duplicates, analyzing why they were escalated and whether the mistake originated with Tech or Customer Support. Prepared visualizations and insights from the data.

**Results (by vertical)**

- **Retail Account** — 40.8% CS mistake, few investigations needed, notable Tech mistake rate. High CS mistakes were traced to an ongoing Pending KYC issue (17-day gap in updates) and agents being unaware of the Ongoing Issues page. Proposed: automate KYC ongoing-page updates (or mandate daily manual updates), have CXM reference the page more often, and emphasize it during agent onboarding/training.
- **Product Expert escalation** — 23.3% CS mistake; most tickets not added to OI; investigation-needed rate lower than average. High CS mistake rate among SMEs (who should be more knowledgeable) may stem from asking for confirmation rather than searching Jira themselves. Proposed: implement the Kgap system for Product Experts (or a tick-box at escalation) and provide vertical-specific training on searching the escalation board.
- **Fincrime** — 61.3% CS mistake, almost no investigation needed — the highest-attention issue type, indicating many avoidable escalations. Proposed: apply the same solutions as Retail Account, with greater emphasis.
- **Referrals** — 72.6% investigation needed, other categories minimal. A flow change (campaigns no longer syncing) may bias this, since many tickets previously required running a tool to pull fail logs. Proposed: fix the syncing issue, or publish a Confluence statement clarifying Tech Support no longer performs this action; removing the sync-campaigns option would meaningfully cut escalated tickets.
- **Cards** — 80% not added to the OI. Many corner cases prevent visibility on Ongoing pages, and agents can't easily link an issue without creating a new ticket. No improvements proposed.
- **Transfers** — 33.9% investigation needed, 16.9% CS mistake — reasonable given the need to check logs. CS mistakes occur when agents raise tickets for known errors (e.g., linking via Open Banking systematically errors) that logs could confirm. No improvements proposed.
- **Credit** — Higher Tech mistake percentage, needing further review (possibly user-specific or country/product differences); sample size may be too small for firm conclusions. Proposed: create a Confluence page explaining Credit particularities to counter the mistake rate.

### Q4 2024

**Reference:** Q4 Duplicate Escalated tickets

**Context**
When a ticket is already escalated to the Product team, Customer Support must check the Ongoing Issues page and link their chat to it. Repeated duplicate escalations prompted this analysis of root causes and patterns.

**Problem**
Recurring "CS mistakes" and tickets "not added to OI" (Ongoing Issues), alongside tickets needing investigation or falling into "Other." Goal: understand and reduce the error rate tied to CS interactions.

**My Work**
Analyzed JIRA tickets weekly from 28 October to 31 December 2024, recording: JIRA link, issue type (primarily [R] Retail Product), created date, reason raised (investigation needed / not added to OI / CS mistake / other), whether a CS mistake was k-gapped, notes, reporter email, TL, and POM. Calculated weekly CS-mistake counts, total tickets, and error rate.

**Results — weekly error rate**

| Period | Error rate | CS mistakes / Total |
|---|---|---|
| 23/12 – 31/12 | 46.15% | 6 / 13 |
| 12/12 – 22/12 | 23.81% | 5 / 21 |
| 2/12 – 11/12 | 25.71% | 9 / 35 |
| 25/11 – 01/12 | 52.63% | 10 / 19 |
| 18/11 – 24/11 | 50.00% | 3 / 6 |
| 11/11 – 17/11 | 70.00% | 7 / 10 |
| 4/11 – 10/11 | 90.91% | 20 / 22 |
| 28/10 – 3/11 | 72.73% | 24 / 33 |

Notes captured reasons tickets weren't added to OI (e.g., "was closed by that time," "ticket was not escalated at that time") and context on specific CS mistakes (e.g., unclear summaries, possible tech support mistakes in some naming cases). One note flagged a critical main ticket missing from the OI page.

### Q3 2025

**Reference:** Nika – Closure Codes Q4 2025

**Problem**
51.76% of escalated tickets were "Mistake from support" — largely because CS agents weren't checking the Ongoing Issues page or were creating new tickets instead of reopening already-escalated ones, causing duplicates.

**My Work**
Analyzed why CS agents were unable to connect issues to ongoing ones and developed an action plan: make it mandatory for CS to check the Ongoing Issues page and record findings in ticket descriptions, and add closed escalated tickets to the Ongoing Issues page for better visibility.

**Results**
The action plan is projected to cut duplicate tickets by 50% through better Ongoing Issues page checks, plus an additional 10% from listing closed escalated tickets there — a total projected reduction of 60%.

---

## 6. Closure Code Analysis – More Information Requested (Recurring)

Recurring audit of tickets closed with "More information requested" (auto-closes after two days if unanswered), checking whether raising them was a CS mistake or a documentation/process gap. Closure-code correctness came up as the top issue in both runs — the Q2 2024 fixes (reminder post, Confluence updates) don't appear to have fully closed the gap, since Q1 2025 still found roughly 30% of cases incorrectly closed. Worth a follow-up check on whether the reminders actually stuck.

**Tags:** Data analysis, Looker, quantitative analysis, process improvement, training/enablement
**Resume bullet:** Ran a recurring audit (2 cycles, 733 tickets reviewed) of "more information requested" closures, surfacing closure-code misuse as the top root cause and driving a team-wide reminder plus Confluence updates on mandatory escalation requirements.

### Q2 2024

**Reference:** Q2 2024 More information requested

**Context**
When a ticket lacks sufficient detail to investigate, the closure code "More information requested" is applied while more detail is sought from Customer Support. If not updated within two days, the ticket auto-closes. This analysis checked whether raising such tickets was a CS mistake or a Confluence documentation gap, to find root causes and reduce recurrence.

**Problem**
A high volume of tickets were being closed after requesting additional information needed for investigation.

**My Work**
Checked 270 tickets to determine why this closure code was used, what information was actually needed, and whether it was already listed as a mandatory escalation requirement.

**Results — by vertical**

| Vertical | Share | Count |
|---|---|---|
| [R] Retail Account | 26.28% | 313 |
| [R] Retail Product | 21.24% | 253 |
| [R] Product Expert escalation | 15.62% | 186 |
| [R] Transfers | 10.66% | 127 |
| [R] Top-up | 9.57% | 114 |
| [R] Cards | 4.20% | 50 |
| [R] Card Payments | 2.69% | 32 |
| [R] Credit | 2.60% | 31 |
| [R] Bug | 2.27% | 27 |
| [R] Fincrime | 1.76% | 21 |
| [R] Wealth & Trading | 1.09% | 13 |
| [R] Chargeback | 0.84% | 10 |
| [R] Referrals | 0.42% | 5 |
| [R] Insurance | 0.34% | 4 |
| [R] Stays | 0.34% | 4 |
| [R] Tool Runner Request | 0.08% | 1 |

**Results — reason distribution**

- Additional investigation steps: 257
- Wrong closure code: 162
- Screenshot/screen recording requested — can't be requested before raising: 144
- Information missing in the description — should be provided: 58
- Clarification was provided: 31
- Fix confirmation pending / Issue resolution pending: 30
- Screenshot/screen recording requested — missing in the description: 25
- Request to reach out to third party: 10

**Impact**
Top three findings, with proposed follow-ups:

- **Additional investigation (35.8%)** — Legitimate requests for more information; no action needed.
- **Wrong closure code (22.6%)** — Agents frequently used "More information requested" when another code fit better. Breakdown: basic troubleshooting (28.8%), escalation to other service team (27.6%), knowledge gap (17.9%), GCP (9.6%), Metabase (5.8%), duplicate of escalated ticket (5.1%), resolved without action (1.9%), Sparkpost (1.9%), Taskmaster (1.3%). **Action:** posted a reminder in the retail-tech-1 channel sharing the analysis and prompting correct closure-code use.
- **Screenshot/recording requested but couldn't be requested before raising (20.1%)** — Cases where Technical QC requested screenshots only after the ticket moved to "waiting for feedback," meaning CS couldn't have obtained them from the user beforehand. Compiled a table of issues, affected features, examples, CXM status, and recommended Confluence wording to close this gap.
- **Other categories** — Information missing in the ticket (8.1%, recommend k-gapping to cut volume); clarification was provided (4.3%, recommend closing with "Missing information on CS knowledge base"); fix confirmation pending (4.2%, low priority, no change); request to reach out to third party (1.4%).
- Also proposed updating the "Mandatory requirements Confluence page" with screenshot exceptions for Top-up, Transfers, Open Banking, Address, Stock trading, chargeback submission issues, Sign in/Log in, Apple Pay card addition, internal transfers, eSIM, Savings, and Credit/Load applications.

### Q1 2025

**Reference:** Q1 2025 – More information requested

**Context**
When ticket descriptions from Customer Support lack sufficient detail for investigation, the "More information requested" closure code is applied, and unanswered tickets auto-close after two days. This project checked whether raising such tickets was a CS mistake or a documentation gap, to reduce recurrence.

**Problem**
Addressed a mix of unresolved cases, issues resolved by Tech Support, self-resolved issues, and issues resolved by Customer Support — with the core challenge being effective management and clear communication across these pathways.

**My Work**
Categorized and tracked resolution of customer issues: identifying root causes of unresolved cases (e.g., lack of communication), documenting successful technical interventions, recognizing self-resolved cases, and recording CS resolutions (sometimes with technical guidance or escalation).

**Results**
Produced a structured overview of issue-resolution pathways, showing where communication or technical assistance was decisive for customer satisfaction. Of 463 cases analyzed, 326 were correctly closed and 137 were not.

---

## 7. Closure Code Analysis – Clarifications Based on Metabase Findings (Q2 2024)

**Timeline:** Q2 2024
**Reference:** MB clarifications based on findings
**Tags:** SQL, Metabase, data querying, data governance
**Resume bullet:** Audited the team's Metabase SQL query base, proposing and implementing a set of new/refined queries to close data-access gaps and improve support-team data capabilities.

**Problem**
Needed to improve the SQL query base and identify scopes requiring additional queries.

**My Work**
- **Areas reviewed:** In-depth analysis across functional areas, examining existing data queries, associated documentation, and handling of sensitive information.
- **Approved enhancements:** Proposed, approved, and integrated several new data queries to improve support capabilities and data management, documenting them in the relevant knowledge bases.
- **New query implementations:** Successfully implemented a set of refined data queries to streamline operations and improve data accessibility for support functions.

---

