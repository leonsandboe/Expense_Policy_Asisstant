# Expense Policy Assistant

Two tools for reviewing employee expenses against Two's internal policy documents.

---

## Setup

**Requires:** Python 3, the Anthropic SDK, and an API key.

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

---

## Milestone 1 — Policy Q&A

Ask plain-English questions about Two's expense policy.

```bash
python3 milestone1_qa.py
```

**Example:**
```
Q: Can I expense a business dinner?
That's within policy — client meals are covered with a receipt and cost commentary.
```

Answers are grounded strictly in the policy documents. If a question isn't covered, the bot says so and directs to asutkute@two.inc.

---

## Milestone 2 — Claim Screener

Describe an expense claim in plain English and get a policy-grounded recommendation.

```bash
python3 milestone2_screener.py
```

**Example:**
```
Claim: Taxi of €120, no receipt attached
Recommendation: Flag
Reason: Supporting documentation is required before an expense can be approved.
Policy: SOP-015 — Step 4.3, Missing receipt
```

---

## Policy Documents

Stored as local `.md` files exported from Notion:

| File | Contents |
|------|----------|
| `notion-employee-expenses-policy-current.md` | Current policy |
| `notion-expense-policy-sop.md` | Core limits and categories |
| `notion-hotels-business-travel.md` | Travel and accommodation |
| `notion-how-to-claim-expenses.md` | Employee how-to |
| `notion-sop-015-expense-approval.md` | Approval process and common errors |

**To update a document:** re-export the Notion page to `.md` and replace the corresponding file. No code changes needed.

---

## Ground Rules

- These tools recommend only — no approvals or declines are made automatically.
- For policy questions not covered by the documents, contact asutkute@two.inc.
