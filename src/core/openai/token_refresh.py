"""
[ADAPTATION NOTE]
这个文件已改成 Grok 壳兼容占位版。

它不再尝试刷新 ChatGPT/Codex token，而是：
- 保留 accounts 页面需要的函数签名
- 在未接入 Grok 专属会话刷新逻辑前，返回清晰的占位结果

如果你后续有 Grok 的 session/cookie/sso 刷新方案，直接在这里替换实现即可。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from ...database import crud
from ...database.models import Account
from ...database.session import get_db

logger = logging.getLogger(__name__)


@dataclass
class TokenRefreshResult:
    success: bool
    access_token: str = ""
    refresh_token: str = ""
    expires_at: Optional[datetime] = None
    error_message: str = ""


def _resolve_account(account_id: int) -> Optional[Account]:
    with get_db() as db:
        return crud.get_account_by_id(db, account_id)


def _has_any_credential(account: Optional[Account]) -> bool:
    if not account:
        return False
    for key in ("access_token", "refresh_token", "session_token", "cookies"):
        value = str(getattr(account, key, "") or "").strip()
        if value:
            return True
    extra = account.extra_data if isinstance(account.extra_data, dict) else {}
    for key in ("cookies", "sso", "cf_clearance", "__cf_bm"):
        value = str(extra.get(key) or "").strip()
        if value:
            return True
    return False


def refresh_account_token(account_id: int, proxy_url: Optional[str] = None) -> TokenRefreshResult:
    """
    Grok 壳兼容占位版。

    当前不做实际刷新，只给出明确提示，避免页面直接报错。
    """
    account = _resolve_account(account_id)
    if not account:
        return TokenRefreshResult(success=False, error_message="账号不存在")

    logger.info(
        "Grok placeholder refresh called: account_id=%s email=%s proxy=%s",
        account_id,
        account.email,
        proxy_url or "-",
    )
    return TokenRefreshResult(
        success=False,
        error_message=(
            "当前仓库已切到 Grok 壳模式：Token 刷新逻辑尚未实现。"
            "请在 src/core/openai/token_refresh.py 中改成你自己的 Grok 会话刷新方案。"
        ),
    )


def validate_account_token(account_id: int, proxy_url: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Grok 壳兼容占位版。

    规则很简单：
    - 只要本地记录里存在任意凭证（access_token / session_token / cookies / extra_data.sso）
      就认为“有凭证可供后续流程使用”。
    - 不访问远端，不代表真实可用，只代表“本地已填过凭证”。
    """
    account = _resolve_account(account_id)
    if not account:
        return False, "账号不存在"

    if _has_any_credential(account):
        return True, "local_credentials_present"

    return False, "missing_credentials"
