"""
[ADAPTATION NOTE]
这个文件已改成 Grok 壳兼容占位版。

它不再请求 ChatGPT/Codex 的远端接口，作用只剩：
- 给账号总览页返回一个稳定的数据结构
- 避免你在还没接好 Grok 配额接口前，页面直接报错

后续如果你想接真正的 Grok 配额/状态接口，直接替换 `fetch_codex_overview()` 即可。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ...database.models import Account


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _unknown_quota(label: str) -> Dict[str, Any]:
    return {
        "label": label,
        "status": "unknown",
        "used": None,
        "total": None,
        "remaining": None,
        "percentage": None,
        "source": "grok-shell-placeholder",
    }


def _plan_from_account(account: Account) -> str:
    raw = str(getattr(account, "subscription_type", "") or "").strip().lower()
    if raw in {"team", "plus", "pro", "premium"}:
        return raw
    return "unknown"


def fetch_codex_overview(account: Account, proxy: Optional[str] = None) -> Dict[str, Any]:
    """
    Grok 壳兼容占位函数。

    目前只根据本地账号记录返回一个不会炸页面的结构，不访问任何 OpenAI 远端。
    """
    extra = account.extra_data if isinstance(account.extra_data, dict) else {}
    provider = str(extra.get("provider") or "grok").strip() or "grok"
    cookies = str(extra.get("cookies") or getattr(account, "cookies", "") or "").strip()
    session_token = str(getattr(account, "session_token", "") or "").strip()
    access_token = str(getattr(account, "access_token", "") or "").strip()

    credential_state = "missing"
    if access_token:
        credential_state = "access_token"
    elif session_token:
        credential_state = "session_token"
    elif cookies:
        credential_state = "cookies"

    return {
        "provider": provider,
        "plan_type": _plan_from_account(account),
        "plan_source": "local.account.subscription_type",
        "status": "placeholder",
        "credential_state": credential_state,
        "hourly_quota": _unknown_quota("hourly_quota"),
        "weekly_quota": _unknown_quota("weekly_quota"),
        "code_review_quota": _unknown_quota("code_review_quota"),
        "error": None if credential_state != "missing" else "missing_credentials",
        "stale": False,
        "fetched_at": _now_iso(),
        "notes": [
            "This overview is a local placeholder.",
            "Replace src/core/openai/overview.py with your Grok-specific availability/quota probe when ready.",
        ],
    }
