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
        self._sa: Optional[Dict[str, Any]] = self._load_sa(
            os.environ.get("GMAIL_SERVICE_ACCOUNT_JSON", "").strip())
        self.live = self._sa is not None

    @staticmethod
    def _load_sa(raw: str) -> Optional[Dict[str, Any]]:
        """Accept the service-account key as raw JSON OR base64-encoded JSON."""
        if not raw:
            return None
        try:
            return json.loads(raw)                      # raw JSON pasted directly
        except json.JSONDecodeError:
            return json.loads(base64.b64decode(raw))    # base64-encoded JSON

    def _service(self):
        # Lazy: only import google libs when actually connecting.
        from google.oauth2 import service_account  # type: ignore
        from googleapiclient.discovery import build  # type: ignore
        creds = service_account.Credentials.from_service_account_info(
            self._sa, scopes=SCOPES, subject=self.mailbox
        )
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    def _to_message(self, thread_id: str, msgs: list) -> Message:
        """Build a normalised Message carrying the FULL thread history (for multi-message context).

        `history` is the whole conversation oldest-first, each tagged from 'customer' or 'us'.
        `body`/`subject`/`customer` focus on the latest *customer* message — the one we're replying to.
        """
        history = []
        for m in msgs:
            h = {hh["name"]: hh["value"] for hh in m.get("payload", {}).get("headers", [])}
            frm = h.get("From", "")
            who = "us" if "fandecor.com" in frm.lower() else "customer"
            history.append({"from": who, "sender": frm, "subject": h.get("Subject", ""),
                            "text": (_extract_body(m.get("payload", {})) or "").strip()})
        cust_idxs = [i for i, e in enumerate(history) if e["from"] == "customer"]
        focus_i = cust_idxs[-1] if cust_idxs else len(msgs) - 1
        focus, fh = msgs[focus_i], history[focus_i]
        return Message(
            id=thread_id, channel=self.name, received_at=focus.get("internalDate"),
            customer={"name": fh["sender"], "email": _addr(fh["sender"])},
            subject=fh["subject"], body=fh["text"],
            order_hint="", attachments=[], raw={"threadId": thread_id}, history=history,
        )

    def fetch_new(self) -> List[Message]:
        if not self.live:
            return []
        svc = self._service()
        # Exclude only the bulk-noise categories (Promotions/Social/Forums = newsletters etc.).
        # Keep Primary AND Updates — Gmail files order-related customer emails (e.g. "ORDER NO #1322")
        # under Updates, so filtering to Primary alone wrongly dropped real customers. The relevance
        # gate (llm.is_customer_message) then drops actual order NOTIFICATIONS vs. customer queries.
        max_threads = int(os.environ.get("CS_MAX_THREADS_PER_MAILBOX", "20"))
        threads = svc.users().threads().list(
            userId="me",
            q="is:unread in:inbox -category:promotions -category:social -category:forums newer_than:7d",
            maxResults=max_threads,
        ).execute().get("threads", [])
        out: List[Message] = []
        for t in threads:
            full = svc.users().threads().get(userId="me", id=t["id"], format="full").execute()
            msgs = full.get("messages", [])
            if msgs:
                out.append(self._to_message(t["id"], msgs))
        return out

    def send_reply(self, msg: Message, body: str) -> Dict[str, Any]:
        svc = self._service()
        raw = _build_raw(to=msg["customer"]["email"], frm=self.mailbox,
                         subject="Re: " + msg.get("subject", ""), body=body)
        return svc.users().messages().send(
            userId="me", body={"raw": raw, "threadId": msg["raw"]["threadId"]}
        ).execute()

    def fetch_recent(self, max_threads: int = 15) -> List[Message]:
        """Recent Primary inbox threads (read OR unread) — used for the demo preview, NOT the live loop."""
        if not self.live:
            return []
        svc = self._service()
        threads = svc.users().threads().list(
            userId="me",
            q="in:inbox -category:promotions -category:social -category:forums newer_than:30d",
            maxResults=max_threads,
        ).execute().get("threads", [])
        out: List[Message] = []
        for t in threads:
            full = svc.users().threads().get(userId="me", id=t["id"], format="full").execute()
            msgs = full.get("messages", [])
            if msgs:
                out.append(self._to_message(t["id"], msgs))
        return out

    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Send a fresh email (no thread) — used for refund-confirmation loop closure."""
        svc = self._service()
        raw = _build_raw(to=to, frm=self.mailbox, subject=subject, body=body)
        return svc.users().messages().send(userId="me", body={"raw": raw}).execute()

    def reply_to_thread(self, thread_id: str, body: str) -> Dict[str, Any]:
        """Reply into an existing thread given only its id — used when a human (via ClickUp)
        tells the agent to send a message to the customer. Raises if the thread isn't in this mailbox."""
        svc = self._service()
        full = svc.users().threads().get(userId="me", id=thread_id, format="full").execute()
        to, subject = None, ""
        for m in full.get("messages", []):
            h = {hh["name"]: hh["value"] for hh in m.get("payload", {}).get("headers", [])}
            frm = h.get("From", "")
            if "fandecor.com" not in frm.lower():     # the customer's address
                to, subject = _addr(frm), h.get("Subject", "")
        if not to:
            raise RuntimeError("no customer address found in thread")
        raw = _build_raw(to=to, frm=self.mailbox, subject="Re: " + subject, body=body)
        return svc.users().messages().send(
            userId="me", body={"raw": raw, "threadId": thread_id}
        ).execute()

    def save_draft(self, msg: Message, body: str) -> Dict[str, Any]:
        svc = self._service()
        raw = _build_raw(to=msg["customer"]["email"], frm=self.mailbox,
                         subject="Re: " + msg.get("subject", ""), body=body)
        return svc.users().drafts().create(
            userId="me", body={"message": {"raw": raw, "threadId": msg["raw"]["threadId"]}}
        ).execute()

    def mark_status(self, msg: Message, status: str) -> None:
        # Mark the thread READ on ANY handled status (resolved/closed/pending_approval/escalated)
        # so the next cycle's `is:unread` fetch won't re-process it. A customer reply re-opens it
        # (unread again) → re-handled with full thread context. The human is alerted via Slack/ClickUp,
        # not the inbox unread state, so marking read is safe for drafts/escalations too.
        svc = self._service()
        svc.users().threads().modify(
            userId="me", id=msg["raw"]["threadId"], body={"removeLabelIds": ["UNREAD"]}
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
