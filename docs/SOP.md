# Fan Decor CS Agent — Standard Operating Procedure

**Owner:** Dom (COO) · **Approver (money/escalations):** Jamie Sharp · **Channel home:** `#fan-decor-cs-agent`
**Status:** built, dry-run proven. Go-live pending: Anthropic credit + per-channel `status: live` flip.

This is the operating guide for the team. The agent handles the bulk of Fan Decor customer service;
humans handle money, escalations, and the physical side of returns.

---

## 1. What the agent does (every 30 min, 07:00–19:00 UK)
For each new customer message on a live channel it:
1. **Triages** it into one of 9 categories (WISMO, delivery, sizing, order change/cancel, returns, refund, damaged/wrong/missing, complaint, spam).
2. **Looks up** the order in Shopify (and the channel's order system).
3. **Decides** the action from the autonomy rules + guardrails.
4. **Drafts or sends** a reply in Fan Decor brand voice, personalised with the real order detail.
5. **Logs** every action to ClickUp (audit trail) and **pings Slack only when a human is needed.**

Models: **Haiku** triages, **Sonnet** drafts. Cheap and fast.

## 2. What gets auto-sent vs. held (current mode: `send_non_money`)
| Category | Action |
|---|---|
| WISMO, delivery status, returns process, sizing*, order-detail change | **Auto-send** (no money, policy confirmed) |
| Refund request, damaged/wrong/missing | **Held — needs Jamie's approval** (money) |
| Complaint / legal / chargeback / large order | **Escalated — same-minute Slack ping** |
| Spam | Closed, no reply |

\* A reply auto-sends **only if** every policy value it quotes is confirmed. Unconfirmed → it becomes a draft.

## 3. The human's job (you + Jamie)
- **Approvals:** when the agent pings `#fan-decor-cs-agent` for a refund/return, Jamie reviews the
  recommendation (amount, policy check, cap check) and approves or declines. Refund cap **£35**; anything
  above is never auto, ever.
- **Escalations:** an angry customer / legal threat / chargeback gets pinged immediately — a human takes over.
- **Returns — the physical step:** when a returned parcel arrives, someone marks the ClickUp task
  "Received & inspected." Only then does the refund/replacement proceed (the agent can't verify a physical parcel).
- Everything else, the agent handles and just reports in the daily brief.

## 4. Cadence (deliberately light)
- **Daily brief, 08:00, one Slack message:** volume by channel/category, auto-resolved count, items
  awaiting approval, escalations, refunds pending/processed, SLA risks.
- **Pings only when action is needed** (approval or escalation) — never for clean auto-resolves.
- We start **daily**; as the agent proves itself we move the brief to **every few days / ad hoc**. The
  approval-edit rate (how often a human changes a draft) is the signal to dial back oversight.

## 5. Where things live
- **Slack `#fan-decor-cs-agent`** — approvals, escalations, daily brief.
- **ClickUp "CS Agent — Log & Escalations"** — audit trail of every action.
- **ClickUp "Returns & Refunds Register"** — the return lifecycle (Requested → Instructions sent →
  Awaiting item → Received & inspected → Refund pending → Resolved). 14-day refund SLA from receipt.
- **GitHub `dom-tldragency/fandecor-cs-agent`** — the code + config; runs as a scheduled cloud worker.

## 6. Channels
- **Email (`customerservice@` + `marketing@fandecor.com`)** — LIVE-ready (Gmail service account). First to go live.
- **TikTok Shop** — connector built; waiting on Partner Center app approval + tokens.
- **Meta (IG + Messenger)** — connector built; waiting on Meta app + review.
- **Shopify** — order-lookup backbone (live), used by all channels.

## 7. Autonomy phases (earn trust; money always gated)
1. **Phase 1 — draft only** (where we start; `DRY_RUN=true`).
2. **Phase 2 — auto-send routine replies** (WISMO/tracking/FAQ); refunds/returns still human-approved. ← target after the first clean days.
3. **Phase 3 — auto-process refunds under £35**; above stays gated, always.
Advance only when the approval-edit rate is consistently low.

## 8. Guardrails (non-negotiable)
- Never a refund/payment over £35, or any refund without approval below Phase 3.
- Never promise outside confirmed policy (delivery dates, refund windows). Escalate instead.
- Never act on suspected fraud/chargeback — flag it.
- Never argue; de-escalate; brand-safe always.
- Every action logged.

## 9. Go-live & rollback
- **Go live:** add Anthropic credit → set the channel `status: live` → uncomment the workflow `schedule:` →
  dry-run dispatch to review drafts → set `DRY_RUN=false`. (Full steps in `DEPLOY.md`.)
- **Rollback (instant):** set `DRY_RUN=true` or disable the workflow — all outbound actions stop immediately.
