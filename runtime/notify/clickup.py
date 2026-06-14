"""ClickUp audit log + escalation/approval queue.

Every CS action becomes/updates a task in the CS list (audit trail). Returns get a task in the
Returns & Refunds Register and move through the lifecycle (see cs-agent/playbook/sops/returns-lifecycle.md).
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

API = "https://api.clickup.com/api/v2"


class ClickUp:
    def __init__(self) -> None:
        self.token = os.environ.get("CLICKUP_TOKEN", "")
        self.list_id = os.environ.get("CLICKUP_LIST_ID", "901615395458")
        self.returns_list_id = os.environ.get("CLICKUP_RETURNS_LIST_ID", "901615395484")
        self.dry_run = os.environ.get("DRY_RUN", "true").lower() != "false"

    def log_action(self, *, category: str, order: str, channel: str, action: str,
                   detail: str = "", returns: bool = False) -> Dict[str, Any]:
        """Create an audit task for a handled message."""
        name = f"[{channel}] {category} · {order or 'no-order'} · {action}"
        body = (
            f"**Category:** {category}\n**Order:** {order}\n**Channel:** {channel}\n"
            f"**Action:** {action}\n**Detail:** {detail}\n"
        )
        return self._create_task(self.returns_list_id if returns else self.list_id, name, body)

    def _create_task(self, list_id: str, name: str, markdown: str) -> Dict[str, Any]:
        if self.dry_run or not self.token:
            print(f"[DRY_RUN clickup] task in {list_id}: {name}")
            return {"dry_run": True, "name": name}
        r = requests.post(
            f"{API}/list/{list_id}/task",
            headers={"Authorization": self.token, "Content-Type": "application/json"},
            json={"name": name, "markdown_description": markdown},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
