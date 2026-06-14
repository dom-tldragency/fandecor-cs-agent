# Template — Returns / exchange

**Action:** auto_send **only if** `policies.returns.confirmed`; else **draft**. The *refund* part is always gated.
**Inputs:** returns window, conditions, who pays postage, process — all from confirmed policy.

---

### How to return / exchange (policy confirmed)
> Hi {first_name},
>
> Happy to help with your return for order **{order_number}**. Here's how it works:
> {returns_process_from_confirmed_policy}
> - Window: {returns_window} from delivery
> - Condition: {returns_conditions}
> - Postage: {who_pays_postage}
>
> {for an exchange:} Let me know the size/item you'd like instead and I'll line that up for you.
>
> Once it's back with us we'll {refund_or_exchange_step — refund step is human-approved}.
>
> {sign_off}

### Policy not yet confirmed → DRAFT only
Write the reply but leave it as a draft and flag in the ClickUp log:
`returns policy unconfirmed — cannot auto-send window/conditions`.

**Guardrail:** issuing the refund at the end of a return is a money action — always human-approved below Phase 3.
