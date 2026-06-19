# SOP-015: Expense Approval

Source: https://app.notion.com/p/9d184145510f4da68fe1aae79c75d90b

---

## 1. Purpose

Review, validate, and approve or decline employee expense claims across all Two entities, ensuring compliance with the company expense policy and accurate booking in the accounting systems.

## 2. When to Run

- **Frequency:** Monthly (batch review), with ad-hoc processing as claims are submitted
- **Trigger:** Employees submit expense claims in the relevant accounting system (Tripletex for Norway, Xero for UK, Deel for Remote)
- **Dependencies:** Employees must attach supporting documentation (receipts) to their claims before review
- **Owner:** Ausra Sutkute

## 3. Systems Involved

- Tripletex (Norway entity expense claims)
- Xero (UK entity expense claims)
- Deel (Remote employee expense claims)
- Google Sheets — "Expenses review" tracker
- Slack — **#fin-hr** channel (policy questions, pre-approval requests)

## 4. Step-by-Step Instructions

1. **Export open claims** — At month-end, pull all pending expense claims from Tripletex (NO), Xero (UK), and Deel (Remote).
2. **Log in tracker** — Enter each claim into the "Expenses review" Google Sheet with: entity, employee name, date, description, expense category, claim amount, currency, and EUR equivalent.
3. **Policy check** — For each claim, verify:
   - Receipt / supporting documentation is attached
   - The expense category is valid per Two's expense policy
   - The amount is reasonable and within policy limits
   - Pre-approval was obtained where required (e.g., travel, equipment)
4. **Flag exceptions** — Add comments in the "AS Comments" column for any claims that need clarification, are missing receipts, or appear non-compliant.
5. **Escalate if needed** — For borderline or high-value claims, consult with Stavros (CFO) via Slack or the tracker's "ST comments" column.
6. **Approve or decline** — Mark each claim as "Approved" or "Declined" in the tracker. For declined claims, add a clear reason.
7. **Process in accounting system** — For approved claims:
   - **Tripletex (NO):** Approve the expense in Tripletex and trigger reimbursement via the next payroll run
   - **Xero (UK):** Approve in Xero; reimbursement is processed via bank payment or payroll
   - **Deel (Remote):** Approve in Deel; reimbursement follows Deel's payment cycle
8. **Notify employees** — For declined claims, inform the employee via Slack or email with the reason and any steps to resubmit.
9. **Reconcile** — At month-end, ensure all approved expenses are correctly booked to the right GL accounts and cost centres.

## 5. Common Errors & How to Fix Them

| Error | Fix |
|-------|-----|
| Missing receipt or supporting documentation | Ask the employee to upload the receipt before approving; decline if not provided after follow-up |
| Expense claimed under wrong category | Reclassify before approving and inform the employee for future reference |
| Duplicate claim submitted across systems | Cross-check the Expenses review tracker; reject the duplicate |
| Claim exceeds policy limit without pre-approval | Escalate to CFO; either approve with documented exception or decline |
| Reimbursement not reflected in payroll | Check with payroll processing (Norian for NO, Gravita for UK) that approved expenses are included in the next run |
| Currency conversion errors | Use the ECB rate on the date of the expense for EUR conversion |

## 6. Contacts

| Role | Person | Reach out when… |
|------|--------|-----------------|
| Finance Analyst (Owner) | Ausra Sutkute | Day-to-day expense review, policy questions |
| CFO | Stavros Tamvakakis | High-value or policy-exception approvals |
| Norian (NO accountant) | Trond (Norian) | Norway payroll reimbursement issues |
| Gravita (UK accountant) | Gravita team | UK expense booking or reimbursement issues |
| People/HR | Elada Gailiunaite | Expense policy clarifications, employee communications |
