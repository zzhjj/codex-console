"""
核心功能模块

当前仓库已切到 Grok 壳适配模式：
- 保留通用 HTTP 客户端
- 保留注册引擎骨架
- 不再从这里对外导出 OpenAI OAuth 相关能力
"""

from .http_client import (
    OpenAIHTTPClient,
    HTTPClient,
    HTTPClientError,
    RequestConfig,
    create_http_client,
    create_openai_client,
)
from .register import RegistrationEngine, RegistrationResult
from .utils import setup_logging, get_data_dir

__all__ = [
    'OpenAIHTTPClient',
    'HTTPClient',
    'HTTPClientError',
    'RequestConfig',
    'create_http_client',
    'create_openai_client',
    'RegistrationEngine',
    'RegistrationResult',
    'setup_logging',
    'get_data_dir',
]
