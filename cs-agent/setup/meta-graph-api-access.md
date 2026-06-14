# Setup — Meta Graph API access (Instagram + Messenger DMs)

**Goal:** let the CS agent read + reply to buyer DMs on the Fan Decor **Instagram** and **Facebook
Messenger**. Like TikTok, this needs a Meta app + permissions + app review — start early.

**Who:** the owner/admin of the Fan Decor Facebook Page + linked Instagram professional account.

## Steps
1. **developers.facebook.com → My Apps → Create App** → type **Business**.
2. Add the **Messenger** and **Instagram** products to the app.
3. **Link** the Fan Decor Facebook Page and the Instagram professional account to the app.
4. Request permissions (these require **App Review** by Meta):
   - `pages_messaging` (Messenger send/receive)
   - `instagram_manage_messages` (IG DM send/receive)
   - `pages_show_list`, `instagram_basic` (read account/conversations)
5. Generate a **long-lived Page access token** (with the above scopes). Note the **IG business account ID**
   and the **Page ID**.
6. Hand back (securely): `META_PAGE_ACCESS_TOKEN`, `META_IG_ID`, `META_PAGE_ID` → set as GitHub secrets.

## Notes
- Meta normally **pushes** new messages via webhooks. We **poll** the Graph conversations endpoints every
  cycle instead (simpler, no public webhook endpoint needed; fine at 30-min cadence). Webhooks can be added
  later for real-time if wanted.
- App review for messaging permissions can take days — submit early.
- Until connected, the `meta_ig` channel stays stubbed and the core runs unaffected.
- Tone caution (in the playbook): DMs are screenshot-prone — never put PII in a DM.
