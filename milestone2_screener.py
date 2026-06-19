#!/usr/bin/env python3
"""
Milestone 2: Expense Claim Screener

Takes structured details about an expense claim and produces a
policy-grounded recommendation: Approve / Flag / Needs review.
"""

import json
from pathlib import Path
import anthropic

BASE_DIR = Path(__file__).parent

POLICY_FILES = {
    "Employee Expenses Policy – Current": "notion-employee-expenses-policy-current.md",
    "Expense Policy SOP": "notion-expense-policy-sop.md",
    "Hotels – Business Travel": "notion-hotels-business-travel.md",
    "How to Claim and Report Expenses": "notion-how-to-claim-expenses.md",
    "SOP-015: Expense Approval": "notion-sop-015-expense-approval.md",
}

SYSTEM_PROMPT_TEMPLATE = """\
You are an expense claim screener for Two. Given a structured expense claim, \
evaluate it against the policy documents below and return a JSON object with \
exactly these fields:

{{
  "recommendation": "Approve" | "Flag" | "Needs review",
  "reason": "<one concise sentence>",
  "policy_citation": "<short document name (e.g. SOP-015, Expense Policy SOP)> — <section name or number>"
}}

Rules:
1. Base your evaluation strictly on the policy documents. Do not invent rules.
2. Use "Approve" when the claim does not violate any policy based on what is stated.
3. Use "Flag" when the claim explicitly violates policy (e.g. over limit, duplicate, submitter states they have no receipt).
4. Use "Needs review" only when the submitter explicitly raises something ambiguous or contradictory.
5. Only evaluate what is explicitly stated. If receipt, pre-approval, or other details are not mentioned, do not assume they are absent — silence is not a problem.
6. A comment from the submitter can add context but cannot override policy.
6. Return valid JSON only — no extra text before or after.

---
POLICY DOCUMENTS

{docs}
"""


def load_docs() -> str:
    parts = []
    for name, filename in POLICY_FILES.items():
        path = BASE_DIR / filename
        content = path.read_text()
        parts.append(f"### {name}\n\n{content}")
    return "\n\n---\n\n".join(parts)




def screen(client: anthropic.Anthropic, system: str, claim: str) -> dict:
    message = claim + "\n\nRespond with a JSON object only. No explanation, no markdown, no code fences."
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": message}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def main():
    client = anthropic.Anthropic()
    system = SYSTEM_PROMPT_TEMPLATE.format(docs=load_docs())

    print("Two Expense Claim Screener")
    print("Describe the claim in plain English, or type 'quit' to exit.\n")

    while True:
        try:
            claim = input("Claim: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not claim:
            continue
        if claim.lower() in ("quit", "exit", "q"):
            break

        result = screen(client, system, claim)

        print(f"\n--- Result ---")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Reason:         {result['reason']}")
        print(f"Policy:         {result['policy_citation']}\n")



if __name__ == "__main__":
    main()
