"""One-shot DEMO — show the team what the agent would draft, without sending anything.

Grabs a recent (already-handled) customer email from customerservice@, runs the full pipeline
(relevance gate -> triage -> Shopify lookup -> brand-voice draft), and posts the result as a
clearly-labelled PREVIEW into #fan-decor-cs-agent. It sends nothing to customers and saves no draft.

Run: python -m runtime.demo
"""
from __future__ import annotations

import json
import os

from .config_loader import Config
from .adapters.email_gmail import GmailChannel
from .adapters.shopify import Shopify
from .notify.slack import Slack
from . import llm


def run_demo() -> None:
    cfg = Config("fandecor")
    gmail = GmailChannel("customerservice@fandecor.com")
    slack = Slack()
    if not gmail.live:
        print("Gmail not configured — set GMAIL_SERVICE_ACCOUNT_JSON.")
        return

    shop = Shopify()
    candidates = gmail.fetch_recent(max_threads=15)

    chosen = None
    for m in candidates:
        try:
            if llm.is_customer_message(cfg, m):
                chosen = m
                break
        except Exception as e:
            print(f"relevance check error: {e}")
    if not chosen:
        slack.post("🧪 *Demo:* couldn't find a recent customer email in customerservice@ to draft from.")
        return

    t = llm.triage(cfg, chosen)
    category = t.get("category", "wismo")
    order = shop.lookup_order(t.get("order_hint", ""), chosen.get("customer", {}).get("email"))
    draft = llm.draft_reply(cfg, chosen, category, order)

    order_line = f" · order {order.get('order_number')}" if order else " · no order matched"
    preview = (
        "🧪 *DRAFT PREVIEW — demo only, nothing sent*\n"
        f"*Customer:* {chosen['customer'].get('name')}\n"
        f"*Subject:* {chosen.get('subject') or '(none)'}\n"
        f"*Their message:*\n> {((chosen.get('body') or '').strip()[:280] or '(empty)')}\n\n"
        f"*Triaged as:* `{category}`{order_line}\n\n"
        f"*The reply I'd draft:*\n{draft}"
    )
    slack.post(preview)
    print("Demo draft posted to Slack.")


if __name__ == "__main__":
    run_demo()
