"""Slack notifications — approvals + escalations + daily brief to #fan-decor-cs-agent.

Only pings when a human is needed (approval/escalation); clean auto-resolves roll into the daily brief.
"""
from __future__ import annotations

import os
from typing import Optional

import requests


class Slack:
    def __init__(self) -> None:
        self.token = os.environ.get("SLACK_BOT_TOKEN", "")
        self.channel = os.environ.get("SLACK_CHANNEL_ID", "C0BAD4YQ80M")
        self.dry_run = os.environ.get("DRY_RUN", "true").lower() != "false"

    def post(self, text: str, thread_ts: Optional[str] = None) -> dict:
        if self.dry_run or not self.token:
            print(f"[DRY_RUN slack] {text}")
            return {"dry_run": True}
        r = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"channel": self.channel, "text": text, "thread_ts": thread_ts},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

    def approval_request(self, summary: str, approver_slack_id: str) -> dict:
        ping = f"<@{approver_slack_id}>" if approver_slack_id else ""
        return self.post(f"✍️ *Approval needed*\n{summary}\n{ping}")

    def escalation(self, summary: str, approver_slack_id: str) -> dict:
        ping = f"<@{approver_slack_id}>" if approver_slack_id else ""
        return self.post(f"🚨 *ESCALATION*\n{summary}\n{ping}")
