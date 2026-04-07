"""
LLM聚类器 - 基于关键词的简化版智能聚类
支持智能聚类任务、提取业务名称和关键词、生成业务总结
"""
import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import os


class LLMCluster:
    """基于关键词的简化版LLM聚类器"""

    # 默认业务模式库（关键词到业务名称的映射）
    DEFAULT_BUSINESS_PATTERNS = {
        '系统开发': ['开发', '编码', '实现', '功能', '模块', '接口', '后端', '前端'],
        'Bug修复': ['bug', '修复', '问题', '错误', '异常', '故障'],
        '需求分析': ['需求', '分析', '设计', '评审', '讨论', '沟通'],
        '文档编写': ['文档', '说明', '手册', 'wiki', '注释'],
        '测试验证': ['测试', '验证', '单元测试', '集成测试', '用例'],
        '部署运维': ['部署', '发布', '运维', '服务器', '环境', '配置'],
        '会议沟通': ['会议', '沟通', '汇报', '同步', '讨论'],
        '代码审查': ['review', '审查', '代码评审', 'pr'],
        '数据分析': ['数据', '分析', '报表', '统计', '指标'],
        '学习研究': ['学习', '研究', '调研', '技术调研', '培训'],
    }

    def __init__(self, use_llm: bool = False, api_key: Optional[str] = None):
        """
        初始化聚类器

        Args:
            use_llm: 是否使用LLM进行增强分析
            api_key: Anthropic API密钥（当use_llm=True时需要）
        """
        self.use_llm = use_llm
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.business_patterns = self.DEFAULT_BUSINESS_PATTERNS.copy()

    def cluster_tasks(self, tasks: List[Dict], custom_rules: Optional[Dict] = None) -> Dict[str, List[Dict]]:
        """
        对任务进行聚类分组

        Args:
            tasks: 任务列表，每个任务包含 person, date, project, detail, hours
            custom_rules: 自定义业务规则 {业务名: [关键词列表]}

        Returns:
            按业务分类的任务字典 {业务名: [任务列表]}
        """
        if custom_rules:
            # 合并自定义规则
            self.business_patterns.update(custom_rules)

        # 初始化业务分组
        business_groups = defaultdict(list)

        # 为每个任务匹配业务
        for task in tasks:
            business = self._match_business(task)
            business_groups[business].append(task)

        return dict(business_groups)

    def _match_business(self, task: Dict) -> str:
        """
        根据任务内容匹配业务分类

        Args:
            task: 任务字典

        Returns:
            匹配的业务名称
        """
        detail = task.get('detail', '').lower()
        project = task.get('project', '').lower()

        # 计算每个业务的匹配得分
        scores = {}
        for business, keywords in self.business_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in detail:
                    score += detail.count(keyword)
                if keyword in project:
                    score += project.count(keyword) * 0.5  # 项目名权重较低
            if score > 0:
                scores[business] = score

        # 返回得分最高的业务，如果没有匹配则返回"其他"
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return '其他'

    def extract_business_info(self, business_name: str, tasks: List[Dict]) -> Dict:
        """
        提取业务信息（名称、关键词、总结）

        Args:
            business_name: 业务名称
            tasks: 该业务下的任务列表

        Returns:
            业务信息字典
        """
        if not tasks:
            return {
                'name': business_name,
                'keywords': [],
                'summary': '暂无任务',
                'total_hours': 0.0,
                'task_count': 0
            }

        # 计算总工时
        total_hours = sum(task.get('hours', 0) for task in tasks)

        # 提取关键词
        keywords = self._extract_keywords_from_tasks(tasks)

        # 生成总结
        summary = self._generate_summary(business_name, tasks, total_hours)

        return {
            'name': business_name,
            'keywords': keywords,
            'summary': summary,
            'total_hours': round(total_hours, 2),
            'task_count': len(tasks)
        }

    def _extract_keywords_from_tasks(self, tasks: List[Dict]) -> List[str]:
        """
        从任务列表中提取关键词

        Args:
            tasks: 任务列表

        Returns:
            关键词列表（去重后的前10个）
        """
        keyword_freq = defaultdict(int)

        for task in tasks:
            detail = task.get('detail', '')
            # 使用简单的分词（按空格和常见分隔符分割）
            words = re.findall(r'[\w]+', detail)

            # 过滤掉常见无意义词
            stop_words = {'的', '了', '是', '在', '和', '与', '或', '等', '进行', '完成'}
            for word in words:
                if len(word) >= 2 and word not in stop_words:
                    keyword_freq[word] += 1

        # 按频率排序，取前10个
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_keywords[:10]]

    def _generate_summary(self, business_name: str, tasks: List[Dict], total_hours: float) -> str:
        """
        生成业务总结

        Args:
            business_name: 业务名称
            tasks: 任务列表
            total_hours: 总工时

        Returns:
            业务总结文本
        """
        if not tasks:
            return f"{business_name}暂无相关任务"

        # 提取项目列表
        projects = list(set(task.get('project', '') for task in tasks if task.get('project')))
        project_summary = f"、".join(projects[:3])  # 只显示前3个项目
        if len(projects) > 3:
            project_summary += f"等{len(projects)}个项目"

        # 提取典型任务描述
        details = [task.get('detail', '') for task in tasks if task.get('detail')]
        typical_tasks = details[:2] if len(details) >= 2 else details

        summary_parts = [
            f"**{business_name}**共完成{len(tasks)}项任务",
            f"累计工时{total_hours}小时",
        ]

        if project_summary:
            summary_parts.append(f"涉及{project_summary}")

        if typical_tasks:
            summary_parts.append(f"主要工作包括：{'; '.join(typical_tasks[:2])}")

        return "，".join(summary_parts) + "。"

    def generate_match_rule(self, business_name: str, keywords: List[str]) -> str:
        """
        生成正则表达式匹配规则

        Args:
            business_name: 业务名称
            keywords: 关键词列表

        Returns:
            正则表达式字符串
        """
        if not keywords:
            return f'.*{business_name}.*'

        # 转义特殊字符并构建正则
        escaped_keywords = [re.escape(kw) for kw in keywords]
        pattern = '|'.join(escaped_keywords)
        return f'.*({pattern}).*'

    def auto_create_businesses(self, business_groups: Dict[str, List[Dict]]) -> List[Dict]:
        """
        自动创建业务定义列表

        Args:
            business_groups: 业务分组字典

        Returns:
            业务定义列表，可传入RulesManager.save_rules()
        """
        businesses = []

        for business_name, tasks in business_groups.items():
            business_info = self.extract_business_info(business_name, tasks)
            match_rule = self.generate_match_rule(
                business_name,
                business_info['keywords']
            )

            businesses.append({
                'name': business_name,
                'keywords': business_info['keywords'],
                'match_rule': match_rule,
                'total_hours': business_info['total_hours']
            })

        # 按工时降序排序
        businesses.sort(key=lambda x: x['total_hours'], reverse=True)
        return businesses
