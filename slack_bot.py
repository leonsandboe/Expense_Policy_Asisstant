#!/usr/bin/env python3
"""
Slack bot for Two Expense Assistant.
- @mention with a policy question → M1 (Policy Q&A)
- @mention with "screen: <claim>" → M2 (Claim Screener)
"""

import json
import os
from pathlib import Path

import anthropic
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request

BASE_DIR = Path(__file__).parent

POLICY_FILES = {
    "Employee Expenses Policy – Current": "notion-employee-expenses-policy-current.md",
    "Expense Policy SOP": "notion-expense-policy-sop.md",
    "Hotels – Business Travel": "notion-hotels-business-travel.md",
    "How to Claim and Report Expenses": "notion-how-to-claim-expenses.md",
    "SOP-015: Expense Approval": "notion-sop-015-expense-approval.md",
}

QA_SYSTEM_PROMPT = """\
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

SCREENER_SYSTEM_PROMPT = """\
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
7. Return valid JSON only — no extra text before or after.

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


docs = load_docs()
qa_system = QA_SYSTEM_PROMPT.format(docs=docs)
screener_system = SCREENER_SYSTEM_PROMPT.format(docs=docs)

anthropic_client = anthropic.Anthropic()

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
)


def ask_policy(question: str) -> str:
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        temperature=0,
        system=qa_system,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text.strip()


def screen_claim(claim: str) -> str:
    message = claim + "\n\nRespond with a JSON object only. No explanation, no markdown, no code fences."
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        temperature=0,
        system=screener_system,
        messages=[{"role": "user", "content": message}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw.strip())
    return (
        f"*Recommendation:* {result['recommendation']}\n"
        f"*Reason:* {result['reason']}\n"
        f"*Policy:* {result['policy_citation']}"
    )


@app.event("app_mention")
def handle_mention(event, say):
    text = event.get("text", "")
    # Strip the bot mention (e.g. <@U123ABC>)
    clean = " ".join(w for w in text.split() if not w.startswith("<@")).strip()

    if clean.lower().startswith("screen:"):
        claim = clean[7:].strip()
        if not claim:
            say("Please describe the claim after `screen:` — e.g. `screen: Hotel €240, receipt attached`")
            return
        say(screen_claim(claim))
    else:
        say(ask_policy(clean))


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)
