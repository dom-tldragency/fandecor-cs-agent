"""Fan Decor CS Agent — one cycle of the always-on loop.

Run: python -m runtime.main [--force] [--brand fandecor]
Safety: DRY_RUN env (default true) means NOTHING is sent/posted — actions are printed instead.
Guardrails are enforced here in code AFTER the LLM, never trusted to the model.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config_loader import Config, is_dry_run
from .adapters.base import ChannelAdapter, StubAdapter, Message
from .adapters.shopify import Shopify
from .adapters.tiktok_seller import TikTokSeller
from .adapters.email_gmail import GmailChannel
from .adapters.meta_ig import MetaIG
from .notify.slack import Slack
from .notify.clickup import ClickUp


# ----- business hours: 07:00–19:00 Europe/London ------------------------------
def within_business_hours() -> bool:
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Europe/London"))
        return 7 <= now.hour < 19
    except Exception:
        return True  # fail open; the GitHub cron already bounds the window


# ----- build the channel adapters from config + env --------------------------
def build_adapters(cfg: Config) -> List[ChannelAdapter]:
    """Create adapters. A channel is ACTIVE only if channels.yaml marks it `status: live`
    (the config gate) AND its credentials are present (the adapter's own .live check). Either
    missing => a stub, so NOTHING runs against a channel until it is explicitly turned on.
    """
    adapters: List[ChannelAdapter] = []
    declared = cfg.channels.get("channels", {})
    for name, ch in declared.items():
        if ch.get("status") != "live":
            adapters.append(StubAdapter(name, ch.get("blocker", "")))
            continue
        if name == "tiktok_seller":
            adapters.append(TikTokSeller())
        elif name == "email":
            mailboxes = ch.get("mailboxes") or [
                "customerservice@fandecor.com", "marketing@fandecor.com"]
            for mb in mailboxes:                      # one adapter per mailbox
                adapters.append(GmailChannel(mb))
        elif name == "meta_ig":
            adapters.append(MetaIG())
        else:
            adapters.append(StubAdapter(name, ch.get("blocker", "")))
    return adapters


# ----- the guardrail decision (code, not the model) --------------------------
def decide_action(cfg: Config, category: str) -> str:
    """Final action after applying mode, policy-confirmation and money gating to the base action."""
    base = cfg.category_action(category)
    if category == "spam":
        return "close"
    if category == "complaint_escalation":
        return "escalate"
    if base == "gated":
        return "gated"            # money — always human-approved below full_phase3
    if base == "auto_send":
        from .llm import reply_quotes_unconfirmed_policy
        if reply_quotes_unconfirmed_policy(cfg, category):
            return "draft"        # would quote an unconfirmed policy -> draft
        if cfg.mode in ("send_non_money", "full_phase3"):
            return "auto_send"
        return "draft"            # draft_only mode
    return "draft"


def handle_message(cfg: Config, adapter: ChannelAdapter, shop: Shopify, slack: Slack,
                   cu: ClickUp, msg: Message, dry: bool) -> Dict[str, Any]:
    from . import llm
    t = llm.triage(cfg, msg)
    category = t.get("category", "complaint_escalation")
    order = adapter.lookup_order(t.get("order_hint", ""), msg.get("customer", {}).get("email")) \
        or shop.lookup_order(t.get("order_hint", ""), msg.get("customer", {}).get("email"))
    action = decide_action(cfg, category)
    order_no = (order or {}).get("order_number", t.get("order_hint", ""))
    approver = cfg.approver.get("slack_id", "")

    if action == "close":
        if not dry:
            adapter.mark_status(msg, "closed")
        cu.log_action(category=category, order=order_no, channel=adapter.name, action="closed")
    elif action == "escalate":
        slack.escalation(f"{category} · {order_no} · \"{t.get('summary','')}\"", approver)
        if not dry:
            adapter.mark_status(msg, "escalated")   # mark handled so it isn't re-processed next cycle
        jamie = [i for i in [cfg.approver.get("clickup_id")] if i]
        cu.log_action(category=category, order=order_no, channel=adapter.name, action="escalated",
                      detail=t.get("summary", ""), assignees=jamie, due_in_hours=24)
    elif action == "auto_send":
        body = llm.draft_reply(cfg, msg, category, order)
        if dry:
            print(f"[DRY_RUN send → {adapter.name}] {order_no}:\n{body}\n")
        else:
            adapter.send_reply(msg, body)
            adapter.mark_status(msg, "resolved")
        cu.log_action(category=category, order=order_no, channel=adapter.name, action="auto_sent")
    else:  # draft or gated
        body = llm.draft_reply(cfg, msg, category, order)
        if not dry:
            adapter.save_draft(msg, body)
            adapter.mark_status(msg, "pending_approval")   # mark handled so it isn't re-processed
        slack.approval_request(
            f"{category} · {order_no} · drafted, needs approval"
            + (" (MONEY)" if action == "gated" else ""), approver)
        # money actions task Camilla + Jamie; other drafts task Camilla (the CS operator)
        if action == "gated":
            assignees = list(cfg.money_task_assignees)
        else:
            assignees = [cfg.cs_operator.get("clickup_id")]
        assignees = [a for a in assignees if a]
        cu.log_action(category=category, order=order_no, channel=adapter.name,
                      action=f"drafted_{action}", detail=t.get("summary", ""),
                      returns=(category in ("returns_exchange", "damaged_wrong_missing")),
                      assignees=assignees, due_in_hours=24)
    return {"category": category, "action": action, "order": order_no}


def run_cycle(brand: str = "fandecor", force: bool = False) -> Dict[str, Any]:
    cfg = Config(brand)
    dry = is_dry_run()
    if not force and not within_business_hours():
        print("Outside 07:00–19:00 Europe/London — idle cycle.")
        return {"skipped": "out_of_hours"}

    shop, slack, cu = Shopify(), Slack(), ClickUp()

    # Loop closure: confirm + close any refunds a human has since processed in Shopify.
    try:
        from .reconcile import reconcile_refunds
        n = reconcile_refunds(cfg, shop, slack, cu, dry)
        if n:
            print(f"Loop-closure: confirmed + closed {n} processed refund(s).")
    except Exception as e:
        print(f"  ! reconcile error: {e}")

    summary = {"seen": 0, "auto_sent": 0, "drafted": 0, "escalated": 0,
               "closed": 0, "errors": 0, "skipped_noise": 0, "stubbed": []}

    max_messages = int(os.environ.get("CS_MAX_MESSAGES", "15"))   # bound per-cycle cost
    for adapter in build_adapters(cfg):
        if not adapter.live:
            summary["stubbed"].append(adapter.name)
            continue
        for msg in adapter.fetch_new():
            # Cheap relevance gate — skip newsletters / order notifications / supplier / automated
            # noise before spending triage+draft tokens (esp. the marketing@ inbox).
            from . import llm
            try:
                relevant = llm.is_customer_message(cfg, msg)
            except Exception:
                relevant = True   # if the gate errors, don't silently drop a possible real message
            if not relevant:
                summary["skipped_noise"] += 1
                if not dry:
                    adapter.mark_status(msg, "closed")
                continue
            if summary["seen"] >= max_messages:
                print(f"Hit CS_MAX_MESSAGES cap ({max_messages}) — stopping cycle to bound cost.")
                break
            summary["seen"] += 1
            try:
                res = handle_message(cfg, adapter, shop, slack, cu, msg, dry)
            except Exception as e:               # one bad message must not kill the cycle
                summary["errors"] += 1
                print(f"  ! error handling message {msg.get('id')}: {e}")
                continue
            key = {"auto_send": "auto_sent", "escalate": "escalated", "close": "closed"} \
                .get(res["action"], "drafted")
            summary[key] += 1

    print(f"Cycle complete (dry_run={dry}, mode={cfg.mode}): {summary}")
    if summary["stubbed"]:
        print(f"Stubbed (awaiting connection): {', '.join(summary['stubbed'])}")
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--brand", default="fandecor")
    p.add_argument("--force", action="store_true", help="ignore the business-hours gate")
    args = p.parse_args()
    try:
        run_cycle(args.brand, args.force)
    except Exception as e:  # never crash the cron silently
        print(f"CYCLE ERROR: {e}", file=sys.stderr)
        raise
