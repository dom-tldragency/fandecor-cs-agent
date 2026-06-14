# Template — Refund request

**Action:** **GATED (money).** Never auto below Phase 3; above the cap never auto at all.
The agent acknowledges warmly, gathers facts, drafts a recommendation, and routes to the named approver.
It does **not** confirm or process the refund.

---

### Customer-facing acknowledgement (this part may be drafted; the refund itself is not actioned)
> Hi {first_name},
>
> Thanks for getting in touch about order **{order_number}**, and sorry it's not worked out. I've passed this to the team to review your refund request and we'll come back to you very shortly with confirmation.
>
> {if more info needed: Could you confirm {what} so we can process this smoothly?}
>
> {sign_off}

### Internal recommendation for the approver (Slack + ClickUp, not sent to customer)
```
REFUND REQUEST — needs approval
Order: {order_number} | Customer: {name} | Amount: £{amount} | Currency: GBP
Reason: {reason}
Order facts: {fulfilment status, delivered?, within returns window?, prior issues?}
Policy check: {within confirmed refund policy? Y/N — cite}
Cap check: {amount vs refund_cap_gbp}
Recommendation: {approve full / partial £X / decline — with one-line rationale}
```

**Guardrail:** if fraud/chargeback suspected → do not process, flag and escalate.
