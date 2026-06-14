# Triage / classification

Classify every inbound message into exactly **one** primary category. If a message spans two,
pick the one with the highest risk/urgency (escalation > money > policy > factual).

| Category | Signals | Default action* |
|---|---|---|
| `wismo` | "where is my order", "has it shipped", "tracking", "not arrived yet" (within window) | auto_send |
| `delivery_issue` | "tracking says delivered but nothing", "stuck", "returned to sender", late beyond window | auto_send → escalate if a promise/refund is needed |
| `sizing_product` | "what size", "does it fit", "is it the home kit", material/print/product questions pre-purchase | auto_send (draft until sizing confirmed) |
| `order_change_cancel` | "change my address", "wrong size ordered", "cancel my order" (pre-fulfilment) | auto_send confirm → gated if refund |
| `returns_exchange` | "how do I return", "want to exchange", "send it back" | auto_send (draft until returns confirmed) |
| `refund_request` | "I want a refund", "money back", "refund me" | **gated (money)** |
| `damaged_wrong_missing` | "arrived damaged", "wrong item", "missing from order", "faulty print" | **gated** (replacement via Tarlu / refund) |
| `complaint_escalation` | angry tone, threats, "terrible", legal mention, chargeback, repeat unresolved | **escalate (immediate Slack)** |
| `spam` | marketing, phishing, irrelevant, bots | close |

\* Default action is the *starting point*; `config/autonomy.yaml` is the source of truth and applies
the policy-confirmation and money downgrades.

## What to extract on every message
- `order_number` (e.g. #1234) and/or customer email
- `customer_name`
- `product` / SKU mentioned
- `sentiment`: positive / neutral / negative / angry
- `urgency`: any deadline, event date (football fans often need kit before a match!), or SLA risk
- `channel`: which adapter it came from

## Routing notes
- **No order found?** Don't guess. Ask for the order number / email in the reply (still a valid auto_send for `wismo` since it quotes no policy).
- **Match-date urgency** (e.g. "need it for Saturday's game") raises urgency — surface in the brief and, if it can't be met within confirmed shipping times, escalate rather than promise.
- **Two customers, one thread / forwarded chains** — treat the latest customer message as the trigger.
