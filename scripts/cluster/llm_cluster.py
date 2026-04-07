"""
LLM聚类器 - 基于关键词的简化版智能聚类
支持智能聚类任务、提取业务名称和关键词、生成业务总结
"""
import re
from typing import Dict, List
from collections import Counter


class LLMCluster:
    """基于关键词的简化聚类器（可升级为LLM版本）"""

    # 业务名称识别规则
    BUSINESS_NAME_RULES = {
        '形成性评价系统': ['学生画像', '形成性', '评价'],
        '智能文档处理': ['OCR', '文档', '解析', 'doc'],
        '报告批阅系统': ['批阅', '报告'],
    }

    # 停用词列表
    STOP_WORDS = {'的', '了', '和', '与', '等', '及', '在', '是', '有', '对'}

    def cluster(self, tasks: List[Dict]) -> List[Dict]:
        """
        智能聚类任务

        Args:
            tasks: 任务列表

        Returns:
            业务列表
        """
        # 提取所有关键词
        all_keywords = []
        for task in tasks:
            keywords = self._extract_keywords(task['detail'])
            all_keywords.extend(keywords)

        # 统计关键词频率
        keyword_freq = Counter(all_keywords)

        # 选择高频关键词作为聚类中心
        top_keywords = [k for k, v in keyword_freq.most_common(10)]

        # 基于关键词聚类
        businesses = []
        used_tasks = set()

        for keyword in top_keywords:
            if keyword in used_tasks:
                continue

            # 找到包含该关键词的所有任务
            cluster_tasks = []
            cluster_people = set()
            cluster_hours = 0.0
            cluster_keywords = [keyword]

            for i, task in enumerate(tasks):
                if i in used_tasks:
                    continue

                if keyword in task['detail']:
                    cluster_tasks.append(task)
                    cluster_people.add(task['person'])
                    cluster_hours += task['hours']
                    used_tasks.add(i)

                    # 提取其他关键词
                    other_keywords = self._extract_keywords(task['detail'])
                    cluster_keywords.extend(other_keywords)

            if cluster_tasks:
                # 去重关键词
                cluster_keywords = list(set(cluster_keywords))[:5]

                businesses.append({
                    'name': self._generate_business_name(keyword, cluster_keywords),
                    'keywords': cluster_keywords,
                    'total_hours': cluster_hours,
                    'people': list(cluster_people),
                    'sample_tasks': [t['detail'][:60] for t in cluster_tasks[:3]],
                    'summary': self._generate_summary(cluster_tasks, cluster_keywords)
                })

        # 处理未被分配的任务
        for i, task in enumerate(tasks):
            if i not in used_tasks:
                keywords = self._extract_keywords(task['detail'])
                businesses.append({
                    'name': self._generate_business_name('', keywords),
                    'keywords': keywords[:5],
                    'total_hours': task['hours'],
                    'people': [task['person']],
                    'sample_tasks': [task['detail'][:60]],
                    'summary': self._generate_summary([task], keywords)
                })

        # 按工时排序
        businesses.sort(key=lambda x: x['total_hours'], reverse=True)

        return businesses

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 分词（简化版，按标点和空格分割）
        words = re.split(r'[，。！？、\s,!?]+', text)

        # 过滤
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) >= 2 and word not in self.STOP_WORDS:
                keywords.append(word)

        return keywords

    def _generate_business_name(self, keyword: str, keywords: List[str]) -> str:
        """生成业务名称"""
        # 简单规则：如果关键词包含特定词，使用固定名称
        for business_name, rule_keywords in self.BUSINESS_NAME_RULES.items():
            for rule_keyword in rule_keywords:
                if rule_keyword in keyword or any(rule_keyword in k for k in keywords):
                    return business_name

        # 使用最长的关键词
        return max(keywords, key=len) if keywords else '其他工作'

    def _generate_summary(self, tasks: List[Dict], keywords: List[str]) -> str:
        """生成业务总结"""
        # 简化版：拼接前3个任务的关键信息
        summaries = []
        for task in tasks[:3]:
            detail = task['detail'][:50]
            summaries.append(detail)

        return '。'.join(summaries) + ('。' if summaries else '')
