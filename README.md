# Fan Decor Customer Service Agent

A channel-agnostic, always-on customer service agent for **Fan Decor** (football merch DTC, Shopify + TikTok Shop, GBP/UK), built to be **reusable across future TL;DR brands** by swapping one config file.

> Built per `Projects/Ops/TLDR_FanDecor_CS_Agent_BuildBrief.md`. This implementation uses the **lean Claude-Code-native architecture** (skill brain + scheduled routine + already-connected MCP tools) rather than a standalone app.

---

## How it works (architecture)

```
                         ┌─────────────────────────────┐
   Inbound channels      │      SHARED CORE (brain)     │
   ─────────────────     │   cs-agent/SKILL.md          │
   Email (Gmail)    ┐    │   1. triage / classify       │
   Shopify Inbox    ┤    │   2. order + customer lookup │
   TikTok Seller    ┼──▶ │   3. draft / send reply      │ ──▶  Slack pings (approval/escalation)
   Meta / IG DMs    ┘    │   4. act within guardrails   │      ClickUp log (audit trail)
   (each = adapter)      │   5. escalate                │      Daily 8am brief (Slack)
                         └─────────────────────────────┘
```

- **One brain, many channels.** Every channel feeds the *same* triage → lookup → respond/act → log → escalate pipeline. Channels are swappable **adapters** (`cs-agent/adapters/`) that all expose the same interface, so the core logic is written once.
- **The LLM is the runtime.** Most of this repo is markdown (playbook, templates, policies, SOPs) + config. A scheduled cloud routine reads it and acts using connected MCP tools. This keeps it auditable and portable.
- **Reusable by design.** Brand voice, policies, refund cap and approver live in `cs-agent/config/brand.fandecor.yaml`. To launch a new brand, copy that file (e.g. `brand.<newbrand>.yaml`) and point the routine at it. The core never changes.

## Repo layout

```
cs-agent/
  SKILL.md                     # the CS brain — the pipeline the routine follows
  config/
    brand.fandecor.yaml        # voice, policies (PLACEHOLDERS), refund cap, approver
    channels.yaml              # which channels are enabled / connected / stubbed
    autonomy.yaml              # phase + per-category send rules (currently: send non-money)
  playbook/
    triage.md                  # classification taxonomy + routing
    guardrails.md              # the hard rules (money gating, escalation, PII)
    templates/                 # one brand-voice template per category
    sops/tarlu-raise-order.md  # how to raise a replacement order (awaiting Loom)
  adapters/
    README.md                  # the adapter interface contract
    email.md  shopify-inbox.md  tiktok-seller.md  meta-ig.md
  evals/
    sample-messages.jsonl      # sample FD messages per category
    run-evals.md               # how to score triage + draft quality
  routines/
    poll-and-respond.md        # the scheduled per-cycle routine prompt
    daily-brief.md             # the 8am Slack brief prompt
```

## Current status (as of 2026-06-14)

| Integration | Status | Notes |
|---|---|---|
| Shopify Admin (Fan Decor) | ✅ **Connected** | Orders, customers, fulfilment, refunds. Wired first. |
| Slack `#fan-decor-cs-agent` | ✅ **Connected** | Team home: approvals, escalations, daily brief. |
| ClickUp | ✅ **Connected** | Audit log + escalation queue (list created on first run). |
| Email `marketing@fandecor.com` | ⛔ **Not connected** | Connected mailbox is `dom@tl-dr.agency`. **Action: connect the FD mailbox** (see Action items). Until then, email runs as a stub. |
| TikTok Shop **Seller** API | ⛔ **Not connected** | Only the affiliate/creator TikTok tool is connected. Stubbed behind the adapter interface. |
| Meta / Instagram DMs | ⛔ **Not connected** | Stubbed behind the adapter interface. |

## Autonomy (current)

**Mode: `send_non_money`** (your choice). See `cs-agent/config/autonomy.yaml`.
- Money (refunds/payments) is **always** human-approved — hard rule, never auto.
- A reply auto-sends **only if every policy value it quotes is confirmed** in the brand config. Anything quoting an unconfirmed placeholder falls back to a draft for approval.
- Complaints / legal / chargebacks / large or influencer orders → **immediate Slack escalation**, never auto-sent.

## Action items for Dom (blockers to full go-live)

1. **Connect `marketing@fandecor.com`** as a Google account so the agent can read/draft/send FD customer mail.
2. **Confirm the policy placeholders** in `cs-agent/config/brand.fandecor.yaml` (shipping times, returns window, refund policy, cancellation window, sizing, refund cap, named approver, brand voice). Each is marked `CONFIRM:`.
3. **Send the Tarlu order-raising Loom** — paste the auto-transcript + screenshots into the chat; I'll fill `cs-agent/playbook/sops/tarlu-raise-order.md`.
4. Later: TikTok Shop Seller API + Meta Graph API credentials to activate those adapters.
