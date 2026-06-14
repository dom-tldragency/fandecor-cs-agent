"""Meta adapter — Instagram + Messenger DMs via the Meta Graph API.

Buyer DMs ("is this in stock?", "where's my order?") on Instagram and Facebook Messenger.

Credentials (from env, never hardcoded):
  META_PAGE_ACCESS_TOKEN  -> long-lived Page access token (with messaging perms)
  META_IG_ID / META_PAGE_ID -> the IG business account / FB page id

⚠️ INTEGRATION NOTE: Meta messaging usually pushes via webhooks; this adapter polls the Graph API
conversations endpoints, which is fine for a 30-min cycle. Graph API version + the exact conversation
fields must be confirmed against the live Graph docs at integration (untested without a token + app
review for instagram_manage_messages / pages_messaging).
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

from .base import ChannelAdapter, Message

GRAPH = "https://graph.facebook.com/v21.0"


class MetaIG(ChannelAdapter):
    name = "meta_ig"

    def __init__(self) -> None:
        self.token = os.environ.get("META_PAGE_ACCESS_TOKEN", "")
        self.ig_id = os.environ.get("META_IG_ID", "")
        self.page_id = os.environ.get("META_PAGE_ID", "")
        self.live = bool(self.token and (self.ig_id or self.page_id))

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        params = dict(params); params["access_token"] = self.token
        r = requests.get(f"{GRAPH}/{path}", params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(f"{GRAPH}/{path}", params={"access_token": self.token},
                          json=body, timeout=20)
        r.raise_for_status()
        return r.json()

    def fetch_new(self) -> List[Message]:
        if not self.live:
            return []
        out: List[Message] = []
        node = self.ig_id or self.page_id
        platform = "instagram" if self.ig_id else "messenger"
        convs = self._get(f"{node}/conversations",
                          {"platform": platform, "fields": "participants,unread_count", "limit": 25})
        for c in convs.get("data", []):
            if not c.get("unread_count"):
                continue
            msgs = self._get(f"{c['id']}/messages",
                             {"fields": "from,message,created_time", "limit": 5}).get("data", [])
            latest = msgs[0] if msgs else None      # Graph returns newest-first
            if not latest:
                continue
            sender = latest.get("from", {})
            out.append(Message(
                id=sender.get("id", c["id"]),       # reply target = sender PSID/IGSID
                channel=self.name, received_at=latest.get("created_time"),
                customer={"name": sender.get("username") or sender.get("name"),
                          "handle": sender.get("username")},
                subject="", body=latest.get("message", ""),
                order_hint="", attachments=[], raw=c,
            ))
        return out

    def send_reply(self, msg: Message, body: str) -> Dict[str, Any]:
        node = self.ig_id or self.page_id
        return self._post(f"{node}/messages",
                          {"recipient": {"id": msg["id"]}, "message": {"text": body}})

    def save_draft(self, msg: Message, body: str) -> Dict[str, Any]:
        return {"draft_held_in": "clickup", "body": body}  # no native DM draft

    def mark_status(self, msg: Message, status: str) -> None:
        return None  # Meta has no per-conversation resolve state via API; tracked in ClickUp
