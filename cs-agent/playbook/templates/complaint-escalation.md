# Template — Complaint / escalation

**Action:** **ESCALATE — never auto-send.** Same-minute Slack ping to the named approver.
The agent's job is to flag fast with full context and (optionally) prepare a de-escalation draft for a human to approve.

---

### Slack escalation ping (immediate)
```
🚨 ESCALATION — {complaint | legal threat | chargeback | influencer/large order}
Channel: {channel} | Customer: {name} | Order: {order_number}
Sentiment: {angry / threatening / legal}
What they said: "{verbatim snippet}"
Order facts: {status, value £, prior contacts}
Why escalated: {trigger}
Suggested next step: {one line}
@{named_approver}
```

### Optional de-escalation draft (for a human to review/send — NOT auto-sent)
> Hi {first_name},
>
> I'm really sorry about this — I completely understand the frustration, and I want to make it right. I've flagged your message to {team/owner} personally and we'll come back to you directly and quickly.
>
> Thank you for your patience while we sort this properly.
>
> {sign_off}

**Guardrails:** never argue, never admit liability on legal threats, never act on a chargeback. Hand to a human.
