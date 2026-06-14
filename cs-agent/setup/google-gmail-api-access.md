# Setup — Direct Gmail API access for the Fan Decor CS Agent

**Goal:** let the CS agent **read and send** email for **two mailboxes** —
`customerservice@fandecor.com` and `marketing@fandecor.com` — programmatically, unattended.

**Who does this:** someone with **Google Workspace super-admin** + Google Cloud Console access for the
fandecor.com domain.

**Recommended method:** a **service account with domain-wide delegation** (the standard way an automated
agent accesses shared Workspace mailboxes). An OAuth-per-mailbox alternative is at the bottom if you'd
rather not enable domain-wide delegation.

---

## Part A — Google Cloud Console (create the credential)

1. Go to **console.cloud.google.com** → create (or pick) a project, e.g. **`fandecor-cs-agent`**.
2. **APIs & Services → Library →** search **Gmail API → Enable**.
3. **APIs & Services → Credentials → Create credentials → Service account**.
   - Name: `fandecor-cs-agent`. No project roles required. Create.
4. Open the new service account → **Keys → Add key → Create new key → JSON → Create.**
   - A `.json` file downloads. **This is the secret credential** — keep it safe (see Security).
5. On the service account's details page, copy its **Unique ID / Client ID** (a long number).
   You'll need it in Part B. (Domain-wide delegation is enabled by registering this Client ID in Admin.)

## Part B — Google Workspace Admin (authorise the two mailboxes)

6. Go to **admin.google.com** → **Security → Access and data control → API controls →
   Domain-wide delegation → Manage domain-wide delegation → Add new.**
7. **Client ID:** paste the service account Client ID from step 5.
8. **OAuth scopes** (paste exactly, comma-separated):
   ```
   https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.send
   ```
   - `gmail.modify` = read, label, organise, create drafts (everything except permanent delete).
   - `gmail.send` = send mail.
9. **Authorise.**
10. Confirm **`customerservice@fandecor.com`** and **`marketing@fandecor.com`** are **real mailboxes**
    (Workspace users or shared mailboxes the service account can impersonate) — not just aliases.
    If either is an alias, tell us which real account it routes to.

## Part C — Hand back to the agent team
- The **JSON key file** (shared securely — see below).
- Confirmation the two addresses above are authorised and the two scopes were granted.

That's everything. We wire the JSON key into the agent runtime (as a stored secret) and the agent then
reads, drafts, and sends for both mailboxes directly via the Gmail API.

---

## Security notes (please read)
- The JSON key is a **password-equivalent secret**. Send it via a **secure vault** (1Password / a shared
  secret) — **not** plain email or Slack. It will be stored as an encrypted secret in the agent runtime,
  never in code or chat.
- Domain-wide delegation lets the service account impersonate domain users **only for the two scopes
  above**. The agent will only ever impersonate the two Fan Decor CS mailboxes. The scopes deliberately
  **exclude** permanent delete and admin access.
- If the key is ever exposed, delete it in **Cloud Console → service account → Keys** and issue a new one.

## Alternative — OAuth2 per mailbox (no domain-wide delegation)
If you'd prefer not to enable domain-wide delegation:
1. Cloud Console → **OAuth consent screen** (User type: Internal) → configure.
2. **Credentials → Create credentials → OAuth client ID** (type: Desktop app or Web).
3. Each mailbox owner signs in and consents to `gmail.modify` + `gmail.send`.
4. Capture the **refresh token** for each mailbox and hand those back (securely).
More granular (no domain-wide power), but needs interactive consent per mailbox and token refresh handling.
