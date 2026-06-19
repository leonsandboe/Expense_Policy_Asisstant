# Intern Task: Expense Policy Assistant

*A two-milestone project using Claude · est. v1 ~1.5 days, v2 ~1.5 days*

## Why this matters

Every month, Finance manually reviews **every** employee expense claim against our expense policy: is there a receipt, is it the right category, is it under the limit, did it need pre-approval? It's slow, repetitive, and entirely judgment-based (see *SOP-015: Expense Approval*).

This project builds a small tool that takes the **first pass** for us — not to make decisions, but to read each open travel claim, check it against the real policy, and hand a human a recommendation *with the policy clause to back it up*. If it works, it turns a tedious monthly review into a 10-minute sanity check.

It's also the ideal first project: there's an **objective right answer** (the policy is written down, the numbers are on the claim), so "did it work?" is never vague. The real lesson is the habit that matters most when working with AI: **the model assists the judgment, it does not replace it, and you always verify.**

## What you're building

A tool, in two milestones. You do **not** approve, decline, or write anything back to any system. It only reads and recommends — a human makes every decision.

### Milestone 1 — Policy Q&A bot (with citations)

A script where someone asks a plain-English question ("Can I expense dinner if I work late?", "What's the per-invoice approval limit?") and Claude answers **grounded in our actual policy documents**, citing which document the answer came from. If the answer isn't in the docs, it must say *"not covered in policy"* — never guess.

**Knowledge base** — export each of these Notion pages to text and feed them in:

