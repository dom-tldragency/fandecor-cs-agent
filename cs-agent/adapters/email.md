# Adapter — Email (Gmail MCP)

**Backend:** Gmail MCP. **Status:** stubbed until `marketing@fandecor.com` is connected.
Currently the connected account is `dom@tl-dr.agency` (wrong inbox for FD CS).

## Interface mapping (once the FD mailbox is connected)

- `fetch_new()` → `search_threads` for unread inbox threads (`is:unread in:inbox newer_than:Nd`),
  excluding internal/notification senders. One thread = one conversation.
- `normalise(raw)` → from `get_thread`: customer = sender; `body` = latest customer message;
  `order_hint` = regex `#\d+` or known order-email patterns; `subject` = thread subject.
- `send_reply(msg, body)` → reply on the thread **as the FD CS mailbox** (auto_send only).
  **Chosen path: direct Gmail API via a service account with domain-wide delegation** — see
  `setup/google-gmail-api-access.md`. Covers both `customerservice@fandecor.com` and `marketing@fandecor.com`,
  with full read (`gmail.modify`) + send (`gmail.send`). This replaces the old draft-only MCP connector and
  the Zapier send workaround. Until the JSON key is provisioned, email "send" degrades to `save_draft`.
- `save_draft(msg, body)` → create a draft on the thread (draft/gated actions; also the fallback when no send path).
- `mark_status(msg, status)` → apply a Gmail label: `CS/Resolved`, `CS/Pending-Approval`, `CS/Closed`
  (create via `create_label` on first run), and mark read.

## Stub behaviour (now)
`fetch_new()` returns `[]` and logs `email channel stubbed: marketing@fandecor.com not connected`.
No drafts, no sends. Flip `channels.yaml: email.status` to `live` after connection.

## To activate
1. Connect `marketing@fandecor.com` as a Google account.
2. Confirm the agent can `search_threads`/`create_draft` on it.
3. Set `email.status: live` in `config/channels.yaml`.
4. Run the eval harness against email samples, then enable per the autonomy mode.
