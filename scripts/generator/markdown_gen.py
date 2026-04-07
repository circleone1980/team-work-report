from typing import List, Dict
from datetime import datetime
from jinja2 import Template


class MarkdownGenerator:
    """Markdown报告生成器"""

    def __init__(self):
        self.template = self._load_template()

    def generate(self, month: str, businesses: List[Dict], unmatched_tasks: List[Dict]) -> str:
        """
        生成Markdown报告

        Args:
            month: 月份（如 2026-03）
            businesses: 业务列表
            unmatched_tasks: 未匹配的任务

        Returns:
            Markdown字符串
        """
        report = self.template.render(
            month=month,
            businesses=businesses,
            unmatched_tasks=unmatched_tasks,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        return report

    def _load_template(self) -> Template:
        """加载报告模板"""
        template_str = """# {{ month }}团队工作月报

## 一、核心业务进展

{% for business in businesses %}
### {{ loop.index }}. {{ business.name }}
{{ business.summary }}

**工时**：{{ business.total_hours }}h | **团队**：{{ business.people|join('、') }}

{% endfor %}

---

{% if unmatched_tasks %}
## 二、其他工作（待确认）

{% for task in unmatched_tasks %}
- **{{ task.person }}**（{{ task.hours }}h）：{{ task.detail }}

{% endfor %}

---

{% endif %}

---

**报告生成时间**：{{ generated_at }}
"""
        return Template(template_str)
