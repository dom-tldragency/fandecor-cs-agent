# Template — Order change / cancellation

**Action:** auto_send the confirmation **if** within `policies.cancellation` window **and** no refund is triggered;
if it triggers a refund → **gated**. Address/size changes pre-fulfilment can be actioned in Shopify if safe.
**Inputs:** fulfilment status (can it still be changed?), cancellation window (confirmed?), refund implication.

---

### Address / details change (pre-fulfilment)
> Hi {first_name},
>
> No problem — I can see order **{order_number}** hasn't shipped yet, so I've updated the {what_changed} to:
> {new_detail}
> You'll get the tracking link to confirm once it's on its way. Thanks for catching that!
>
> {sign_off}

### Cancellation request (within window, no refund yet taken / unpaid)
> Hi {first_name},
>
> Done — order **{order_number}** has been cancelled as requested and nothing further will be dispatched. {refund_line — only if no money action, else route to approval}.
>
> Sorry to see this one go — hope to kit you out next time! ⚽
>
> {sign_off}

### Already shipped / outside window / refund needed
*(Do not auto-confirm. If a refund is involved → gated. If outside the confirmed window → escalate.)*
> Hi {first_name},
>
> Thanks for letting me know. Order **{order_number}** has already been {status}, so let me check the best option for you here — a colleague will follow up shortly with how we can sort this.
>
> {sign_off}
