# Setup — ClickUp API token for the cloud worker

The worker logs every CS action to the **CS Agent — Log & Escalations** list (901615395458) and returns to
the **Returns & Refunds Register** (901615395484). It needs a ClickUp token.

## Steps
1. In ClickUp: **Settings → Apps → API Token** → **Generate** (personal token `pk_…`).
   - For a cleaner long-term setup, create a ClickUp **OAuth app / a dedicated bot user** so logs aren't
     tied to a personal account — but a personal token is fine to start.
2. Store it as the `CLICKUP_TOKEN` secret (see DEPLOY.md).
3. List IDs are already wired (`CLICKUP_LIST_ID`, `CLICKUP_RETURNS_LIST_ID`).

## Optional (manual, in the ClickUp UI) — richer returns tracking
The returns lifecycle (Requested → Instructions sent → Awaiting item → Received & inspected →
Refund pending → Resolved) is tracked today via task content. To make it visual, add a **Stage** dropdown
custom field (or list statuses) on the Returns & Refunds Register with those six options. The ClickUp API
used here can't create custom fields, so this is a quick manual step if you want the board view.
