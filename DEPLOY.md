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
```bash
gh secret set ANTHROPIC_API_KEY            --repo dom-tldragency/fandecor-cs-agent
gh secret set SHOPIFY_ADMIN_TOKEN          --repo dom-tldragency/fandecor-cs-agent
gh secret set SLACK_BOT_TOKEN              --repo dom-tldragency/fandecor-cs-agent
gh secret set CLICKUP_TOKEN                --repo dom-tldragency/fandecor-cs-agent
gh secret set TIKTOK_APP_KEY               --repo dom-tldragency/fandecor-cs-agent   # 6kam07mo727sq
gh secret set TIKTOK_APP_SECRET            --repo dom-tldragency/fandecor-cs-agent   # rotate this — it was shared in chat
gh secret set TIKTOK_ACCESS_TOKEN          --repo dom-tldragency/fandecor-cs-agent   # after shop auth
gh secret set TIKTOK_REFRESH_TOKEN         --repo dom-tldragency/fandecor-cs-agent
gh secret set TIKTOK_SHOP_CIPHER           --repo dom-tldragency/fandecor-cs-agent
gh secret set GMAIL_SERVICE_ACCOUNT_JSON   --repo dom-tldragency/fandecor-cs-agent   # base64 of the JSON
```

## 3. Verify safely (still not live)
- The GitHub workflow runs with `DRY_RUN` defaulting to **true** — every "send" is printed, nothing goes
  out. Trigger a manual run (`workflow_dispatch`) and read the logs.
- Flip a channel to `status: live` in `cs-agent/config/channels.yaml` only once its credentials are set.

## 4. Go live (per channel, when trust is earned)
1. Set the channel `status: live`.
2. Run a `workflow_dispatch` with `DRY_RUN=true` and confirm the drafts look right.
3. Set repo variable `DRY_RUN=false` to allow real sends (money stays gated regardless).
4. Watch the daily brief + approval-edit rate; advance autonomy per `cs-agent/config/autonomy.yaml`.

## Rollback
Set `DRY_RUN=true` (or disable the workflow) — instantly stops all outbound actions.