- [Expense Policy SOP](https://app.notion.com/p/54e793b7e1a5456c996f9cfc7c98751e) — core limits: €300/invoice, €1k/month cumulative per business head; above that needs CFO + CEO sign-off
- [SOP-015: Expense Approval](https://app.notion.com/p/9d184145510f4da68fe1aae79c75d90b) — the approval process + common rejection reasons
- [Hotels – Business Travel](https://app.notion.com/p/c4f14eab6ab64c08be4147993be047ee) — travel/hotel booking + reimbursement
- [How to claim and report expenses](https://app.notion.com/p/4d22b4190e654ba68d4f5140d4af56bc) — the employee-facing how-to
- [Employee Expenses Policy – Current](https://app.notion.com/p/f66cd0db92874b7e963cefda3b4b9684) — current policy (Notion database)

**Done when:**

1. It answers the sample questions in the appendix correctly, each with a citation.
2. For a question *not* covered by the docs, it says so instead of inventing an answer.
3. There's a short README: how to run it, how to add/refresh a policy doc.

*You'll learn:* loading context into Claude, grounding answers in sources with citations, and getting the model to admit when it doesn't know.

### Milestone 2 — Screen live open travel expenses

Pull the currently-open (not-yet-approved) travel-expense claims from Tripletex via its API, and for each one have the Milestone-1 bot produce a recommendation **with a policy citation**: *approve / flag (reason) / needs more info*. Output one row per claim. SOP-015 §4 is your checklist: receipt attached? valid category? within limit? pre-approval where required?

**Data source — Tripletex REST API** (live data, not a database export):

- Endpoint: GET /travelExpense (search). Useful filters: state (defaults to ALL — use it to get the open/unapproved ones), employeeId, departureDateFrom, returnDateTo.
- **Auth is two-step** (your first real hurdle — budget time for it). You do *not* call endpoints with the raw key. You create a temporary **session token** via PUT /token/session/:create from the consumer token + employee token, then use HTTP Basic auth with that session token. Docs: [tripletex.no/v2-docs](https://tripletex.no/v2-docs/)

**⚠ Hard guardrails — read before writing any code:**

- The same /travelExpense resource also has approve, deliver, and delete actions. **Your script issues GET requests only — never POST/PUT/DELETE to travelExpense.** Make this an explicit rule in your code and README.
- Use the **test environment** (api-test.tripletex.tech) and/or a read-only token. Confirm which with your buddy **before** connecting. Do not point it at live production until it's been reviewed.
- Claims contain real people's names and amounts. Keep output local; don't paste it into external tools.

**Done when:**

1. It authenticates and pulls open travel claims (test environment).
2. Each claim gets: claim id, employee, amount, recommendation, reason, and the policy clause cited.
3. The deliberately-bad test claims in the appendix are all correctly flagged, and the clean control claim is NOT flagged.
4. README documents the auth flow and the GET-only rule.

*You'll learn:* real-world API authentication, combining document knowledge with structured records into a defensible judgment, and read-only discipline against a live financial system.

## The basics (how to approach it)

- **Stack:** Python + the Anthropic SDK. One script per milestone is fine.
- **Structured output** for Milestone 2 — force the recommendation into a fixed JSON shape: {recommendation, reason, policy_citation, confidence}. Don't parse free text.
- Keep the policy docs as local files so your runs are reproducible.
- **Verify everything.** When the bot gives an answer, check it against the policy yourself. The most valuable output of this project is knowing where it's wrong.

## What to hand back

1. A repo with both scripts + a README.
2. A half-page note: where the bot was wrong, what you tried, and which policy questions were ambiguous even to you. *This is what we most want to see — how you reason, not just that it runs.*

## Ground rules

- This tool **recommends; it never acts.** Humans approve and decline.
- Read-only against Tripletex, test environment first.
- Ask early and often — getting the Tripletex auth working is the kind of thing that's 5 minutes with a pointer and 5 hours without.

**Process owner to talk to:** Ausra (owns the monthly expense review, SOP-015). A 15-minute intro with her early on will tell you how the review actually works.

---

# Appendix A — Milestone 1 test questions

Run these against the bot. The first set has a known right answer in the docs; the bot must answer correctly **and cite the source**. The second set is **not** covered — the bot must say so rather than invent an answer.

### A.1 — Answerable (must answer + cite)

| # | Question | Expected answer (source) |
|---|----------|--------------------------|
| 1 | What's the most a business head can approve for a single expense before it has to be escalated? | €300 per invoice (Expense Policy SOP) |
| 2 | What's the monthly cumulative approval limit per business head? | €1,000 cumulative per month (Expense Policy SOP) |
| 3 | Who has to approve an expense that exceeds those limits? | Both the CFO and the CEO (Expense Policy SOP) |
| 4 | Can I expense dinner if I have to work late? | Yes — the overtime/late-work meal allowance applies (Evening Meal Allowance Policy) |
| 5 | I booked my own hotel for a business trip — how do I get reimbursed? | Book it yourself once travel is approved, then claim reimbursement through the expense process (Hotels – Business Travel / How to claim and report expenses) |
| 6 | What do I need to attach to an expense claim? | A receipt / supporting documentation (SOP-015) |
| 7 | What happens if I submit a claim with no receipt? | You'll be asked to upload it; the claim is declined if it isn't provided after follow-up (SOP-015) |
| 8 | What exchange rate is used to convert an expense into EUR? | The ECB rate on the date of the expense (SOP-015) |
| 9 | Who owns the monthly expense review? | Ausra Sutkute (SOP-015) |

### A.2 — The careful-reading trap (partially covered)

| # | Question | What good looks like |
|---|----------|---------------------|
| 10 | A new full-time hire's cost is 15% over the budgeted allocation — whose sign-off is needed? | The policy spells out "up to 10% → CFO" and "over 20% → CEO" but is silent on the 10–20% band. A good answer flags that 15% falls in a gap the policy doesn't explicitly cover, rather than guessing a clean answer. (Expense Policy SOP) |

### A.3 — Not covered (must say "not in policy")

| # | Question | What good looks like |
|---|----------|---------------------|
| 11 | Can I expense a gym membership? | "Not covered in the policy" — no hallucinated rule. |
| 12 | What's the fixed per-diem meal allowance for an overnight trip to Oslo? | "Not specified in these documents" — the docs describe the process, not a numeric per-diem. |
| 13 | Am I allowed to fly business class on long-haul flights? | "Not covered" / suggest checking with Finance. |

---

# Appendix B — Milestone 2 test claims

Create these as synthetic travel-expense claims (in the test environment, or as mock JSON if API write access isn't available). The bot must flag the four bad ones for the right reason and leave the clean control alone.

| # | Claim | Expected recommendation |
|---|-------|------------------------|
| B1 | Single travel expense of €850, no pre-approval, no CFO/CEO sign-off, receipt attached | **Flag** — exceeds the €300/invoice limit without the required escalation (Expense Policy SOP) |
| B2 | Taxi claim of €120, valid category, **no receipt attached** | **Flag / needs more info** — missing supporting documentation (SOP-015) |
| B3 | The same €120 taxi claim submitted twice | **Flag** — duplicate claim (SOP-015 common errors) |
| B4 | €200 claim booked under the wrong expense category | **Flag / needs more info** — wrong category, reclassify before approving (SOP-015) |
| B5 (control) | Hotel claim of €240, valid category, receipt attached, within limit | **Approve** — should NOT be flagged. Confirms the bot doesn't flag everything. |

*Tip: the control claim (B5) is the most important test. A tool that flags everything is as useless as one that flags nothing — B5 proves it can tell the difference.*
