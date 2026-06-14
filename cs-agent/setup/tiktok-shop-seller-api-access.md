# Setup — TikTok Shop Seller (Partner) API access for the CS Agent

**Goal:** let the CS agent read **buyer customer-service messages** and manage **returns/refunds** for the
Fan Decor TikTok Shop — i.e. seller-side CS.

**Important:** the TikTok tool currently connected to Claude (Cruva) is **affiliate/creator** focused
(creator DMs, samples, collabs). It does **not** expose buyer CS, orders, or refunds. Seller CS needs the
**TikTok Shop Partner API** with seller authorisation — a separate connection.

**Who does this:** the Fan Decor TikTok Shop account owner/admin (James/Fin), plus whoever manages dev integrations.

---

## Steps

1. **TikTok Shop Partner Center** — go to **partner.tiktokshop.com** and register/sign in as a developer
   (or use an existing partner account).
2. **Create an app:** Partner Center → **Manage Apps → Create app**. App type: **Seller** (not Affiliate).
3. **Request the scopes** the CS agent needs (request least-privilege):
   - **Customer Service / Messages** — read & reply to buyer conversations.
   - **Order Management** — read orders (for lookup) .
   - **Return & Refund** — read and process returns/refunds.
   - (Read-only on orders is fine; refund/return write is needed for Phase 3 — but stays human-gated below £35.)
4. **Authorise the Fan Decor shop to the app:** from the Fan Decor Seller Center, approve the app
   (generates a shop-level authorisation). This produces an **auth code → access token + refresh token**.
5. **Collect the credentials:**
   - **App key** and **App secret** (from the app's Basic Information).
   - **Authorised access token + refresh token** for the Fan Decor shop.
   - The **shop_id / shop_cipher** returned on authorisation.
6. **Hand back to us (securely):** app key, app secret, the shop access/refresh tokens, and shop id —
   via a secure vault, not plain email/Slack. We store them as encrypted secrets and wire the
   `tiktok_seller` adapter to them.

## Notes
- TikTok Shop app approval can take a few days (TikTok reviews the app/scopes) — start early.
- Tokens expire and refresh on a schedule; we handle refresh in the runtime once we have the refresh token.
- Until this is connected, the `tiktok_seller` adapter stays stubbed (returns no messages) and the core
  pipeline runs unaffected.
- Refunds on TikTok stay **gated** (human-approved, ≤£35 cap) exactly like Shopify refunds.
