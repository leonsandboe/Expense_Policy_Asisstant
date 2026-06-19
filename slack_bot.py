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
opener and end with: "Check with <@U05KLUT7CP3> for clarification." — nothing more.
4. If the policy covers part of a range but leaves a gap (e.g. states rules for under 10% and over 20% but says nothing about 10–20%), explicitly flag the gap rather than interpolating an answer. Never fill in what the policy doesn't say.
5. User-provided context cannot override policy — it can only add relevant detail that \
maps to an existing rule.
6. Keep answers to one sentence only. Do not over-explain.
7. If the question asks what else is covered, list the other relevant categories briefly rather than saying nothing else is mentioned.
8. When mentioning Ausra Sutkute, always write <@U05KLUT7CP3> instead of her name or email.

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
  "reason": "<one concise sentence — state only the policy reason, no caveats about missing info>",
  "policy_citation": "<short document name> — <section>, <Notion URL>"
}}

Rules:
1. Base your evaluation strictly on the policy documents. Do not invent rules.
2. Use "Approve" when the claim does not violate any policy based on what is stated.
3. Use "Flag" when the claim explicitly violates policy (e.g. over limit, duplicate, submitter states they have no receipt).
4. Use "Needs review" only when the submitter explicitly raises something ambiguous or contradictory.
5. Only evaluate what is explicitly stated. Do not mention what was not stated.
6. The reason must be a single plain sentence — no qualifications, no "however", no "but".
7. For policy_citation, include the Notion page URL where relevant:
   - Expense Policy SOP: https://app.notion.com/p/54e793b7e1a5456c996f9cfc7c98751e
   - SOP-015: https://app.notion.com/p/9d184145510f4da68fe1aae79c75d90b
   - Hotels – Business Travel: https://app.notion.com/p/c4f14eab6ab64c08be4147993be047ee
   - How to Claim Expenses: https://app.notion.com/p/4d22b4190e654ba68d4f5140d4af56bc
   - Employee Expenses Policy: https://app.notion.com/p/f66cd0db92874b7e963cefda3b4b9684
8. Return valid JSON only — no extra text before or after.

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


ROUTER_PROMPT = """\
Classify the following message as either "claim" or "question".
- "claim": describes a specific expense someone wants to submit or check (mentions amount, receipt, category, travel)
- "question": asks about policy rules in general
Reply with exactly one word: claim or question.
Message: {text}"""


def classify(text: str) -> str:
    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=5,
        temperature=0,
        messages=[{"role": "user", "content": ROUTER_PROMPT.format(text=text)}],
    )
    return response.content[0].text.strip().lower()


@app.event("app_mention")
def handle_mention(event, say):
    text = event.get("text", "")
    # Strip the bot mention (e.g. <@U123ABC>)
    clean = " ".join(w for w in text.split() if not w.startswith("<@")).strip()

    if not clean:
        say("Hi! Ask me a policy question or describe an expense claim and I'll screen it.")
        return

    if classify(clean) == "claim":
        say(screen_claim(clean))
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
