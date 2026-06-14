# Fan Decor CS Agent — cloud runtime

The **always-on body** for the CS agent. Runs server-side (no Mac dependency), polls each live channel,
triages + drafts replies via the Claude API using the playbook in `../cs-agent/`, acts via each channel's
API, and logs to Slack + ClickUp.

## Why this shape
- **Always-on requirement** (Dom): must run without his Mac open. A hosted worker meets that; the local
  Claude schedulers do not.
- **Custom connector required:** there is no off-the-shelf TikTok Shop Seller connector (checked the MCP
  registry + Zapier — only TikTok *ads* tools exist). So we build, and a self-contained worker is the
  cleanest thing to host.
- **Host-agnostic:** default runtime is a **GitHub Actions scheduled workflow** (same pattern as
  `tldr-cash-sheet`). The identical code lifts onto Cloud Run / Railway later if we want webhooks or
  stronger uptime guarantees.

## Runtime loop (per cycle)
1. Load `../cs-agent/config/*` (brand, autonomy, channels) + the playbook/templates.
2. For each channel with `status: live`, `fetch_new()` via its adapter.
3. For each message: triage → Shopify (and channel) order lookup → decide action (autonomy + guardrails)
   → draft/send/escalate/close via the Claude API + channel adapter.
4. Log to ClickUp (audit list 901615395458 / returns list 901615395484); Slack only when a human is needed.

## Intended layout
```
runtime/
  README.md                ← this file
  main.py                  ← the cycle loop (config-driven, channel-agnostic)  [to build]
  config_loader.py         ← reads ../cs-agent/config/*.yaml                    [testable now]
  llm.py                   ← Claude API calls for triage + drafting             [testable now]
  adapters/
    base.py                ← the adapter interface (fetch_new/send/draft/status)
    shopify.py             ← order lookup (live)                                [buildable now]
    tiktok_seller.py       ← TikTok Shop Partner API client                     [needs creds]
    email_gmail.py         ← Gmail API client                                   [needs creds]
  notify/ slack.py clickup.py                                                    [buildable now]
```

## Secrets (stored as GitHub Actions secrets, never in code)
`ANTHROPIC_API_KEY`, `SHOPIFY_ADMIN_TOKEN`, `SLACK_BOT_TOKEN`, `CLICKUP_TOKEN`,
`TIKTOK_APP_KEY` `TIKTOK_APP_SECRET` `TIKTOK_ACCESS_TOKEN` `TIKTOK_REFRESH_TOKEN` `TIKTOK_SHOP_CIPHER`,
`GMAIL_SERVICE_ACCOUNT_JSON` (base64).

## Schedule
`.github/workflows/cs-agent.yml` — every 30 min during UK working hours. GitHub cron is **UTC**; the window
is set wide enough to cover 07:00–19:00 London across BST/GMT, and `main.py` enforces the exact
Europe/London 07:00–19:00 window so DST never matters.

## Build status / critical path
The **one true blocker is TikTok API credentials** (Partner Center app + shop authorisation — Dom owns the
shop, starting from zero, app review takes days). The connector body is written **against the authenticated
API once creds exist** — writing it blind would be guesswork we'd redo. Everything that doesn't need creds
(loop, config, Slack/ClickUp, Shopify lookup) is built first so the worker runs end-to-end with stubs, and
each channel is a single file we fill when its credentials land.
