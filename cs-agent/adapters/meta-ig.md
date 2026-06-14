# Adapter — Meta / Instagram DMs (Meta Graph API)

**Backend:** Meta Graph API (Instagram DMs + Messenger). **Status:** STUB.

## Interface mapping (when wired)
- `fetch_new()` → poll IG/Messenger conversations for new inbound DMs.
- `normalise(raw)` → customer = IG/FB handle (often no order number — ask for it or match by name/email).
- order lookup → Shopify by any provided order number/email; social handles rarely map directly.
- `send_reply` / `save_draft` → DM reply / draft.
- `mark_status` → label/mark the conversation handled.

## Notes specific to social
- DMs are casual and public-adjacent — extra care on tone and **never** post PII in a DM that could be screenshotted.
- Messages are often pre-purchase (sizing/product) → mostly `sizing_product` and `wismo`.

## Stub behaviour (now)
`fetch_new()` returns `[]`, logs `meta_ig channel stubbed: Meta Graph API not connected`.

## To activate
Connect Meta Graph API (IG messaging + Messenger scopes), map payloads, set `meta_ig.status: live`.
