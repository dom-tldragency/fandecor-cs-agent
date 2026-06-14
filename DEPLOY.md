# Deploy / go-live runbook — Fan Decor CS Agent

The build is **not live**. This is the checklist to take it live when you're ready. Nothing here runs
customer-facing actions until the final step.

## 0. Prerequisites (the slow ones — start early)
- [ ] TikTok Shop Partner app **approved** + Fan Decor shop **authorised** → access/refresh tokens + shop_cipher (`cs-agent/setup/tiktok-shop-seller-api-access.md`)
- [ ] Gmail service-account JSON for the FD mailbox(es) (`cs-agent/setup/google-gmail-api-access.md`)
- [ ] Slack bot token (`cs-agent/setup/slack-bot-setup.md`)
- [ ] ClickUp API token (`cs-agent/setup/clickup-token-setup.md`)
- [ ] Shopify Admin API token (custom app on the FD store, read_orders/read_customers; refunds later)
- [ ] Anthropic API key

## 1. Create the repo + push (needs your GitHub auth — `gh` not installed on this machine)
```bash
# from the project root
gh repo create dom-tldragency/fandecor-cs-agent --private --source . --remote origin --push
# or: create the repo in the UI, then:
#   git remote add origin git@github.com:dom-tldragency/fandecor-cs-agent.git && git push -u origin main
```

## 2. Set the secrets (NEVER commit these)
`gh` is **not installed** on the build machine, so add these via the repo's
**Settings → Secrets and variables → Actions → New repository secret**. Add the value directly in the UI —
don't route secrets through chat/logs.

| Secret | Where to get it | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys | the agent's brain (triage + drafting) |
| `SHOPIFY_ADMIN_TOKEN` | FD Shopify admin → Settings → Apps → **Develop apps** → create custom app → Admin API token | scopes: `read_orders`, `read_customers` (add `read_fulfillments`; refund write later) |
| `SLACK_BOT_TOKEN` | the Slack app (`cs-agent/setup/slack-bot-setup.md`) | `xoxb-…`, scope `chat:write` |
| `CLICKUP_TOKEN` | ClickUp → Settings → Apps → API Token | `pk_…` |
| `TIKTOK_APP_KEY` | TikTok Partner Center app | `6kam07mo727sq` (not sensitive) |
| `TIKTOK_APP_SECRET` | TikTok Partner Center app | 🔐 **rotate first** — was shared in chat |
| `TIKTOK_ACCESS_TOKEN` / `TIKTOK_REFRESH_TOKEN` / `TIKTOK_SHOP_CIPHER` | after app approval + shop auth | minted by us from the auth_code |
| `GMAIL_SERVICE_ACCOUNT_JSON` | the service-account key, **base64-encoded** | ✅ done. `base64 -i key.json \| pbcopy` |
| `META_PAGE_ACCESS_TOKEN` / `META_IG_ID` / `META_PAGE_ID` | after Meta app review | for IG + Messenger |

**Optional repo *variable* (not a secret):** `DRY_RUN` — leave unset/`true` to keep drafting-only; set `false` only when going live.

## 3. Verify safely (still not live)
- The GitHub workflow runs with `DRY_RUN` defaulting to **true** — every "send" is printed, nothing goes
  out. Trigger a manual run (`workflow_dispatch`) and read the logs.
- Flip a channel to `status: live` in `cs-agent/config/channels.yaml` only once its credentials are set.

## 4. Go live (per channel, when trust is earned)
1. Set the channel `status: live` in `cs-agent/config/channels.yaml`.
2. **Enable the cron:** uncomment the `schedule:` blocks in `.github/workflows/cs-agent.yml` and
   `cs-brief.yml` (they're commented out so nothing auto-runs until you choose to). Push.
3. Run a `workflow_dispatch` with `DRY_RUN=true` and confirm the drafts look right.
4. Set repo variable `DRY_RUN=false` to allow real sends (money stays gated regardless).
5. Watch the daily brief + approval-edit rate; advance autonomy per `cs-agent/config/autonomy.yaml`.

## Rollback
Set `DRY_RUN=true` (or disable the workflow) — instantly stops all outbound actions.
