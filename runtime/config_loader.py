"""Load the agent's brain: brand config, autonomy rules, channel config, playbook + templates.

The markdown playbook in ../cs-agent/ is the agent's knowledge; the YAML configs are its policy.
Everything is read at runtime so editing the repo updates the agent with no code change.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# repo root = parent of runtime/
ROOT = Path(__file__).resolve().parent.parent
CS = ROOT / "cs-agent"


def _read_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


class Config:
    """Resolved agent configuration for one brand."""

    def __init__(self, brand: str = "fandecor") -> None:
        self.brand_name = brand
        self.brand = _read_yaml(CS / "config" / f"brand.{brand}.yaml")
        self.autonomy = _read_yaml(CS / "config" / "autonomy.yaml")
        self.channels = _read_yaml(CS / "config" / "channels.yaml")
        # Playbook text (used as LLM context)
        self.skill = _read_text(CS / "SKILL.md")
        self.triage = _read_text(CS / "playbook" / "triage.md")
        self.guardrails = _read_text(CS / "playbook" / "guardrails.md")
        self.templates = {
            p.stem: _read_text(p)
            for p in sorted((CS / "playbook" / "templates").glob("*.md"))
        }

    # ----- policy helpers -------------------------------------------------
    def policy_confirmed(self, key: str) -> bool:
        """Has a brand policy been confirmed? Unconfirmed => never auto-send a reply quoting it."""
        pol = self.brand.get("policies", {}).get(key, {})
        return bool(pol.get("confirmed"))

    @property
    def mode(self) -> str:
        return self.autonomy.get("mode", "draft_only")

    @property
    def auto_confirm_refunds(self) -> bool:
        return bool(self.autonomy.get("auto_confirm_refunds", False))

    @property
    def refund_cap_gbp(self) -> Optional[float]:
        g = self.brand.get("guardrails", {}).get("refund_cap_gbp", {})
        return g.get("value") if g.get("confirmed") else None

    @property
    def approver(self) -> Dict[str, Any]:
        return self.brand.get("guardrails", {}).get("named_approver", {})

    @property
    def cs_operator(self) -> Dict[str, Any]:
        return self.brand.get("guardrails", {}).get("cs_operator", {})

    @property
    def money_task_assignees(self) -> list:
        return self.brand.get("guardrails", {}).get("money_task_assignees_clickup_ids", [])

    @property
    def cover_clickup_id(self) -> Optional[str]:
        """If set, ALL CS tasks route to this person (e.g. a colleague covering while others are off)."""
        return self.brand.get("guardrails", {}).get("cover_clickup_id") or None

    @property
    def cover_slack_id(self) -> Optional[str]:
        """If set, ALL Slack pings (approval/escalation) go to this person instead of the approver."""
        return self.brand.get("guardrails", {}).get("cover_slack_id") or None

    def category_action(self, category: str) -> str:
        """Base action for a triage category from autonomy.yaml (auto_send/draft/escalate/gated/close)."""
        cats = self.autonomy.get("categories", {})
        return cats.get(category, {}).get("action", "draft")

    def live_channels(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: cfg
            for name, cfg in self.channels.get("channels", {}).items()
            if cfg.get("status") == "live"
        }


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def is_dry_run() -> bool:
    return env("DRY_RUN", "true").lower() != "false"
