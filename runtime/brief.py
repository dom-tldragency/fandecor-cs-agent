"""Daily 8am CS brief — compiles the last 24h from the ClickUp CS list and posts one Slack message.

Run: python -m runtime.brief    (DRY_RUN prints instead of posting)
"""
from __future__ import annotations

import os
import time
from collections import Counter
from typing import Any, Dict, List

import requests

from .notify.slack import Slack

API = "https://api.clickup.com/api/v2"


def _recent_tasks(list_id: str, since_ms: int) -> List[Dict[str, Any]]:
    token = os.environ.get("CLICKUP_TOKEN", "")
    if not token:
        return []
    r = requests.get(
        f"{API}/list/{list_id}/task",
        headers={"Authorization": token},
        params={"date_created_gt": since_ms, "subtasks": "true", "include_closed": "true"},
        timeout=20,
    )
    r.raise_for_status()
    return r.json().get("tasks", [])


def _tally(tasks: List[Dict[str, Any]]) -> Dict[str, Counter]:
    by_action: Counter = Counter()
    by_category: Counter = Counter()
    for t in tasks:
        # task name format: "[channel] category · order · action"
        name = t.get("name", "")
        if "]" in name:
            rest = name.split("]", 1)[1].strip()
            parts = [p.strip() for p in rest.split("·")]
            if parts:
                by_category[parts[0]] += 1
            if len(parts) >= 3:
                by_action[parts[-1]] += 1
    return {"action": by_action, "category": by_category}


def build_and_post() -> Dict[str, Any]:
    list_id = os.environ.get("CLICKUP_LIST_ID", "901615395458")
    since = int((time.time() - 24 * 3600) * 1000)
    tasks = _recent_tasks(list_id, since)
    if not tasks:
        # Quiet day — one-liner, not a full report.
        return Slack().post("☀️ *Frankie* — all quiet overnight, nothing new to report. Nothing needs you 👍")
    tallies = _tally(tasks)
    act, cat = tallies["action"], tallies["category"]

    awaiting = sum(v for k, v in act.items() if k.startswith("drafted"))
    escal = act.get("escalated", 0)
    auto = act.get("auto_sent", 0)
    text = (
        f"☀️ *Frankie — Daily Brief*\n"
        f"📥 Volume (24h): *{len(tasks)}* handled\n"
        f"   by category: " + (" · ".join(f"{k} {v}" for k, v in cat.most_common()) or "—") + "\n"
        f"✅ Auto-resolved: {auto}   ✍️ Awaiting approval: {awaiting}   🚨 Escalations: {escal}\n"
        f"🔧 Blockers: email + TikTok channels awaiting API credentials (see DEPLOY.md)"
    )
    return Slack().post(text)


if __name__ == "__main__":
    build_and_post()
