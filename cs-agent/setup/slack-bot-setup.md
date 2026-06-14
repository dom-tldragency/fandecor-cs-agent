# Setup — Slack bot token for the cloud worker

The cloud worker posts approvals/escalations/the daily brief to `#fan-decor-cs-agent` (C0BAD4YQ80M).
It needs its own bot token (the in-session Slack connector doesn't travel to the cloud worker).

## Steps
1. Go to **api.slack.com/apps → Create New App → From scratch**. Name: `Fan Decor CS Agent`. Pick the TL;DR workspace.
2. **OAuth & Permissions → Bot Token Scopes** → add:
   - `chat:write` (post messages)
   - `chat:write.customize` (optional — post as the agent name/icon)
3. **Install to Workspace** → authorise. Copy the **Bot User OAuth Token** (`xoxb-…`).
4. In Slack, invite the bot to the channel: `/invite @Fan Decor CS Agent` in `#fan-decor-cs-agent`.
5. Store the token as the `SLACK_BOT_TOKEN` secret (see DEPLOY.md). `SLACK_CHANNEL_ID` is already `C0BAD4YQ80M`.

That's all the worker needs for notifications.
