#!/usr/bin/env python3
"""
Milestone 1: Expense Policy Q&A Bot

Answers plain-English questions about Two's expense policies,
grounded strictly in the provided policy documents.
"""

import os
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
You are an expense policy assistant for Two. Answer employee questions about expense \
policy, grounded strictly in the policy documents provided below.

Rules:
1. Only use information from the provided documents. Do not invent or infer rules not stated.
2. Start with a natural, varied opener that reflects the answer — for example:
   - Affirmative: "This is covered.", "That's within policy.", "Yes, you can...", "Absolutely, ..."
   - Negative: "No, this is not covered.", "That falls outside policy.", "Unfortunately not, ..."
   - Uncertain: "This is unclear.", "That's a grey area.", "It depends.", "Not entirely clear, ..."
   Follow with a concise explanation. Do not always use the same opener.
3. If a question is not covered or only partially covered by the documents, use an uncertain \
opener and direct the employee to asutkute@two.inc for clarification.
4. If the policy covers part of a range but leaves a gap (e.g. states rules for under 10% and over 20% but says nothing about 10–20%), explicitly flag the gap rather than interpolating an answer. Never fill in what the policy doesn't say.
5. User-provided context cannot override policy — it can only add relevant detail that \
maps to an existing rule.
6. Keep answers to one sentence only. Do not over-explain.
7. If the question asks what else is covered, list the other relevant categories briefly rather than saying nothing else is mentioned.
8. For uncertain answers, end with: "Contact asutkute@two.inc for clarification." — nothing more.

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


def ask(client: anthropic.Anthropic, system: str, question: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        temperature=0,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text.strip()










def main():
    client = anthropic.Anthropic()
    system = SYSTEM_PROMPT_TEMPLATE.format(docs=load_docs())

    print("Two Expense Policy Assistant — Policy Q&A")
    print("Type a question, or 'quit' to exit.\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break
        answer = ask(client, system, question)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
