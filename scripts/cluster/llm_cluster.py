"""
LLM聚类器 - 基于大模型的语义理解聚类
"""
from typing import List, Dict
import os
import json


class LLMCluster:
    """基于大模型的智能聚类器"""

    def cluster(self, tasks: List[Dict]) -> List[Dict]:
        """
        使用LLM智能聚类任务

        Args:
            tasks: 任务列表

        Returns:
            业务列表
        """
        # 准备任务数据
        task_list = []
        for task in tasks:
            task_list.append({
                'person': task['person'],
                'detail': task['detail'][:200],  # 限制长度
                'hours': task['hours']
            })

        # 构建提示词
        prompt = self._build_prompt(task_list)

        # 调用大模型（这里用本地模拟，实际可以调用Claude API）
        try:
            # 尝试导入anthropic
            from anthropic import Anthropic

            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if api_key:
                client = Anthropic(api_key=api_key)

                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

                result_text = response.content[0].text

                # 解析JSON
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(1)

                businesses = json.loads(result_text)
                return businesses
        except Exception as e:
            print(f"   LLM调用失败: {e}")
            print("   使用规则聚类...")

        # 降级方案：基于规则聚类
        return self._rule_based_cluster(tasks)

    def _build_prompt(self, tasks: List[Dict]) -> str:
        """构建LLM提示词"""
        prompt = """你是一位团队工作分析专家。请分析以下工作记录，将它们聚类为4-6个核心业务类型。

要求：
1. 业务类型应该是**业务价值导向**（如"形成性评价系统"），而不是项目代码（如"泰擎II期"）
2. 每个业务类型需要提取：
   - name: 业务名称（简洁，5-10字）
   - summary: 业务总结（1-2句话，突出核心成果和价值）
   - total_hours: 总工时
   - people: 参与人员列表
   - sample_tasks: 2-3个代表性任务（每个不超过80字）

3. 业务总结示例：
   - "AI驱动全流程数字化，完成学生画像8维度设计与4类类型生成，实现教师批阅后自动更新"
   - "打通多格式（doc、docx、pdf）文档解析-OCR识别-MD适配链路，集成手写体识别功能"
   - "构建'后台+移动端'一体化平台，完成管理后台全模块开发，对接区县业务"

工作记录：
```json
TASK_DATA_PLACEHOLDER
```

请以JSON格式输出：
```json
{
  "businesses": [
    {
      "name": "业务名称",
      "summary": "业务总结（突出成果和价值）",
      "total_hours": 100.0,
      "people": ["张三", "李四"],
      "sample_tasks": ["任务1描述", "任务2描述"]
    }
  ]
}
```
"""
        # 替换任务数据
        prompt = prompt.replace('TASK_DATA_PLACEHOLDER', json.dumps(tasks, ensure_ascii=False, indent=2))
        return prompt

    def _rule_based_cluster(self, tasks: List[Dict]) -> List[Dict]:
        """基于规则的降级聚类方案"""
        # 定义业务关键词映射（更全面的关键词）
        business_rules = {
            '形成性评价系统': {
                'keywords': [
                    '形成性', '学生画像', '8维度', '批阅', '评价',
                    '学生', '画像', 'AI工作流', '分组作业', '教学优化',
                    '批阅后自动', '教师批阅', '数字化', '类型生成'
                ],
                'tasks': [],
                'hours': 0.0,
                'people': set()
            },
            '实验报告批阅': {
                'keywords': [
                    '报告批阅', 'OCR', '文档解析', '手写体', 'AI批阅',
                    'pdf', 'doc', 'docx', '图片提取', '共性问题',
                    'md适配', '识别ocr', '实验报告', '试卷', '手写',
                    '共性问题分析', '批阅系统', '文档解析', 'base64'
                ],
                'tasks': [],
                'hours': 0.0,
                'people': set()
            },
            '农委土地延包系统': {
                'keywords': [
                    '农委', '土地延包', '土地', '承包', '延包',
                    '后台', '移动端', '一体化平台', '区县业务',
                    '客户管理', '会议模块', '评论点赞', '项目管理',
                    '仪表盘', '权限管理', '流程管理'
                ],
                'tasks': [],
                'hours': 0.0,
                'people': set()
            },
            'AI综合管理平台': {
                'keywords': [
                    'AI重构', 'NSC-100', 'VMC-100', '架构设计', '代码重构',
                    '平台', '底层架构', '遗留问题', '技术支撑', '规模化',
                    'AI引擎', 'T-Mind', 'II期', '泰擎'
                ],
                'tasks': [],
                'hours': 0.0,
                'people': set()
            }
        }

        # 其他工作容器
        other_tasks = []
        other_hours = 0.0
        other_people = set()

        # 匹配任务
        for task in tasks:
            matched = False
            detail = task['detail'].lower()

            for biz_name, biz_data in business_rules.items():
                if any(kw in detail for kw in biz_data['keywords']):
                    biz_data['tasks'].append(task['detail'][:80])
                    biz_data['hours'] += task['hours']
                    biz_data['people'].add(task['person'])
                    matched = True
                    break

            if not matched:
                other_tasks.append(task['detail'][:80])
                other_hours += task['hours']
                other_people.add(task['person'])

        # 构建结果
        businesses = []
        for biz_name, biz_data in business_rules.items():
            if biz_data['hours'] > 0:
                businesses.append({
                    'name': biz_name,
                    'summary': self._generate_business_summary(biz_name, biz_data['tasks']),
                    'total_hours': biz_data['hours'],
                    'people': list(biz_data['people']),
                    'sample_tasks': biz_data['tasks'][:3]
                })

        # 添加其他工作
        if other_hours > 0:
            businesses.append({
                'name': '其他工作',
                'summary': '临时性支持工作和日常维护任务',
                'total_hours': other_hours,
                'people': list(other_people),
                'sample_tasks': other_tasks[:3]
            })

        # 按工时排序
        businesses.sort(key=lambda x: x['total_hours'], reverse=True)

        return businesses

    def _generate_business_summary(self, biz_name: str, tasks: List[str]) -> str:
        """生成业务总结"""
        summaries = {
            '形成性评价系统': 'AI驱动全流程数字化，完成学生画像8维度设计与4类类型生成，实现教师批阅后自动更新，支持分组作业批量处理，为教学优化提供数据支撑。',
            '实验报告批阅': '打通多格式（doc、docx、pdf）文档解析-OCR识别-MD适配链路，集成手写体识别功能，开发共性问题智能提取模块，优化查询性能与安全防护。',
            '农委土地延包系统': '构建"后台+移动端"一体化平台，完成管理后台全模块开发与移动端API集成，对接区县业务并完成数据整理，输出演示材料，支撑业务高效协同。',
            'AI综合管理平台': '落地底层架构优化（AI代码重构、遗留问题修复），搭建稳定技术支撑体系，同步推进NSC-100业务对接设计，为多场景AI应用规模化落地奠定基础。'
        }
        return summaries.get(biz_name, '相关工作')
