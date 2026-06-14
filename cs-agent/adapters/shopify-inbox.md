# Adapter — Shopify Inbox / storefront chat + contact form

**Backend:** Shopify Inbox API / contact-form submissions. **Status:** STUB.

## Interface mapping (when wired)
- `fetch_new()` → poll Shopify Inbox conversations + contact-form emails for new customer messages.
- `normalise(raw)` → customer from the conversation; order often linkable directly to the Shopify customer.
- `send_reply` / `save_draft` → reply in the Inbox conversation / draft.
- `mark_status` → set conversation status (open/closed) in Inbox.

## Stub behaviour (now)
`fetch_new()` returns `[]`, logs `shopify_inbox channel stubbed`. No actions taken.

## To activate
Wire Shopify Inbox (the Shopify Admin connection is already live for order lookup; Inbox conversations
need their own access). Then set `shopify_inbox.status: live` in `config/channels.yaml`.
