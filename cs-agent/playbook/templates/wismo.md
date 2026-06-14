# Template — WISMO (where is my order)

**Action:** auto_send (pure Shopify read; quotes no policy beyond live tracking).
**Inputs:** order status, fulfilment status, tracking number + URL, carrier, order date.

---

### If shipped + tracking available
> Hi {first_name},
>
> Thanks for the message — good news, your order **{order_number}** is on its way! 🎉
> It's with {carrier} and you can track it live here: {tracking_url}
> Latest update: {tracking_status}.
>
> If anything looks off with the tracking, just reply here and I'll chase it for you.
>
> {sign_off}

### If still being prepared (paid, not yet fulfilled)
> Hi {first_name},
>
> Thanks for checking in on order **{order_number}**! It's confirmed and being prepared for dispatch right now. As soon as it's picked up by the courier you'll get a tracking link by email.
>
> {— only state an expected timeframe if policies.shipping_uk/intl.confirmed; otherwise omit —}
>
> {sign_off}

### If no order found
> Hi {first_name},
>
> Happy to track that down for you! I couldn't find an order from the details I have — could you reply with your **order number** (looks like #1234) or the **email** you used at checkout? I'll get you an update straight away.
>
> {sign_off}
