# Channel adapters — the interface contract

Every channel (email, Shopify Inbox, TikTok Seller, Meta/IG) is a swappable **adapter** that exposes
the **same interface** to the core pipeline. The core (`SKILL.md`) never knows or cares which channel a
message came from — it just calls these operations. Adding a channel = writing one adapter; the brain is untouched.

## Interface every adapter must implement

| Operation | Purpose | Returns |
|---|---|---|
| `fetch_new()` | Poll for new/unhandled inbound messages since last cycle | list of normalised messages |
| `normalise(raw)` | Map the channel's raw payload to the common message shape (below) | normalised message |
| `send_reply(msg, body)` | Send a reply on the channel (only called when action = auto_send) | send result |
| `save_draft(msg, body)` | Save a reply as a draft for human approval (action = draft/gated) | draft ref |
| `mark_status(msg, status)` | Set channel-side state: `resolved` / `pending_approval` / `closed` | ok |

## Common (normalised) message shape

```yaml
id:            # channel-native id (thread/message/conversation id)
channel:       # email | shopify_inbox | tiktok_seller | meta_ig
received_at:   # ISO timestamp
customer:
  name:
  email:
  handle:      # for social channels
subject:       # if any
body:          # the customer's text
order_hint:    # any order number / id mentioned
attachments:   # e.g. damage photos
raw:           # original payload, kept for audit
```

## Status of each adapter
- `email.md` — **ready, channel stubbed** until `marketing@fandecor.com` is connected (Gmail MCP).
- `shopify-inbox.md` — stub.
- `tiktok-seller.md` — stub (needs TikTok Shop Seller/Partner API).
- `meta-ig.md` — stub (needs Meta Graph API).

A stub implements the interface but `fetch_new()` returns empty and logs "channel stubbed", so the core
runs unchanged and the channel lights up the moment its backend is connected.
