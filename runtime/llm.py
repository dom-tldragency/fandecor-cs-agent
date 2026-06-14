"""Claude API calls for triage + drafting.

The LLM is the reasoning core: it classifies a message and (when allowed) drafts a brand-voice reply,
constrained by the playbook + confirmed policies passed in as context. Deterministic guardrails
(money gating, policy-confirmation, escalation) are applied in main.py AFTER the LLM, never trusted to
the model alone.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .config_loader import Config

TRIAGE_CATEGORIES = [
    "wismo", "delivery_issue", "sizing_product", "order_change_cancel",
    "returns_exchange", "refund_request", "damaged_wrong_missing",
    "complaint_escalation", "spam",
]

MODEL = os.environ.get("CS_MODEL", "claude-opus-4-8")


def _client():
    import anthropic  # lazy import so dry-run/tests don't need the package
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def triage(cfg: Config, message: Dict[str, Any]) -> Dict[str, Any]:
    """Classify a message. Returns {category, order_hint, sentiment, urgency, summary}."""
    system = (
        "You are the Fan Decor customer service triage step. Classify the customer message into "
        "exactly one category and extract fields. Respond ONLY with JSON.\n\n"
        f"Categories: {', '.join(TRIAGE_CATEGORIES)}\n\n"
        "Triage guide:\n" + cfg.triage
    )
    user = (
        f"Channel: {message.get('channel')}\n"
        f"Subject: {message.get('subject', '')}\n"
        f"Message: {message.get('body', '')}\n\n"
        'Return JSON: {"category": "...", "order_hint": "...", "customer_name": "...", '
        '"sentiment": "positive|neutral|negative|angry", "urgency": "...", "summary": "..."}'
    )
    resp = _client().messages.create(
        model=MODEL, max_tokens=400, system=system,
        messages=[{"role": "user", "content": user}],
    )
    return _parse_json(resp.content[0].text)


def draft_reply(cfg: Config, message: Dict[str, Any], category: str,
                order: Optional[Dict[str, Any]]) -> str:
    """Draft a brand-voice reply using the category template + live order data + confirmed policy."""
    template = cfg.templates.get(_template_name(category), "")
    voice = cfg.brand.get("voice", {})
    system = (
        "You are the Fan Decor customer service agent writing a reply in brand voice.\n"
        f"Voice: {json.dumps(voice)}\n\n"
        "HARD RULES:\n"
        "- Never quote a policy value that is not confirmed in the provided policies.\n"
        "- Never promise refunds, delivery dates, or anything outside confirmed policy.\n"
        "- Use ONLY the real order data provided; never invent order details.\n"
        "- Warm, fan-friendly, concise. Never argue.\n\n"
        f"Confirmed policies: {json.dumps(cfg.brand.get('policies', {}))}\n\n"
        f"Template to adapt:\n{template}"
    )
    user = (
        f"Customer message: {message.get('body','')}\n"
        f"Order data: {json.dumps(order) if order else 'No order found'}\n\n"
        "Write the reply body only (no subject, no preamble)."
    )
    resp = _client().messages.create(
        model=MODEL, max_tokens=700, system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text.strip()


def reply_quotes_unconfirmed_policy(cfg: Config, category: str) -> bool:
    """Categories whose stock reply quotes a policy value — gated to draft unless that policy is confirmed."""
    policy_for = {
        "returns_exchange": "returns",
        "sizing_product": "sizing",
        "order_change_cancel": "cancellation",
    }
    key = policy_for.get(category)
    return bool(key) and not cfg.policy_confirmed(key)


def _template_name(category: str) -> str:
    mapping = {
        "wismo": "wismo",
        "delivery_issue": "delivery-issue",
        "sizing_product": "sizing-product",
        "order_change_cancel": "order-change-cancel",
        "returns_exchange": "returns-exchange",
        "refund_request": "refund-request",
        "damaged_wrong_missing": "damaged-wrong-missing",
        "complaint_escalation": "complaint-escalation",
        "spam": "spam",
    }
    return mapping.get(category, category)


def _parse_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip()
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
        raise
