import os
from typing import Dict, List
from datetime import datetime


class RulesManager:
    """管理业务分类规则文件"""

    def __init__(self, rules_file: str = 'business_rules.md'):
        self.rules_file = rules_file

    def load_rules(self) -> Dict:
        if not os.path.exists(self.rules_file):
            return {}

        rules = {}
        current_business = None

        with open(self.rules_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # 识别业务名称
                if line.startswith('### ') and '. ' in line:
                    parts = line.split('. ', 1)
                    if len(parts) == 2:
                        current_business = parts[1]
                        rules[current_business] = {
                            'keywords': [],
                            'match_rule': '',
                            'total_hours': 0.0
                        }

                # 提取关键词
                elif line.startswith('- **关键词**：') and current_business:
                    keywords_str = line.split('：', 1)[1]
                    rules[current_business]['keywords'] = [
                        k.strip() for k in keywords_str.split(',')
                    ]

                # 提取匹配规则
                elif line.startswith('- **匹配规则**：`') and current_business:
                    rule = line.split('`', 1)[1].rsplit('`', 1)[0]
                    rules[current_business]['match_rule'] = rule

        return rules

    def save_rules(self, businesses: List[Dict]):
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            f.write("# 业务分类规则\n\n")
            f.write(f"## 元数据\n")
            f.write(f"- 版本：v1.0\n")
            f.write(f"- 更新时间：{datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write("## 业务定义\n\n")

            for i, business in enumerate(businesses, 1):
                f.write(f"### {i}. {business['name']}\n")
                f.write(f"- **关键词**：{', '.join(business['keywords'])}\n")
                f.write(f"- **匹配规则**：`{business['match_rule']}`\n")
                if 'total_hours' in business:
                    f.write(f"- **历史工时**：{business['total_hours']}h\n")
                f.write("\n")

    def update_rules(self, new_businesses: List[Dict]):
        existing = self.load_rules()

        for business in new_businesses:
            if business['name'] not in existing:
                existing[business['name']] = business

        businesses_list = [
            {'name': name, **data}
            for name, data in existing.items()
        ]
        self.save_rules(businesses_list)
