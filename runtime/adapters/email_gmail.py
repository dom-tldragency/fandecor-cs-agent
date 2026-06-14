"""Gmail adapter via a Google service account with domain-wide delegation.

Reads + sends for the Fan Decor CS mailbox(es) (customerservice@ / marketing@fandecor.com).
Activated when GMAIL_SERVICE_ACCOUNT_JSON (base64) is present; impersonates each mailbox.

⚠️ Pending the service-account key (see cs-agent/setup/google-gmail-api-access.md). Until then this is
not live and fetch_new() returns []. Code path is structured; the Gmail API calls are wired to the
google-api-python-client client built from the delegated credentials.
"""
from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, List, Optional

from .base import ChannelAdapter, Message

SCOPES = ["https://www.googleapis.com/auth/gmail.modify",
          "https://www.googleapis.com/auth/gmail.send"]


class GmailChannel(ChannelAdapter):
    name = "email"

    def __init__(self, mailbox: str = "customerservice@fandecor.com") -> None:
        self.mailbox = mailbox
        raw = os.environ.get("GMAIL_SERVICE_ACCOUNT_JSON", "")
        self._sa: Optional[Dict[str, Any]] = json.loads(base64.b64decode(raw)) if raw else None
        self.live = self._sa is not None

    def _service(self):
        # Lazy: only import google libs when actually connecting.
        from google.oauth2 import service_account  # type: ignore
        from googleapiclient.discovery import build  # type: ignore
        creds = service_account.Credentials.from_service_account_info(
            self._sa, scopes=SCOPES, subject=self.mailbox
        )
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    def fetch_new(self) -> List[Message]:
        if not self.live:
            return []
        svc = self._service()
        threads = svc.users().threads().list(
            userId="me", q="is:unread in:inbox newer_than:7d", maxResults=25
        ).execute().get("threads", [])
        out: List[Message] = []
        for t in threads:
            full = svc.users().threads().get(userId="me", id=t["id"], format="full").execute()
            msgs = full.get("messages", [])
            last = msgs[-1]
            headers = {h["name"]: h["value"] for h in last.get("payload", {}).get("headers", [])}
            out.append(Message(
                id=t["id"], channel=self.name, received_at=last.get("internalDate"),
                customer={"name": headers.get("From", ""), "email": _addr(headers.get("From", ""))},
                subject=headers.get("Subject", ""), body=_extract_body(last.get("payload", {})),
                order_hint="", attachments=[], raw={"threadId": t["id"]},
            ))
        return out

    def send_reply(self, msg: Message, body: str) -> Dict[str, Any]:
        svc = self._service()
        raw = _build_raw(to=msg["customer"]["email"], frm=self.mailbox,
                         subject="Re: " + msg.get("subject", ""), body=body)
        return svc.users().messages().send(
            userId="me", body={"raw": raw, "threadId": msg["raw"]["threadId"]}
        ).execute()

    def save_draft(self, msg: Message, body: str) -> Dict[str, Any]:
        svc = self._service()
        raw = _build_raw(to=msg["customer"]["email"], frm=self.mailbox,
                         subject="Re: " + msg.get("subject", ""), body=body)
        return svc.users().drafts().create(
            userId="me", body={"message": {"raw": raw, "threadId": msg["raw"]["threadId"]}}
        ).execute()

    def mark_status(self, msg: Message, status: str) -> None:
        svc = self._service()
        remove = ["UNREAD"] if status in ("resolved", "closed") else []
        svc.users().threads().modify(
            userId="me", id=msg["raw"]["threadId"], body={"removeLabelIds": remove}
        ).execute()


def _addr(frm: str) -> str:
    if "<" in frm and ">" in frm:
        return frm.split("<", 1)[1].split(">", 1)[0]
    return frm.strip()


def _extract_body(payload: Dict[str, Any]) -> str:
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", "ignore")
    return ""


def _build_raw(to: str, frm: str, subject: str, body: str) -> str:
    from email.mime.text import MIMEText
    m = MIMEText(body)
    m["To"], m["From"], m["Subject"] = to, frm, subject
    return base64.urlsafe_b64encode(m.as_bytes()).decode()
