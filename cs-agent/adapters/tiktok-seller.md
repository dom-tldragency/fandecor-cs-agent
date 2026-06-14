# Adapter — TikTok Shop Seller (Partner API)

**Backend:** TikTok Shop Seller/Partner API. **Status:** STUB.
⚠️ The currently connected TikTok tool is **affiliate/creator** focused — it is NOT seller CS,
orders, or refunds. A separate TikTok Shop Seller/Partner API connection is required.

## Interface mapping (when wired)
- `fetch_new()` → poll Seller Center messages + return/refund requests.
- `normalise(raw)` → customer + TikTok order id; `order_hint` = TikTok order number.
- order lookup → TikTok Shop orders API (separate from Shopify).
- `send_reply` / `save_draft` → Seller Center message reply / draft.
- refund/return → TikTok Shop seller refund flow — **gated** money action, same guardrails as Shopify refunds.
- `mark_status` → set the Seller Center conversation / request status.

## Stub behaviour (now)
`fetch_new()` returns `[]`, logs `tiktok_seller channel stubbed: Seller/Partner API not connected`.

## Confirmed 2026-06-14
Checked FD's TikTok inbox via the connected Cruva tool — it returns **creator/affiliate handles**
(@luca_daily_finds, @legit.storytime, etc.), i.e. collab DMs, NOT buyer CS. So buyer CS is not reachable
through the current connection; the TikTok Shop Partner API is required.

## To activate
1. Connect the TikTok Shop Seller/Partner API — see `setup/tiktok-shop-seller-api-access.md`.
2. Map TikTok order schema → common shape.
3. Set `tiktok_seller.status: live`. Refunds stay gated (≤£35 cap, human-approved) until Phase 3.
