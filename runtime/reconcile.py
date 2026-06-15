"""Loop closure — detect refunds processed by a human, confirm + close the task.

Each cycle: scan open refund/money tasks in the CS list, check Shopify for a refund on that order,
and when one is found: comment + close the ClickUp task and post a Slack confirmation. Optionally
(behind the auto_confirm_refunds flag) emails the customer a "you've been refunded" confirmation.

The agent NEVER processes the refund itself — a human does that in Shopify/TikTok. This step only
*observes* that it happened and closes the loop, so nothing lingers and the customer hears back.
"""
from __future__ import annotations

import re
from typing import Any

from .config_loader import Config
from .adapters.shopify import Shopify
from .notify.slack import Slack
from .notify.clickup import ClickUp

_ORDER_RE = re.compile(r"#?(\d{3,})")


def reconcile_refunds(cfg: Config, shop: Shopify, slack: Slack, cu: ClickUp, dry: bool = True) -> int:
    """Returns the number of refunds confirmed + closed this cycle."""
    closed = 0
    gmail = None
    if cfg.auto_confirm_refunds:
        from .adapters.email_gmail import GmailChannel
        gmail = GmailChannel("customerservice@fandecor.com")

    for task in cu.list_open_tasks(cu.list_id):
        name = (task.get("name") or "")
        if "refund" not in name.lower() and "gated" not in name.lower():
            continue
        m = _ORDER_RE.search(name)
        if not m:
            continue
        order_no = m.group(1)
        order = shop.lookup_order(order_no)
        if not order:
            continue
        try:
            refunded = float(order.get("total_refunded") or 0)
        except (TypeError, ValueError):
            refunded = 0.0
        if refunded <= 0:
            continue

        # A human has processed the refund — close the loop.
        cu.comment_task(task["id"], f"✅ Refund of £{refunded:.2f} detected as processed in Shopify. Closing.")
        cu.close_task(task["id"], cu.list_id)
        slack.post(f"✅ Refund for #{order_no} confirmed processed (£{refunded:.2f}) — ClickUp task closed.")

        if gmail and gmail.live and order.get("email") and not dry:
            body = (
                f"Hi {order.get('customer_first_name') or 'there'},\n\n"
                f"Good news — your refund for order #{order_no} (£{refunded:.2f}) has been processed and is "
                f"on its way back to the payment method you used.\n\n"
                f"Thanks for your patience, and sorry again for the hassle.\n\n"
                f"Cheers,\nThe Fan Decor team"
            )
            gmail.send_email(order["email"], f"Your Fan Decor refund — order #{order_no}", body)
        elif gmail:
            print(f"[refund-confirm] would email {order.get('email')} re #{order_no}")
        closed += 1

    return closed
