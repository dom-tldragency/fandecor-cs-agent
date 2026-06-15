"""ClickUp audit log + escalation/approval queue.

Every CS action becomes/updates a task in the CS list (audit trail). Returns get a task in the
Returns & Refunds Register and move through the lifecycle (see cs-agent/playbook/sops/returns-lifecycle.md).
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import requests

API = "https://api.clickup.com/api/v2"


class ClickUp:
    def __init__(self) -> None:
        self.token = os.environ.get("CLICKUP_TOKEN", "")
        self.list_id = os.environ.get("CLICKUP_LIST_ID", "901615395458")
        self.returns_list_id = os.environ.get("CLICKUP_RETURNS_LIST_ID", "901615395484")
        self.dry_run = os.environ.get("DRY_RUN", "true").lower() != "false"

    def log_action(self, *, category: str, order: str, channel: str, action: str,
                   detail: str = "", returns: bool = False,
                   assignees: Optional[List[str]] = None,
                   due_in_hours: Optional[float] = None,
                   convo_key: Optional[str] = None) -> Dict[str, Any]:
        """One task PER CONVERSATION. If a task already exists for this convo, add a comment
        (and close it when the action means complete) instead of creating a new task."""
        list_id = self.returns_list_id if returns else self.list_id

        if convo_key:
            existing = self.find_open_task_by_convo(list_id, convo_key)
            if existing:
                note = f"🔄 *{action}*" + (f" — {detail}" if detail else "")
                self.comment_task(existing["id"], note)
                if action in ("auto_sent", "closed"):
                    self.close_task(existing["id"], list_id)   # conversation complete
                return {"task": existing, "created": False}

        name = f"[{channel}] {category} · {order or 'no-order'} · {action}"
        marker = f"\n\n<!-- convo:{convo_key} -->" if convo_key else ""
        body = (
            f"**Category:** {category}\n**Order:** {order}\n**Channel:** {channel}\n"
            f"**Action:** {action}\n**Detail:** {detail}\n{marker}"
        )
        return {"task": self._create_task(list_id, name, body, assignees, due_in_hours),
                "created": True}

    def find_open_task_by_convo(self, list_id: str, convo_key: str) -> Optional[Dict[str, Any]]:
        """Find an OPEN task for this conversation (matched on the embedded convo marker)."""
        if not (self.token and convo_key):
            return None
        needle = f"convo:{convo_key}"
        for t in self.list_open_tasks(list_id):
            blob = (t.get("description") or "") + (t.get("text_content") or "") + (t.get("name") or "")
            if needle in blob:
                return t
        return None

    def _create_task(self, list_id: str, name: str, markdown: str,
                     assignees: Optional[List[str]] = None,
                     due_in_hours: Optional[float] = None) -> Dict[str, Any]:
        if self.dry_run or not self.token:
            who = f" -> assignees {assignees}" if assignees else ""
            due = f" due+{due_in_hours}h" if due_in_hours else ""
            print(f"[DRY_RUN clickup] task in {list_id}: {name}{who}{due}")
            return {"dry_run": True, "name": name}
        payload: Dict[str, Any] = {"name": name, "markdown_description": markdown}
        if assignees:
            payload["assignees"] = [int(a) for a in assignees]
        if due_in_hours:
            payload["due_date"] = int((time.time() + due_in_hours * 3600) * 1000)
            payload["due_date_time"] = True
        r = requests.post(
            f"{API}/list/{list_id}/task",
            headers={"Authorization": self.token, "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()

    # ----- reconciliation helpers (loop closure) -------------------------
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": self.token, "Content-Type": "application/json"}

    def list_open_tasks(self, list_id: str) -> List[Dict[str, Any]]:
        """Open (not closed) tasks in a list. Empty if no token."""
        if not self.token:
            return []
        r = requests.get(f"{API}/list/{list_id}/task",
                         headers=self._headers(), params={"include_closed": "false"}, timeout=15)
        r.raise_for_status()
        return r.json().get("tasks", [])

    def get_task_comments(self, task_id: str) -> List[Dict[str, Any]]:
        """Comments on a task (for reading team instructions like REPLY:/CLOSE)."""
        if not self.token:
            return []
        r = requests.get(f"{API}/task/{task_id}/comment", headers=self._headers(), timeout=15)
        r.raise_for_status()
        return r.json().get("comments", [])

    def comment_task(self, task_id: str, text: str) -> None:
        if self.dry_run or not self.token:
            print(f"[DRY_RUN clickup] comment on {task_id}: {text}")
            return
        requests.post(f"{API}/task/{task_id}/comment",
                      headers=self._headers(), json={"comment_text": text}, timeout=15)

    def _done_status(self, list_id: str) -> Optional[str]:
        """Find the list's 'done'/'closed' status name."""
        r = requests.get(f"{API}/list/{list_id}", headers=self._headers(), timeout=15)
        r.raise_for_status()
        for s in r.json().get("statuses", []):
            if s.get("type") in ("done", "closed"):
                return s.get("status")
        return None

    def close_task(self, task_id: str, list_id: str) -> None:
        if self.dry_run or not self.token:
            print(f"[DRY_RUN clickup] close task {task_id}")
            return
        status = self._done_status(list_id)
        if status:
            requests.put(f"{API}/task/{task_id}",
                         headers=self._headers(), json={"status": status}, timeout=15)
