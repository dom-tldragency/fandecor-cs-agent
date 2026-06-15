# Frankie — Fan Decor Customer Service Agent (SOP)

**Who:** Frankie is Fan Decor's always-on customer service agent. **Owner:** Dom (COO) ·
**Money approver:** Jamie Sharp · **CS operator:** Camilla · **Home:** Slack `#fan-decor-cs-agent` ·
**Code:** `github.com/dom-tldragency/fandecor-cs-agent`
**Status:** built + tested in draft mode. Not live yet — go-live pending final sign-off.

Frankie handles the bulk of customer service. Humans handle money, the physical side of returns, and
anything Frankie escalates.

---

## 1. What Frankie does (every 30 min, 07:00–19:00 UK)
For each new customer message on a live channel: **triage** → **look up the order in Shopify** →
**decide** (per autonomy + guardrails) → **draft or send** a brand-voice reply with the real order
detail → **log to ClickUp** + **ping Slack only if a human is needed**. Reads the **whole email thread**
for context on ongoing conversations. Models: Haiku triages, Sonnet drafts.

## 2. Voice
Warm, human, football-fan friendly — signs off as **Frankie**. Apologetic but **measured, never gushing**
(no "genuinely gutting" etc.). Never argues, never blames the customer, never promises outside policy.

## 3. What's auto vs. held (current mode: send non-money)
- **Auto-send:** WISMO/tracking, delivery status, returns process, sizing, order-detail changes.
- **Held for Jamie (money):** refund requests, damaged/wrong/missing.
- **Escalated (instant Slack, never auto-replied):** complaints, legal, chargebacks, large/influencer orders.
- **Closed, no reply:** spam.
- A reply auto-sends only if every policy value it quotes is confirmed; otherwise it becomes a draft.

## 4. How you work with Frankie
- **Jamie — approvals.** Frankie pings you + tasks you on refunds/returns. Cap **£35**; above is never auto, ever.
- **Camilla — CS operator.** Frankie tasks you for returns + replacements (e.g. raising one in Tarlu).
- **Closing a case (you drive Frankie from ClickUp):** one task per customer. When you've actioned
  something Frankie didn't finish, comment on the task:
  - `REPLY: your replacement's on the way, tracking ABC123` → Frankie sends that to the customer on the
    original thread **and closes the task**.
  - `CLOSE` → Frankie just closes it.
- **Refunds close themselves:** once you process the refund in Shopify, Frankie spots it, confirms to the
  customer, and closes the task — no comment needed.
- **Returns — physical step:** when a parcel arrives back, mark the ClickUp task "received & inspected";
  only then does the refund/replacement proceed (Frankie can't verify a physical parcel).

## 5. One task per conversation
Everything is **one ClickUp task per customer conversation**, updated with comments as it progresses and
closed when complete. Frankie **pings Slack only the first time** a conversation needs a human — follow-ups
update the task and roll into the daily brief. No per-reply spam. Nothing slips: if a customer replies
after a case is "closed", the thread reopens and Frankie re-triages/re-escalates.

## 6. Cadence (deliberately light)
- **Daily 8am Slack brief:** volume, what Frankie auto-resolved, what's awaiting approval, escalations,
  refunds pending/processed, SLA risks.
- **Pings only when a human's needed.** Start daily → dial back to ad-hoc as trust builds.

## 7. Where things live
Slack `#fan-decor-cs-agent` (approvals/escalations/brief) · ClickUp "CS Agent — Log & Escalations"
(audit) + "Returns & Refunds Register" (return lifecycle, 14-day refund SLA) · GitHub repo (code, runs
as a scheduled cloud worker).

## 8. Channels
Email (`customerservice@` + `marketing@fandecor.com`) — live-ready, first to go live. TikTok Shop + Meta
(IG/Messenger) — connectors built, awaiting API approvals. Shopify — order-lookup backbone.

## 9. Guardrails (non-negotiable)
Never a refund/payment over £35 or without approval (below Phase 3) · never promise outside confirmed
policy · never act on fraud/chargeback (flag it) · never argue · everything logged.

## 10. Go-live & rollback
Go live: confirm the inbox trigger → set channel `status: live` → enable the workflow schedule →
dry-run review → set `DRY_RUN=false`. Rollback instantly: `DRY_RUN=true` or disable the workflow — all
outbound stops. (Full steps: `DEPLOY.md`.)
