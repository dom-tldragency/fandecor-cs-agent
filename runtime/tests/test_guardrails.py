"""Reproducible guardrail test — no network. The one that must never regress:
no money/escalation category may ever resolve to auto_send.

Run: python -m runtime.tests.test_guardrails   (or pytest)
"""
from __future__ import annotations

from runtime.config_loader import Config
from runtime.main import decide_action

MONEY_OR_COMPLAINT = {"refund_request", "damaged_wrong_missing", "complaint_escalation"}
CATEGORIES = [
    "wismo", "delivery_issue", "sizing_product", "order_change_cancel",
    "returns_exchange", "refund_request", "damaged_wrong_missing",
    "complaint_escalation", "spam",
]


def test_no_money_or_complaint_autosend():
    cfg = Config("fandecor")
    for c in CATEGORIES:
        action = decide_action(cfg, c)
        if c in MONEY_OR_COMPLAINT:
            assert action != "auto_send", f"LEAK: {c} resolved to auto_send"
    # explicit expectations
    assert decide_action(cfg, "refund_request") == "gated"
    assert decide_action(cfg, "complaint_escalation") == "escalate"
    assert decide_action(cfg, "spam") == "close"


def test_unconfirmed_policy_downgrades_to_draft():
    cfg = Config("fandecor")
    # sizing policy is unconfirmed -> must be a draft, never auto_send
    assert decide_action(cfg, "sizing_product") == "draft"


if __name__ == "__main__":
    test_no_money_or_complaint_autosend()
    test_unconfirmed_policy_downgrades_to_draft()
    print("guardrail tests: PASS")
