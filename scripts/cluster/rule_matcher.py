from typing import Dict, List, Tuple, Optional

class RuleMatcher:
    """规则匹配器"""

    def match(self, task: Dict, rules: Dict) -> Optional[str]:
        """
        匹配单个任务到业务

        Args:
            task: 任务字典，包含 'detail' 字段
            rules: 规则字典

        Returns:
            匹配的业务名称，未匹配返回 None
        """
        task_detail = task.get('detail', '')

        for business_name, rule_data in rules.items():
            match_rule = rule_data.get('match_rule', '')

            # 执行匹配规则
            try:
                # 安全的规则执行环境
                if eval(match_rule, {'task': task_detail, '__builtins__': {}}):
                    return business_name
            except:
                # 规则执行失败，跳过
                continue

        return None

    def batch_match(self, tasks: List[Dict], rules: Dict) -> Tuple[List, List]:
        """
        批量匹配任务

        Args:
            tasks: 任务列表
            rules: 规则字典

        Returns:
            (matched_tasks, unmatched_tasks)
            matched_tasks: [(task, business_name), ...]
            unmatched_tasks: [task, ...]
        """
        matched = []
        unmatched = []

        for task in tasks:
            business = self.match(task, rules)
            if business:
                matched.append((task, business))
            else:
                unmatched.append(task)

        return matched, unmatched

    def calculate_match_rate(self, matched: List, total: int) -> float:
        """计算匹配率"""
        if total == 0:
            return 0.0
        return len(matched) / total
