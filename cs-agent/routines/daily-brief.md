# Routine — daily 8am CS brief (Slack)

Runs once daily at 08:00 Europe/London. Posts ONE message to `#fan-decor-cs-agent`.

---

Compile the last 24h of Fan Decor CS activity from the ClickUp CS list (and live channels) and post a
single Slack message to `#fan-decor-cs-agent` in this shape:

```
☀️ Fan Decor CS — Daily Brief · {date}

📥 Volume: {total} messages
   by channel: Email {n} · Shopify Inbox {n} · TikTok {n} · IG {n}
   by category: WISMO {n} · Returns {n} · Refunds {n} · Damaged/Wrong/Missing {n} · Sizing {n} · Delivery {n} · Complaints {n} · Spam {n}

✅ Auto-resolved: {n}   ✍️ Awaiting approval: {n}   🚨 Escalations: {n}

💷 Refunds: {n} pending approval (£{total}) · {n} processed
⏱️ SLA risk: {n} unanswered > {X}h   {list the oldest}
📈 Sentiment: {flag any complaint/negative spike vs baseline}

🔧 Blockers: {e.g. email channel still stubbed; policies X,Y unconfirmed}
```

Rules:
- If there were escalations or items awaiting approval, list them with order # and a one-line ask so they
  can be actioned straight from the brief.
- Keep it scannable — one message, no threads unless listing >5 open items.
- `SLA threshold {X}h` and sentiment baseline: CONFIRM with Dom.
