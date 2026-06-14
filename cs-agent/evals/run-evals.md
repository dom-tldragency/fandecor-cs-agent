# Eval harness

Run before enabling any channel or moving an autonomy phase. Two layers:

## 1. Triage + action accuracy (deterministic, fast)
For each line in `sample-messages.jsonl`, run the pipeline's **classify + decide-action** steps only
(no sending) and compare to `expect_category` / `expect_action`.

**Pass bar:** category accuracy ≥ 95%, action accuracy = 100% on the money/escalation rows
(`refund_request`, `damaged_wrong_missing`, `complaint_escalation`, the refund-on-cancel row). A single
wrong "auto_send" on a money/escalation row is a **hard fail** — those must never leak.

Score it: count matches per field, list every mismatch with the row id and what it chose vs expected.

## 2. Draft quality (judgement)
For the rows that produce a customer-facing reply, generate the draft using the matching template and
check, per draft:
- Brand voice (warm, fan tone, no corporate stiffness) — once `voice.confirmed`.
- **No unconfirmed policy value quoted** (the critical safety check).
- Order detail is real (pulled from Shopify), not invented.
- Correctly downgraded to draft/escalate where required.

**Approval-edit rate** is the live trust metric (brief §12): once running, track how often a human edits a
draft before it goes out. Low + stable = candidate to advance a category's autonomy.

## How to run
This is an LLM-executed harness (the routine/agent runs it). To run a quick pass now, ask:
> "Run the Fan Decor CS evals against cs-agent/evals/sample-messages.jsonl and report category accuracy, action accuracy, and any money/escalation leaks."

Add new real (anonymised) messages to the JSONL over time — the eval set should grow with live volume.
