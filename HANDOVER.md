# Fan Decor CS Agent — Morning Handover (built overnight 2026-06-14)

Good morning. Here's exactly where this is and what's left. **It's one top-up away from going live.**

## TL;DR
The agent is built, deployed to GitHub, and the **email pipeline is proven end-to-end in the cloud**
(authenticated Gmail → read a real inbox → reached drafting). Slack, ClickUp, the SOP, and the cadence
are all set up. **The only blocker is Anthropic API credit** (a payment — your call). Add it and we go live.

## What I did while you slept
- **Models:** switched the agent to **Haiku (triage) + Sonnet (drafting)** — cheaper/faster, Opus dropped. Configurable via `CS_TRIAGE_MODEL` / `CS_DRAFT_MODEL`.
- **Slack:** created the "Fan Decor CS Agent" Slack app + an **incoming webhook** bound to `#fan-decor-cs-agent`, stored as the `SLACK_WEBHOOK_URL` secret. **Tested — posted the handover + notification examples to the channel** (go look 👀).
- **SOP:** written into the **TLDR Brands Wiki → "3. The Engine" → "Fan Decor CS Agent — SOP"**, and in the repo at `docs/SOP.md`.
- **ClickUp:** "📌 START HERE" reference task pinned in the CS Log list; audit + Returns registers live.
- **Hardening:** per-message error isolation (one bad message can't crash a cycle); Gmail key now accepts raw JSON or base64.
- All committed/pushed to `github.com/dom-tldragency/fandecor-cs-agent`. **Scheduled runs remain OFF** (manual-only) so nothing is live yet.

## Secrets in GitHub (done ✅)
`ANTHROPIC_API_KEY` · `SHOPIFY_ADMIN_TOKEN` · `GMAIL_SERVICE_ACCOUNT_JSON` · `CLICKUP_TOKEN` · `SLACK_WEBHOOK_URL`
Still pending (after their app reviews): `TIKTOK_*` tokens, `META_*` tokens.

## To go live (≈10 min, together)
1. **Add Anthropic credit** — console.anthropic.com → Billing (a few £).
2. We run a **dry-run** (`Actions → Fan Decor CS Agent → Run workflow`, `dry_run=true`) and **read the real drafts together**.
3. If the drafts look right: enable the schedule (uncomment `schedule:` in `.github/workflows/cs-agent.yml` + `cs-brief.yml`) and set the `DRY_RUN` repo variable to `false`.
4. Email is then live, auto-sending the safe categories, money gated (refunds ≤£35 → Jamie).

## Housekeeping (when you have a sec)
- 🔐 **Rotate** the credentials that passed through chat earlier: the TikTok app secret, the Shopify `shpat_` token, and ideally regenerate the Slack webhook. None are critical (read-scoped / single-channel), but good hygiene.
- TikTok + Meta: keep their app reviews moving; I'll wire the tokens when they land.

## Channels status
| Channel | Status |
|---|---|
| Email (customerservice@ + marketing@) | ✅ live-ready — first to go live |
| Shopify (order lookup) | ✅ live backbone |
| TikTok Shop | connector built, awaiting Partner API approval |
| Meta (IG + Messenger) | connector built, awaiting Meta app review |

Nothing's been sent to a customer. Everything's safe and reversible (`DRY_RUN=true` or disable the workflow stops it instantly).
