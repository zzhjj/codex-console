"""
[ADAPTATION NOTE]
这个文件已从 OpenAI/Codex 注册主引擎，改造成适配 Grok 的“骨架版”。

保留内容：
- Web 壳依赖的统一接口：RegistrationEngine.run() / save_to_database()
- 任务日志回调
- RegistrationResult 数据结构
- 数据库存储入口

你需要自己补的内容：
- 真正的 Grok 注册流程（临时邮箱、验证码、会话、SSO、cookies 等）
- Grok 特定的请求参数和响应解析
- 成功后如何从你的注册流程里提取最终凭证

推荐填充顺序：
1. 实现 _prepare_registration_context()
2. 实现 _perform_registration()
3. 按你的返回结果组装 RegistrationArtifacts
4. 用 build_success_result() 返回给 Web 壳
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from ..database import crud
from ..database.session import get_db
from ..services import BaseEmailService

logger = logging.getLogger(__name__)


@dataclass
class RegistrationResult:
    """Web 壳与路由层使用的统一注册结果。"""

    success: bool
    email: str = ""
    password: str = ""
    account_id: str = ""
    workspace_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    id_token: str = ""
    session_token: str = ""
    device_id: str = ""
    error_message: str = ""
    logs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = "register"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "email": self.email,
            "password": self.password,
            "account_id": self.account_id,
            "workspace_id": self.workspace_id,
            "access_token": self.access_token[:20] + "..." if self.access_token else "",
            "refresh_token": self.refresh_token[:20] + "..." if self.refresh_token else "",
            "id_token": self.id_token[:20] + "..." if self.id_token else "",
            "session_token": self.session_token[:20] + "..." if self.session_token else "",
            "device_id": self.device_id,
            "error_message": self.error_message,
            "logs": self.logs or [],
            "metadata": self.metadata or {},
            "source": self.source,
        }


@dataclass
class RegistrationArtifacts:
    """给你自己补 Grok 内核时使用的中间结果结构。"""

    email: str = ""
    password: str = ""
    account_id: str = ""
    workspace_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    id_token: str = ""
    session_token: str = ""
    device_id: str = ""
    cookies: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class RegistrationEngine:
    """
    Grok 注册骨架引擎。

    这个类不再包含 OpenAI 特定实现，只保留：
    - 任务日志
    - Web 壳兼容接口
    - 数据库存储

    你后续真正要改的就是：
    - _prepare_registration_context
    - _perform_registration
    - （可选）_normalize_artifacts
    """

    def __init__(
        self,
        email_service: BaseEmailService,
        proxy_url: Optional[str] = None,
        callback_logger: Optional[Callable[[str], None]] = None,
        task_uuid: Optional[str] = None,
    ):
        self.email_service = email_service
        self.proxy_url = proxy_url
        self.callback_logger = callback_logger or (lambda msg: logger.info(msg))
        self.task_uuid = task_uuid
        self.logs: list[str] = []

    # ---------------------------------------------------------------------
    # 通用日志 / 结果辅助
    # ---------------------------------------------------------------------
    def _log(self, message: str, level: str = "info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.logs.append(log_message)

        if self.callback_logger:
            self.callback_logger(log_message)

        if self.task_uuid:
            try:
                with get_db() as db:
                    crud.append_task_log(db, self.task_uuid, log_message)
            except Exception as exc:
                logger.warning(f"记录任务日志失败: {exc}")

        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)

    def build_success_result(self, artifacts: RegistrationArtifacts) -> RegistrationResult:
        metadata = dict(artifacts.metadata or {})
        if artifacts.cookies and "cookies" not in metadata:
            metadata["cookies"] = artifacts.cookies
        metadata.setdefault("provider", "grok")
        metadata.setdefault("adapter", "grok-shell-skeleton")

        return RegistrationResult(
            success=True,
            email=artifacts.email,
            password=artifacts.password,
            account_id=artifacts.account_id,
            workspace_id=artifacts.workspace_id,
            access_token=artifacts.access_token,
            refresh_token=artifacts.refresh_token,
            id_token=artifacts.id_token,
            session_token=artifacts.session_token,
            device_id=artifacts.device_id,
            logs=self.logs.copy(),
            metadata=metadata,
            source="register",
        )

    def build_failure_result(self, error_message: str, **metadata: Any) -> RegistrationResult:
        payload = {"provider": "grok", "adapter": "grok-shell-skeleton", **metadata}
        return RegistrationResult(
            success=False,
            error_message=error_message,
            logs=self.logs.copy(),
            metadata=payload,
            source="register",
        )

    # ---------------------------------------------------------------------
    # 你后续该实现的三个骨架点
    # ---------------------------------------------------------------------
    def _prepare_registration_context(self) -> Dict[str, Any]:
        """
        TODO: 这里准备你的 Grok 注册上下文。

        你可以在这里做：
        - 初始化 session / headers
        - 选择代理
        - 准备邮箱地址
        - 拉取注册页面参数
        - 记录 site_key / action_id / state_tree 等
        """
        self._log("[骨架] _prepare_registration_context() 尚未实现", "warning")
        return {
            "provider": "grok",
            "proxy_url": self.proxy_url,
            "email_service": getattr(getattr(self.email_service, "service_type", None), "value", None)
            or getattr(self.email_service, "service_type", "unknown"),
        }

    def _perform_registration(self, context: Dict[str, Any]) -> RegistrationArtifacts:
        """
        TODO: 在这里真正执行你的 Grok 注册流程。

        建议你最终返回 RegistrationArtifacts，例如：
            return RegistrationArtifacts(
                email="xxx@example.com",
                password="...",
                session_token="...",
                cookies="sso=...; ...",
                metadata={"provider": "grok", "notes": "..."},
            )
        """
        raise NotImplementedError(
            "Grok 注册内核尚未实现：请在 src/core/register.py 的 _perform_registration() 中填入你自己的流程。"
        )

    def _normalize_artifacts(self, artifacts: RegistrationArtifacts) -> RegistrationArtifacts:
        """可选：统一整理你的结果结构。"""
        artifacts.metadata = dict(artifacts.metadata or {})
        artifacts.metadata.setdefault("provider", "grok")
        artifacts.metadata.setdefault("adapter", "grok-shell-skeleton")
        return artifacts

    # ---------------------------------------------------------------------
    # Web 壳实际调用的主入口
    # ---------------------------------------------------------------------
    def run(self) -> RegistrationResult:
        self._log("[系统] 已切换到 Grok 注册骨架引擎")
        self._log("[系统] 保留的是 Web 控制台壳、任务状态和实时日志")
        self._log("[系统] 真正需要你补的是 src/core/register.py 里的 Grok 注册步骤")

        try:
            context = self._prepare_registration_context()
            self._log("[系统] 注册上下文已准备（骨架）")

            artifacts = self._perform_registration(context)
            artifacts = self._normalize_artifacts(artifacts)

            if not artifacts.email:
                self._log("[错误] 注册实现返回了空邮箱，请检查你的 Grok 注册流程", "error")
                return self.build_failure_result(
                    "Grok 注册实现返回了空邮箱，请检查 _perform_registration()",
                    stage="validate_artifacts",
                )

            self._log(f"[成功] Grok 注册流程返回结果：{artifacts.email}")
            return self.build_success_result(artifacts)

        except NotImplementedError as exc:
            self._log(f"[待实现] {exc}", "warning")
            self._log("[提示] 你可以先在这个文件里完成 Grok 的页面参数抓取、邮箱验证码和会话提取", "warning")
            return self.build_failure_result(str(exc), stage="not_implemented")

        except Exception as exc:
            self._log(f"[异常] Grok 注册骨架执行失败: {exc}", "error")
            return self.build_failure_result(str(exc), stage="exception")

    # ---------------------------------------------------------------------
    # 数据库存储：保留给 Web 壳继续用
    # ---------------------------------------------------------------------
    def save_to_database(self, result: RegistrationResult):
        if not result.success:
            self._log("[系统] 注册未成功，跳过数据库保存", "warning")
            return None

        email_service_name = (
            getattr(getattr(self.email_service, "service_type", None), "value", None)
            or getattr(self.email_service, "service_type", None)
            or "manual"
        )

        metadata = dict(result.metadata or {})
        cookies = str(metadata.get("cookies") or "").strip() or None

        with get_db() as db:
            existing = crud.get_account_by_email(db, result.email)
            payload = dict(
                password=result.password or None,
                session_token=result.session_token or None,
                account_id=result.account_id or None,
                workspace_id=result.workspace_id or None,
                access_token=result.access_token or None,
                refresh_token=result.refresh_token or None,
                id_token=result.id_token or None,
                cookies=cookies,
                proxy_used=self.proxy_url,
                extra_data=metadata,
                status="active",
                source=result.source or "register",
            )

            if existing:
                self._log(f"[系统] 数据库中已存在账号，转为更新：{result.email}")
                return crud.update_account(db, existing.id, **payload)

            self._log(f"[系统] 正在写入数据库：{result.email}")
            return crud.create_account(
                db,
                email=result.email,
                email_service=str(email_service_name),
                **payload,
            )
