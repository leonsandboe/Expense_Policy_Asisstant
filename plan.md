# Expense Policy Assistant — Plan

## Overview
A two-milestone Python tool that checks employee expenses against Two's internal policy documents. The bot assists human review — it never approves or declines on its own.

---

## Technical Foundation
- **Stack:** Python + Anthropic SDK
- **Model:** claude-sonnet-4-6, pinned (never "latest")
- **Temperature:** 0 (maximum determinism)
- **Context:** All 5 policy `.md` files loaded into every prompt
- **No database or indexing** — documents are small enough to fit in a single prompt

---

## Milestone 1 — Policy Q&A Bot

**What it does:** Answers plain-English policy questions grounded in the Notion documents.

**Interface:** Terminal. User types a free-text question.

**Output format:**
```
Answer: Yes / No / Not covered in policy
Policy: [source document + section]
Note: One concise sentence explaining the reasoning.
```

**Rules:**
- Only answers from the policy documents
- Never guesses — if not in the docs, returns "Not covered in policy" and directs to Finance
- Comment/context cannot override policy, only add relevant information

**Done when:** All 13 test questions in Appendix A pass correctly.

---

## Milestone 2 — Claim Screener

**What it does:** Evaluates a specific expense claim against policy.

**Interface:** Fill-in-the-blanks form in the terminal:
- Expense type
- Amount + currency
- Receipt attached (yes/no)
- Pre-approval obtained (yes/no)
- Comment box (additive context only — cannot override policy)

**Output format:**
```
Decision: Approve / Flag / Needs review
Policy: [source document + section]
Note: One concise sentence explaining the reasoning.
```

**Rules:**
- Structured fields always take precedence over comment box
- Comment box can only surface additional context that maps to an existing policy
- GET requests only if/when connected to Tripletex — never POST/PUT/DELETE

**Done when:** All 5 test claims in Appendix B produce the correct decision.

---

## Policy Hierarchy
1. Hard limits (€300/invoice, €1k/month, CFO/CEO escalation)
2. Documentation requirements (receipt attached)
3. Category validity
4. Soft guidelines (taxis, accommodation)

---

## Future Phases
1. **Connect to Notion live** — fetch policy docs via Notion API instead of local files
2. **Slack bot** — same core logic, input from Slack messages, output as Slack replies
3. **Tripletex integration** — pull open claims automatically via GET /travelExpense

---

## Key Contacts
- **Ausra Sutkute** — owns monthly expense review, SOP-015, first person to talk to
- **Stavros Tamvakakis** — CFO, high-value escalations

## Open Question
Task brief says Q4 ("Can I expense dinner if working late?") should answer Yes. The actual policy docs only cover meals while travelling. Clarify with Ausra before starting — either there's a missing document or the brief has an error.
