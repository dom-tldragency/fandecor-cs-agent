# SOP — Returns & refunds lifecycle (closing the loop)

A return is long-running and multi-step, unlike a one-shot WISMO reply. It gets its own task in the
**ClickUp "Returns & Refunds Register"** (list_id 901615395484) — the system of record — and is advanced
through these stages. The agent owns the comms + tracking; humans own the physical receipt + the money.

## Stages (each task moves through these)
| # | Stage | Who advances it | What happens |
|---|---|---|---|
| 1 | **Requested** | Agent (auto) | Customer asks to return/refund. Agent creates the task, logs order #, item, reason, channel, value. |
| 2 | **Instructions sent** | Agent (auto) | Agent replies with the returns process (365-day window, unused/original packaging, who pays postage). Task → this stage. |
| 3 | **Awaiting item** | — (timer) | Waiting for the parcel to come back. Agent sets a follow-up; nudges the customer if stale. |
| 4 | **Received & inspected** | **Human / warehouse** | Someone physically receives + checks the item. They mark the task received (the agent can't verify a physical parcel). |
| 5 | **Refund/exchange pending approval** | Agent drafts → **Jamie Sharp approves** | Agent posts the refund recommendation (amount, channel, policy + cap check) to Slack + task. Money is gated. |
| 6 | **Resolved** | Agent (after approval) | Refund processed **on the original channel** (Shopify refund / TikTok Shop refund), or replacement raised in Tarlu. Agent confirms to the customer and closes the task. |

## Rules that keep the loop closed
- **Refund SLA: 14 days** from "Received & inspected" (the published promise). The task carries a due date; SLA risk surfaces in the daily brief.
- **Refund channel = purchase channel.** Bought on TikTok → refund via TikTok Shop. Bought on Shopify → refund via Shopify. Never cross-refund.
- **Money is gated.** No refund is processed without Jamie Sharp's approval (and never above £35 auto, even at Phase 3).
- **Nothing sits in "Awaiting item" forever.** If no parcel after a sensible window, agent nudges once, then flags for a human decision.
- **Exchanges** follow the same flow but stage 6 = raise the replacement (Tarlu) instead of refunding.
- Wall art is **non-returnable** (made to order) — if a wall-art return is requested, explain politely and close, unless damaged/faulty (then it's the damaged flow).

## Daily brief pulls from this list
The 8am brief counts: returns requested / awaiting item / pending approval / resolved, refunds pending (£) vs processed, and any return breaching the 14-day SLA.
