"""TikTok Shop Seller (Partner API) adapter.

Buyer customer-service messages + orders + returns/refunds for the Fan Decor TikTok Shop.

Credentials (all from env, NEVER hardcoded):
  TIKTOK_APP_KEY, TIKTOK_APP_SECRET  -> identify the app (provided)
  TIKTOK_ACCESS_TOKEN, TIKTOK_REFRESH_TOKEN, TIKTOK_SHOP_CIPHER  -> per-shop, obtained AFTER the
  Partner Center app is approved and the Fan Decor shop authorises it (token exchange below).

⚠️ INTEGRATION NOTE: the exact API version segments (e.g. /202309/) and the precise signature byte
order are pinned to TikTok's published spec. They are implemented here per the documented v2 scheme but
MUST be verified against the authenticated Partner docs the moment we can make a real call. Until tokens
exist this module cannot be exercised live — by design (we are not going live yet).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, List, Optional

import requests

from .base import ChannelAdapter, Message

API_BASE = "https://open-api.tiktokglobalshop.com"
AUTH_BASE = "https://auth.tiktok-shops.com"
CS_VER = "202309"        # customer service API version — VERIFY against live docs
ORDER_VER = "202309"     # order API version — VERIFY
RETURN_VER = "202309"    # return/refund API version — VERIFY


class TikTokSeller(ChannelAdapter):
    name = "tiktok_seller"

    def __init__(self) -> None:
        self.app_key = os.environ.get("TIKTOK_APP_KEY", "")
        self.app_secret = os.environ.get("TIKTOK_APP_SECRET", "")
        self.access_token = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
        self.refresh_token = os.environ.get("TIKTOK_REFRESH_TOKEN", "")
        self.shop_cipher = os.environ.get("TIKTOK_SHOP_CIPHER", "")
        # Live only once we have an access token for the shop.
        self.live = bool(self.app_key and self.app_secret and self.access_token)

    # ----- signing --------------------------------------------------------
    def _sign(self, path: str, query: Dict[str, Any], body: str = "") -> str:
        """TikTok Shop signature (HMAC-SHA256).

        signString = secret + path + (sorted {key}{value} for all query params except sign &
        access_token) + body + secret ; then HMAC-SHA256 with secret as key, hex digest.
        """
        params = {k: v for k, v in query.items() if k not in ("sign", "access_token")}
        concatenated = "".join(f"{k}{params[k]}" for k in sorted(params))
        base = f"{self.app_secret}{path}{concatenated}{body}{self.app_secret}"
        return hmac.new(self.app_secret.encode(), base.encode(), hashlib.sha256).hexdigest()

    def _request(self, method: str, path: str, query: Optional[Dict[str, Any]] = None,
                 body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = dict(query or {})
        query.update({"app_key": self.app_key, "timestamp": int(time.time())})
        if self.shop_cipher:
            query["shop_cipher"] = self.shop_cipher
        body_str = json.dumps(body) if body is not None else ""
        query["sign"] = self._sign(path, query, body_str)
        headers = {"x-tts-access-token": self.access_token, "Content-Type": "application/json"}
        url = f"{API_BASE}{path}"
        r = requests.request(method, url, params=query, data=body_str or None,
                             headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    # ----- token lifecycle ------------------------------------------------
    def exchange_auth_code(self, auth_code: str) -> Dict[str, Any]:
        """One-time: after the shop authorises the app, swap the auth code for access/refresh tokens."""
        r = requests.get(
            f"{AUTH_BASE}/api/v2/token/get",
            params={"app_key": self.app_key, "app_secret": self.app_secret,
                    "auth_code": auth_code, "grant_type": "authorized_code"},
            timeout=20,
        )
        r.raise_for_status()
        return r.json()

    def refresh(self) -> Dict[str, Any]:
        """Refresh the access token (they expire). Store the new tokens as secrets."""
        r = requests.get(
            f"{AUTH_BASE}/api/v2/token/refresh",
            params={"app_key": self.app_key, "app_secret": self.app_secret,
                    "refresh_token": self.refresh_token, "grant_type": "refresh_token"},
            timeout=20,
        )
        r.raise_for_status()
        return r.json()

    # ----- adapter interface ---------------------------------------------
    def fetch_new(self) -> List[Message]:
        if not self.live:
            return []
        out: List[Message] = []
        convs = self._request("GET", f"/customer_service/{CS_VER}/conversations",
                              query={"page_size": 20}).get("data", {}).get("conversations", [])
        for c in convs:
            if not c.get("unread_count"):
                continue
            cid = c.get("conversation_id")
            msgs = self._request(
                "GET", f"/customer_service/{CS_VER}/conversations/{cid}/messages",
                query={"page_size": 10},
            ).get("data", {}).get("messages", [])
            latest = next((m for m in msgs if m.get("sender", {}).get("role") == "BUYER"), None)
            if not latest:
                continue
            out.append(Message(
                id=cid, channel=self.name, received_at=latest.get("create_time"),
                customer={"name": c.get("participant", {}).get("nickname"), "handle": None},
                subject="", body=latest.get("content", {}).get("text", ""),
                order_hint=c.get("order_id", ""), attachments=[], raw=c,
            ))
        return out

    def send_reply(self, msg: Message, body: str) -> Dict[str, Any]:
        return self._request(
            "POST", f"/customer_service/{CS_VER}/conversations/{msg['id']}/messages",
            body={"type": "TEXT", "content": json.dumps({"text": body})},
        )

    def save_draft(self, msg: Message, body: str) -> Dict[str, Any]:
        # TikTok has no native draft; drafts are held in ClickUp for approval (handled in main.py).
        return {"draft_held_in": "clickup", "body": body}

    def mark_status(self, msg: Message, status: str) -> None:
        if status == "closed":
            self._request("POST", f"/customer_service/{CS_VER}/conversations/{msg['id']}/read")

    def lookup_order(self, order_hint: str, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not (self.live and order_hint):
            return None
        data = self._request("GET", f"/order/{ORDER_VER}/orders",
                             query={"ids": order_hint}).get("data", {})
        orders = data.get("orders", [])
        return orders[0] if orders else None

    def list_returns(self) -> List[Dict[str, Any]]:
        if not self.live:
            return []
        return self._request("GET", f"/return_refund/{RETURN_VER}/returns/search",
                            query={"page_size": 20}).get("data", {}).get("return_orders", [])
