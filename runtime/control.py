"""Two-way control — let Camilla/Jamie drive the agent from ClickUp.

Each cycle, scan open tasks for a team instruction in the comments:
  • `REPLY: <message>`  -> send <message> to the customer on the original thread, then close the task.
  • `CLOSE`             -> just close the task.

This is how a human closes the loop on anything the agent didn't finish itself (Tarlu replacements,
escalations, goodwill messages): they action it, drop a REPLY:/CLOSE comment, and the agent delivers
it to the customer and closes off — one task per conversation, start to finish.

The agent leaves a "🤖 delivered" marker so an instruction is never actioned twice.
"""
from __future__ import annotations

import re
from typing import Optional

from .config_loader import Config
from .notify.clickup import ClickUp

_CONVO_RE = re.compile(r"convo:([^\s>]+)")
_CHANNEL_RE = re.compile(r"\*\*Channel:\*\*\s*([A-Za-z_]+)")
_DONE_MARKER = "🤖 delivered"

# Email mailboxes to try when replying (the task doesn't record which one the thread is in).
_MAILBOXES = ["customerservice@fandecor.com", "marketing@fandecor.com"]


def _latest_instruction(comments) -> Optional[tuple]:
    """Return ('reply', text) | ('close', '') for the latest unactioned instruction, else None."""
    instr = None
    for c in sorted(comments, key=lambda x: str(x.get("date", "0"))):
        txt = (c.get("comment_text") or "").strip()
        low = txt.lower()
        if low.startswith("reply:"):
            instr = ("reply", txt[6:].strip())
        elif low == "close":
            instr = ("close", "")
        elif _DONE_MARKER in low:
            instr = None  # already actioned since the last instruction
    return instr


def process_team_instructions(cfg: Config, cu: ClickUp, dry: bool = True) -> int:
    actioned = 0
    for list_id in {cu.list_id, cu.returns_list_id}:
        for task in cu.list_open_tasks(list_id):
            desc = (task.get("description") or "") + (task.get("text_content") or "")
            instr = _latest_instruction(cu.get_task_comments(task["id"]))
            if not instr:
                continue
            kind, text = instr

            if kind == "close":
                if not dry:
                    cu.close_task(task["id"], list_id)
                cu.comment_task(task["id"], f"{_DONE_MARKER}: closed per team instruction.")
                actioned += 1
                continue

            # kind == "reply": deliver `text` to the customer on the original thread
            cm = _CONVO_RE.search(desc)
            chm = _CHANNEL_RE.search(desc)
            convo, channel = (cm.group(1) if cm else None), (chm.group(1) if chm else None)
            if not convo:
                cu.comment_task(task["id"], "⚠️ Couldn't action REPLY — no conversation id on this task.")
                continue

            sent = False
            if channel == "email":
                from .adapters.email_gmail import GmailChannel
                for mb in _MAILBOXES:
                    gm = GmailChannel(mb)
                    if not gm.live:
                        continue
                    try:
                        if not dry:
                            gm.reply_to_thread(convo, text)
                        sent = True
                        break
                    except Exception:
                        continue  # thread not in this mailbox — try the next
            # (TikTok/Meta: same pattern via their send_reply once those channels are live)

            if sent or dry:
                cu.comment_task(task["id"], f"{_DONE_MARKER}: sent to customer & closing.")
                if not dry:
                    cu.close_task(task["id"], list_id)
                actioned += 1
            else:
                cu.comment_task(task["id"], "⚠️ Couldn't deliver REPLY (thread not found / channel not live).")
    return actioned
