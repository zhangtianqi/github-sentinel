from abc import ABC, abstractmethod
import openai
from github_sentinel.components.config_loader import config
from datetime import datetime, timedelta, timezone


# --- 基类 (保持不变) ---
class BaseSummarizer(ABC):
    """所有摘要器的抽象基类。"""

    @abstractmethod
    def summarize(self, repo_url: str, updates: dict) -> str:
        """为给定的更新生成报告。"""
        pass

    def _get_report_header(self, repo_url: str) -> str:
        """创建一个标准的报告头部。"""
        return f"# 定期报告: {repo_url}\n*由 GitHub Sentinel 生成于 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC*\n\n"


# --- SimpleSummarizer 的完整实现 ---
class SimpleSummarizer(BaseSummarizer):
    """
    生成一个格式化的、未经 AI 处理的原始更新列表。
    它将原始数据转换为易于阅读的 Markdown 报告。
    """

    def _format_updates(self, updates: dict) -> str:
        """将原始更新数据格式化为清晰的 Markdown 文本块。"""
        content = []

        # 1. 新版本发布 (Releases)
        if updates.get('releases'):
            content.append("## 🚀 新版本发布")
            for r in updates['releases']:
                content.append(f"- **{r['name']} ({r['tag_name']})** 由 `{r['author']}` 发布。")
            content.append("")  # 添加空行以分隔

        # 2. 最新提交 (Commits)
        if updates.get('commits'):
            content.append("## ⚙️ 最新提交")
            # 限制最多显示15条，防止报告过长
            for c in updates['commits'][:15]:
                content.append(f"- `{c['sha'][:7]}`: {c['message']} (作者: `{c['author']}`)")
            if len(updates['commits']) > 15:
                content.append("- ... 以及更多提交。")
            content.append("")

        # 3. 拉取请求 (Pull Requests)
        if updates.get('pull_requests'):
            content.append("## 📥 拉取请求 (Pull Requests) 动态")
            for pr in updates['pull_requests']:
                status = "✅ 已合并/关闭" if pr['state'] != 'open' else "📝 开启中"
                content.append(f"- `#{pr['number']}` {pr['title']} (由 `{pr['user']}`) - **状态: {status}**")
            content.append("")

        # 4. 议题 (Issues)
        if updates.get('issues'):
            content.append("## 📝 议题 (Issues) 动态")
            for issue in updates['issues']:
                status = "✅ 已关闭" if issue['state'] != 'open' else "📝 开启中"
                content.append(f"- `#{issue['number']}` {issue['title']} (由 `{issue['user']}`) - **状态: {status}**")
            content.append("")

        return "\n".join(content)

    def summarize(self, repo_url: str, updates: dict) -> str:
        """
        生成最终报告，将报告头和格式化后的更新内容结合起来。
        """
        header = self._get_report_header(repo_url)
        formatted_updates = self._format_updates(updates)

        # 如果格式化后的更新内容为空，则返回“无更新”消息
        if not formatted_updates.strip():
            return header + "在过去的时间段内没有发现重要的更新。"

        return header + formatted_updates


# --- AI 摘要器 (保持不变) ---
class AISummarizer(BaseSummarizer):
    # ... (此处省略 AISummarizer 的代码，保持原样即可)
    """Uses an LLM to generate an intelligent summary of updates."""

    def __init__(self):
        llm_config = config.get('llm', {})
        if not llm_config.get('api_key'):
            raise ValueError("LLM configuration ('llm.api_key') is missing in config.yaml for 'ai' summarizer.")
        self.client = openai.OpenAI(api_key=llm_config['api_key'])
        self.model = llm_config.get('model', 'gpt-4o-mini')

    def _format_updates_for_prompt(self, updates: dict) -> str:
        # 复用 SimpleSummarizer 的格式化方法来为 AI 提供干净的输入
        return SimpleSummarizer()._format_updates(updates)

    def summarize(self, repo_url: str, updates: dict) -> str:
        header = self._get_report_header(repo_url)
        update_text = self._format_updates_for_prompt(updates)

        if not update_text.strip():
            return header + "在过去的时间段内没有发现重要的更新。"

        system_prompt = (
            "You are GitHub Sentinel, an AI assistant for developer teams. Your task is to analyze a list of recent "
            "GitHub repository activities and provide a high-level summary. The summary should be in Chinese. "
            "Structure the report with clear Markdown headings (e.g., '## 关键摘要', '## 需关注的拉取请求', '## 主要变更'). "
            "Focus on what's important for a project manager or team lead to know, avoiding excessive detail. "
            "Start with a brief, high-level '关键摘要' section."
        )

        user_prompt = f"请为以下仓库活动生成一份摘要报告:\n\n{update_text}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            summary = response.choices[0].message.content
            return header + summary
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return header + "生成 AI 摘要时出错。\n\n**原始更新列表:**\n" + update_text


# --- 工厂函数 (保持不变) ---
def get_summarizer() -> BaseSummarizer:
    """
    工厂函数，根据配置获取合适的摘要器。
    """
    summarizer_type = config.get('summarizer', {}).get('type', 'simple')

    if summarizer_type == 'ai':
        print("Using AI Summarizer.")
        return AISummarizer()
    elif summarizer_type == 'simple':
        print("Using Simple Summarizer.")
        return SimpleSummarizer()
    else:
        print(f"Warning: Unknown summarizer type '{summarizer_type}' in config. Defaulting to 'simple'.")
        return SimpleSummarizer()