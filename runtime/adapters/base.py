"""The adapter interface every channel implements.

The core loop (main.py) only ever calls these methods, so it is identical regardless of channel.
A stubbed adapter returns no messages, so the loop runs unchanged until the channel's API is connected.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class Message(dict):
    """Normalised inbound message. Keys: id, channel, received_at, customer{name,email,handle},
    subject, body, order_hint, attachments, raw."""


class ChannelAdapter:
    name = "base"
    live = False

    def fetch_new(self) -> List[Message]:
        """Return new/unhandled inbound messages. Stub returns []."""
        return []

    def send_reply(self, msg: Message, body: str) -> Dict[str, Any]:
        raise NotImplementedError

    def save_draft(self, msg: Message, body: str) -> Dict[str, Any]:
        raise NotImplementedError

    def mark_status(self, msg: Message, status: str) -> None:
        """status in {resolved, pending_approval, closed}."""
        raise NotImplementedError

    def lookup_order(self, order_hint: str, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Channel-specific order lookup. Email/IG fall back to Shopify."""
        return None


class StubAdapter(ChannelAdapter):
    """A not-yet-connected channel. Implements the interface as a no-op so the core runs unchanged."""

    def __init__(self, name: str, reason: str = "") -> None:
        self.name = name
        self.reason = reason
        self.live = False

    def fetch_new(self) -> List[Message]:
        return []
