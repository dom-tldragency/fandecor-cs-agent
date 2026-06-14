# Template — Damaged / wrong / missing item

**Action:** **GATED.** Usually needs a replacement (raised in **Tarlu** — see `sops/tarlu-raise-order.md`)
and/or a refund. Agent gathers evidence, drafts the empathetic reply, and routes the resolution for approval.

---

### Customer-facing acknowledgement (drafted; resolution is human-approved)
> Hi {first_name},
>
> Oh no — I'm really sorry your order **{order_number}** arrived {damaged / with the wrong item / incomplete}. That's not the standard we want for you. {if photo needed per confirmed policy: Could you reply with a quick photo of the {item/packaging}? That lets us sort a replacement or refund fast.}
>
> As soon as I have that I'll get this put right for you straight away.
>
> {sign_off}

### Internal resolution note for approver (Slack + ClickUp)
```
DAMAGED/WRONG/MISSING — needs decision
Order: {order_number} | Customer: {name} | Item(s): {sku / product}
Issue: {damaged | wrong item sent | missing line item}
Evidence: {photo received? Y/N}
Confirmed policy: {damaged_wrong_missing.process — cite if confirmed}
Proposed fix: {replacement via Tarlu (qty, SKU) / refund £X / both}
Cap check: {if refund, amount vs refund_cap_gbp}
```

**Once approved:** raise the replacement in Tarlu per the SOP, then confirm to the customer with the new order/tracking. (SOP pending the Loom — do not action until it's filled in.)
