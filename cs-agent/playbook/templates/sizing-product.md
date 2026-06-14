# Template — Sizing / product question

**Action:** auto_send **only if** `policies.sizing.confirmed` (and the specific product detail is known); else **draft**.
**Inputs:** product/SKU, size chart link, variant info from Shopify product data.

---

### Sizing question
> Hi {first_name},
>
> Great question! For the **{product_name}**, {sizing_guidance_from_confirmed_policy}.
> Here's the full size guide so you can pick with confidence: {size_chart_link}
>
> If you let me know your usual size/measurements I'm happy to recommend the best fit.
>
> {sign_off}

### General product question (in stock / material / team / print)
> Hi {first_name},
>
> Thanks for getting in touch! {answer_from_shopify_product_data}.
> {availability_note — from live Shopify inventory}.
>
> Anything else you'd like to know before you order? Happy to help.
>
> {sign_off}

**Guardrail:** if sizing policy is unconfirmed, do **not** invent fit advice — draft it and let a human confirm, or answer only the parts backed by live Shopify product data.
