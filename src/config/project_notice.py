"""Shared project notice content for terminal and Web UI."""

PROJECT_NOTICE = {
    "title": "Grok 壳适配说明",
    "free_notice": "当前版本已裁掉支付/绑卡入口，保留 Web 壳、任务状态和实时日志。真正的 Grok 注册内核仍需你自行替换。",
    "disclaimer": (
        "免责声明：本工具仅供学习和研究使用，使用本工具产生的一切后果由使用者自行承担。"
        "请遵守相关服务的使用条款，不要用于任何违法或不当用途。"
        "如有侵权，请及时联系，会及时删除。"
    ),
    "github_repo_name": "请改成你自己的仓库名",
    "github_repo_url": "请改成你自己的 GitHub 仓库地址",
    "qq_group_id": "（可自行修改）",
    "qq_group_url": "#",
    "telegram_name": "（可自行修改）",
    "telegram_url": "#",
    "afdian_name": "（可自行修改）",
    "afdian_url": "#",
}


def build_terminal_notice_lines() -> list[str]:
    """Build terminal-friendly notice lines."""
    return [
        "=" * 72,
        "Grok 壳适配说明",
        PROJECT_NOTICE["free_notice"],
        "建议先阅读仓库根目录 GROK_SHELL_ADAPTATION.md 与页面中的 /adaptation-guide。",
        f"GitHub 仓库 {PROJECT_NOTICE['github_repo_name']}：{PROJECT_NOTICE['github_repo_url']}",
        f"QQ交流群 {PROJECT_NOTICE['qq_group_id']}：{PROJECT_NOTICE['qq_group_url']}",
        f"Telegram频道 {PROJECT_NOTICE['telegram_name']}：{PROJECT_NOTICE['telegram_url']}",
        PROJECT_NOTICE["disclaimer"],
        "=" * 72,
    ]
