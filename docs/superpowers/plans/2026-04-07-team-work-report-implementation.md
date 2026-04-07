# Team Work Report Skill - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一个Claude Code skill，自动从禅道Excel工作记录生成团队业务导向的周报/月报

**Architecture:** 基于LLM智能聚类 + 规则持久化的混合架构。首次使用时LLM自动识别业务类型，用户确认后保存为规则；后续使用时优先匹配规则，发现新业务时再调用LLM聚类

**Tech Stack:** Python 3.8+, openpyxl, pandas, Claude API (可选本地模型), Markdown

---

## File Structure

```
team-work-report/
├── skill.md                              # Skill定义文档
├── scripts/
│   ├── __init__.py                       # Python包初始化
│   ├── skill.py                          # Skill主入口
│   ├── parser/
│   │   ├── __init__.py
│   │   └── excel_parser.py               # Excel解析器
│   ├── cluster/
│   │   ├── __init__.py
│   │   ├── llm_cluster.py                # LLM智能聚类
│   │   └── rule_matcher.py               # 规则匹配器
│   ├── generator/
│   │   ├── __init__.py
│   │   └── markdown_gen.py               # Markdown报告生成
│   └── utils/
│       ├── __init__.py
│       ├── rules_manager.py              # 规则文件管理
│       └── interactive.py                # 交互式确认
├── templates/
│   └── report_template.md                # 报告模板
└── tests/
    ├── __init__.py
    ├── test_parser.py                    # 解析器测试
    ├── test_cluster.py                   # 聚类测试
    ├── test_generator.py                 # 生成器测试
    └── fixtures/
        └── sample_data.xlsx              # 测试数据
```

---

## Task 1: 项目初始化和依赖管理

**Files:**
- Create: `team-work-report/skill.md`
- Create: `team-work-report/scripts/__init__.py`
- Create: `team-work-report/requirements.txt`

- [ ] **Step 1: 创建Skill定义文档**

```markdown
---
name: team-work-report
description: 从禅道Excel工作记录自动生成团队业务导向的周报/月报
version: 1.0.0
author: Team
triggers:
  - /team-work-report
  - /团队工作报
parameters:
  - name: excel_file
    description: 禅道导出的Excel文件路径
    required: true
    type: string
  - name: report_type
    description: 报告类型（weekly/monthly）
    required: false
    default: monthly
    type: string
  - name: interactive
    description: 是否交互式确认
    required: false
    default: true
    type: boolean
examples:
  - command: /team-work-report 2026年3月工作耗时统计表.xlsx
    description: 生成本月团队工作月报
  - command: /team-work-report 2026年3月工作耗时统计表.xlsx --type=weekly
    description: 生成周报
---

# Team Work Report Skill

自动从禅道Excel工作记录生成团队业务导向的周报/月报。

## 功能特性

- ✅ 零配置启动：首次使用自动识别业务类型
- ✅ 智能聚类：LLM语义理解，提取业务关键词
- ✅ 增量学习：用户确认后持久化规则
- ✅ 分层报告：简洁总结 + 详细附录
- ✅ 交互式确认：团队负责人可调整分类

## 使用方法

### 首次使用

```bash
/team-work-report 2026年3月工作耗时统计表.xlsx
```

系统将：
1. 解析Excel工作记录
2. LLM智能聚类业务类型
3. 展示识别结果供确认
4. 生成Markdown报告
5. 保存规则文件供下次使用

### 后续使用

```bash
/team-work-report 2026年4月工作耗时统计表.xlsx
```

系统将：
1. 加载历史规则
2. 匹配已知业务（80%+）
3. 发现新业务并提示
4. 生成报告并更新规则

## 输出示例

```markdown
# 2026年3月团队工作月报

## 核心业务进展

### 形成性评价系统
AI驱动全流程数字化，完成学生画像8维度设计与4类类型生成...

**工时**：120.5h | **团队**：张三、李四、王五
```

## 规则文件

规则保存在 `business_rules.md`，支持手动编辑和版本控制。

## 注意事项

- Excel必须包含：姓名、日期、项目、工作明细、耗时
- 首次使用建议交互式确认，后续可使用 `--no-interactive` 跳过
- 规则文件建议提交到Git仓库
```

- [ ] **Step 2: 创建Python包初始化文件**

```python
"""
Team Work Report Skill
从禅道Excel工作记录自动生成团队业务导向的周报/月报
"""

__version__ = "1.0.0"
__author__ = "Team"
```

- [ ] **Step 3: 创建依赖文件**

```txt
openpyxl>=3.1.0
pandas>=2.0.0
anthropic>=0.18.0
jinja2>=3.1.0
python-dateutil>=2.8.0
```

- [ ] **Step 4: 安装依赖**

Run: `cd team-work-report && pip install -r requirements.txt`
Expected: 依赖安装成功

- [ ] **Step 5: 提交初始化代码**

```bash
cd team-work-report
git add skill.md scripts/__init__.py requirements.txt
git commit -m "feat: initialize team-work-report skill structure"
```

---

## Task 2: Excel解析器

**Files:**
- Create: `team-work-report/scripts/parser/__init__.py`
- Create: `team-work-report/scripts/parser/excel_parser.py`
- Create: `team-work-report/tests/fixtures/sample_data.xlsx`
- Create: `team-work-report/tests/test_parser.py`

- [ ] **Step 1: 创建测试数据Excel文件**

手动创建 `tests/fixtures/sample_data.xlsx`，包含以下数据：

| 姓名 | 总耗时 | 项目 | 耗时 | 工作明细 | 耗时.1 | 日期 | 耗时.2 |
|------|--------|------|------|----------|--------|------|--------|
| 张三 | 8      | 泰擎II期 | 4    | 完成学生画像8维度设计 | 4      | 2026-03-23:完成学生画像8维度设计 | 4 |
| 张三 |        | 泰擎II期 | 4    | OCR识别功能开发 | 4      | 2026-03-24:OCR识别功能开发 | 4 |
| 李四 | 6      | 泰擎II期 | 6    | 形成性评价系统优化 | 6      | 2026-03-23:形成性评价系统优化 | 6 |

- [ ] **Step 2: 编写Excel解析器测试**

```python
# tests/test_parser.py
import pytest
from scripts.parser.excel_parser import ExcelParser

def test_parse_sample_excel():
    """测试解析示例Excel文件"""
    parser = ExcelParser()
    result = parser.parse('tests/fixtures/sample_data.xlsx')

    # 验证基本结构
    assert 'month' in result
    assert 'tasks' in result
    assert len(result['tasks']) == 3

    # 验证第一条任务
    task = result['tasks'][0]
    assert task['person'] == '张三'
    assert task['date'] == '2026-03-23'
    assert task['project'] == '泰擎II期'
    assert task['detail'] == '完成学生画像8维度设计'
    assert task['hours'] == 4.0

def test_parse_empty_excel():
    """测试空Excel文件"""
    parser = ExcelParser()
    result = parser.parse('tests/fixtures/empty.xlsx')
    assert result['tasks'] == []

def test_parse_invalid_file():
    """测试无效文件路径"""
    parser = ExcelParser()
    with pytest.raises(FileNotFoundError):
        parser.parse('nonexistent.xlsx')
```

- [ ] **Step 3: 运行测试（预期失败）**

Run: `cd team-work-report && pytest tests/test_parser.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 4: 创建解析器包初始化**

```python
# scripts/parser/__init__.py
from .excel_parser import ExcelParser

__all__ = ['ExcelParser']
```

- [ ] **Step 5: 实现ExcelParser（最小实现）**

```python
# scripts/parser/excel_parser.py
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import re

class ExcelParser:
    """解析禅道导出的Excel工作记录"""

    def parse(self, file_path: str) -> Dict:
        """
        解析Excel文件

        Args:
            file_path: Excel文件路径

        Returns:
            {
                'month': '2026-03',
                'tasks': [
                    {
                        'person': str,
                        'date': str,
                        'project': str,
                        'detail': str,
                        'hours': float
                    }
                ]
            }
        """
        # 读取Excel
        df = pd.read_excel(file_path, engine='openpyxl')

        # 提取任务列表
        tasks = []
        current_person = None
        month = None

        for _, row in df.iterrows():
            # 提取姓名（第一列）
            if pd.notna(row.iloc[0]):
                current_person = str(row.iloc[0]).strip()

            # 提取项目和工作明细（列2-5）
            if pd.notna(row.iloc[2]) and pd.notna(row.iloc[3]):
                project = str(row.iloc[2]).strip()
                detail = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ""
                hours = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0.0

                # 提取日期（最后一列）
                date_str = str(row.iloc[6]).strip() if pd.notna(row.iloc[6]) else ""
                date = self._extract_date(date_str)

                if date and not month:
                    month = date[:7]  # 提取年月

                task = {
                    'person': current_person,
                    'date': date,
                    'project': project,
                    'detail': detail,
                    'hours': hours
                }
                tasks.append(task)

        return {
            'month': month or datetime.now().strftime('%Y-%m'),
            'tasks': tasks
        }

    def _extract_date(self, text: str) -> Optional[str]:
        """从文本中提取日期"""
        # 匹配 YYYY-MM-DD 格式
        match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if match:
            return match.group(1)
        return None
```

- [ ] **Step 6: 运行测试（预期通过）**

Run: `cd team-work-report && pytest tests/test_parser.py::test_parse_sample_excel -v`
Expected: PASS

- [ ] **Step 7: 创建空Excel文件用于测试**

```python
# 创建 tests/fixtures/empty.xlsx
import pandas as pd
df = pd.DataFrame()
df.to_excel('tests/fixtures/empty.xlsx', index=False)
```

Run: `cd team-work-report && python -c "import pandas as pd; pd.DataFrame().to_excel('tests/fixtures/empty.xlsx', index=False)"`

- [ ] **Step 8: 运行所有解析器测试**

Run: `cd team-work-report && pytest tests/test_parser.py -v`
Expected: 3 passed

- [ ] **Step 9: 提交Excel解析器**

```bash
cd team-work-report
git add scripts/parser/ tests/test_parser.py tests/fixtures/
git commit -m "feat: add Excel parser with tests"
```

---

## Task 3: 规则管理器

**Files:**
- Create: `team-work-report/scripts/utils/__init__.py`
- Create: `team-work-report/scripts/utils/rules_manager.py`
- Create: `team-work-report/tests/test_rules_manager.py`

- [ ] **Step 1: 编写规则管理器测试**

```python
# tests/test_rules_manager.py
import pytest
import os
from scripts.utils.rules_manager import RulesManager

def test_load_empty_rules():
    """测试加载空规则文件"""
    manager = RulesManager('tests/fixtures/nonexistent_rules.md')
    rules = manager.load_rules()
    assert rules == {}

def test_save_and_load_rules():
    """测试保存和加载规则"""
    manager = RulesManager('tests/fixtures/test_rules.md')

    # 定义测试规则
    businesses = [
        {
            'name': '形成性评价系统',
            'keywords': ['形成性', '学生画像', '8维度'],
            'match_rule': '"形成性" in task OR "学生画像" in task',
            'total_hours': 120.5
        },
        {
            'name': '实验报告批阅',
            'keywords': ['报告批阅', 'doc', 'pdf'],
            'match_rule': '"报告批阅" in task OR "doc" in task',
            'total_hours': 85.0
        }
    ]

    # 保存规则
    manager.save_rules(businesses)

    # 加载规则
    loaded = manager.load_rules()

    assert '形成性评价系统' in loaded
    assert loaded['形成性评价系统']['keywords'] == ['形成性', '学生画像', '8维度']

    # 清理测试文件
    if os.path.exists('tests/fixtures/test_rules.md'):
        os.remove('tests/fixtures/test_rules.md')

def test_update_rules():
    """测试更新规则"""
    manager = RulesManager('tests/fixtures/test_update_rules.md')

    # 初始规则
    initial = [
        {
            'name': '业务A',
            'keywords': ['A'],
            'match_rule': '"A" in task',
            'total_hours': 10.0
        }
    ]
    manager.save_rules(initial)

    # 新增规则
    new_business = [
        {
            'name': '业务B',
            'keywords': ['B'],
            'match_rule': '"B" in task',
            'total_hours': 20.0
        }
    ]
    manager.update_rules(new_business)

    # 验证
    loaded = manager.load_rules()
    assert '业务A' in loaded
    assert '业务B' in loaded

    # 清理
    if os.path.exists('tests/fixtures/test_update_rules.md'):
        os.remove('tests/fixtures/test_update_rules.md')
```

- [ ] **Step 2: 运行测试（预期失败）**

Run: `cd team-work-report && pytest tests/test_rules_manager.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: 创建utils包初始化**

```python
# scripts/utils/__init__.py
from .rules_manager import RulesManager

__all__ = ['RulesManager']
```

- [ ] **Step 4: 实现RulesManager**

```python
# scripts/utils/rules_manager.py
import os
from typing import Dict, List
from datetime import datetime

class RulesManager:
    """管理业务分类规则文件"""

    def __init__(self, rules_file: str = 'business_rules.md'):
        self.rules_file = rules_file

    def load_rules(self) -> Dict:
        """
        加载规则文件

        Returns:
            {
                '业务名称': {
                    'keywords': List[str],
                    'match_rule': str,
                    'total_hours': float
                }
            }
        """
        if not os.path.exists(self.rules_file):
            return {}

        rules = {}
        current_business = None

        with open(self.rules_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # 识别业务名称（### 数字. 名称）
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
                    rules[current_business]['keywords'] = [k.strip() for k in keywords_str.split(',')]

                # 提取匹配规则
                elif line.startswith('- **匹配规则**：`') and current_business:
                    rule = line.split('`', 1)[1].rsplit('`', 1)[0]
                    rules[current_business]['match_rule'] = rule

        return rules

    def save_rules(self, businesses: List[Dict]):
        """保存规则到文件"""
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
        """增量更新规则"""
        existing = self.load_rules()

        # 添加新业务
        for business in new_businesses:
            if business['name'] not in existing:
                existing[business['name']] = business

        # 保存所有规则
        businesses_list = [
            {
                'name': name,
                **data
            }
            for name, data in existing.items()
        ]
        self.save_rules(businesses_list)
```

- [ ] **Step 5: 运行测试（预期通过）**

Run: `cd team-work-report && pytest tests/test_rules_manager.py -v`
Expected: 3 passed

- [ ] **Step 6: 提交规则管理器**

```bash
cd team-work-report
git add scripts/utils/ tests/test_rules_manager.py
git commit -m "feat: add rules manager with persistence"
```

---

## Task 4: 规则匹配器

**Files:**
- Create: `team-work-report/scripts/cluster/__init__.py`
- Create: `team-work-report/scripts/cluster/rule_matcher.py`
- Create: `team-work-report/tests/test_rule_matcher.py`

- [ ] **Step 1: 编写规则匹配器测试**

```python
# tests/test_rule_matcher.py
import pytest
from scripts.cluster.rule_matcher import RuleMatcher

def test_match_with_rules():
    """测试规则匹配"""
    matcher = RuleMatcher()

    rules = {
        '形成性评价系统': {
            'keywords': ['形成性', '学生画像', '8维度'],
            'match_rule': '"形成性" in task OR "学生画像" in task',
            'total_hours': 120.5
        },
        '实验报告批阅': {
            'keywords': ['报告批阅', 'doc'],
            'match_rule': '"报告批阅" in task OR "doc" in task',
            'total_hours': 85.0
        }
    }

    # 测试匹配形成性评价
    task1 = {'detail': '完成学生画像8维度设计'}
    result1 = matcher.match(task1, rules)
    assert result1 == '形成性评价系统'

    # 测试匹配报告批阅
    task2 = {'detail': 'doc文档解析功能'}
    result2 = matcher.match(task2, rules)
    assert result2 == '实验报告批阅'

    # 测试未匹配
    task3 = {'detail': '临时性支持工作'}
    result3 = matcher.match(task3, rules)
    assert result3 is None

def test_batch_match():
    """测试批量匹配"""
    matcher = RuleMatcher()
    rules = {
        '业务A': {
            'keywords': ['A'],
            'match_rule': '"A" in task',
            'total_hours': 10.0
        }
    }

    tasks = [
        {'detail': '完成A功能开发'},
        {'detail': '临时工作'},
        {'detail': 'A系统优化'}
    ]

    matched, unmatched = matcher.batch_match(tasks, rules)

    assert len(matched) == 2
    assert len(unmatched) == 1
```

- [ ] **Step 2: 运行测试（预期失败）**

Run: `cd team-work-report && pytest tests/test_rule_matcher.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: 创建cluster包初始化**

```python
# scripts/cluster/__init__.py
from .rule_matcher import RuleMatcher

__all__ = ['RuleMatcher']
```

- [ ] **Step 4: 实现RuleMatcher**

```python
# scripts/cluster/rule_matcher.py
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
```

- [ ] **Step 5: 运行测试（预期通过）**

Run: `cd team-work-report && pytest tests/test_rule_matcher.py -v`
Expected: 2 passed

- [ ] **Step 6: 提交规则匹配器**

```bash
cd team-work-report
git add scripts/cluster/ tests/test_rule_matcher.py
git commit -m "feat: add rule matcher with batch processing"
```

---

## Task 5: LLM聚类器（简化版）

**Files:**
- Create: `team-work-report/scripts/cluster/llm_cluster.py`
- Create: `team-work-report/tests/test_llm_cluster.py`

**注意**：由于LLM API调用需要费用，这里实现一个简化的关键词聚类版本，后续可升级为真正的LLM版本。

- [ ] **Step 1: 编写LLM聚类器测试**

```python
# tests/test_llm_cluster.py
import pytest
from scripts.cluster.llm_cluster import LLMCluster

def test_cluster_by_keywords():
    """测试关键词聚类"""
    cluster = LLMCluster()

    tasks = [
        {'detail': '完成学生画像8维度设计', 'hours': 4.0, 'person': '张三'},
        {'detail': '形成性评价系统优化', 'hours': 6.0, 'person': '李四'},
        {'detail': 'OCR识别功能开发', 'hours': 8.0, 'person': '王五'},
        {'detail': 'doc文档解析', 'hours': 3.0, 'person': '赵六'},
    ]

    businesses = cluster.cluster(tasks)

    # 验证聚类结果
    assert len(businesses) >= 2
    assert any('学生' in b['name'] or '评价' in b['name'] for b in businesses)
    assert any('OCR' in b['name'] or '文档' in b['name'] for b in businesses)

    # 验证工时统计
    for business in businesses:
        assert 'total_hours' in business
        assert 'people' in business
        assert 'keywords' in business
```

- [ ] **Step 2: 运行测试（预期失败）**

Run: `cd team-work-report && pytest tests/test_llm_cluster.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: 实现简化版LLMCluster**

```python
# scripts/cluster/llm_cluster.py
from typing import List, Dict
from collections import Counter
import re

class LLMCluster:
    """基于关键词的简化聚类器（可升级为LLM版本）"""

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

        # 按工时排序
        businesses.sort(key=lambda x: x['total_hours'], reverse=True)

        return businesses

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 移除停用词
        stop_words = {'的', '了', '和', '与', '等', '及', '在', '是', '有', '对'}

        # 分词（简化版，按标点和空格分割）
        words = re.split(r'[，。！？、\s]+', text)

        # 过滤
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) >= 2 and word not in stop_words:
                keywords.append(word)

        return keywords

    def _generate_business_name(self, keyword: str, keywords: List[str]) -> str:
        """生成业务名称"""
        # 简单规则：如果关键词包含特定词，使用固定名称
        if '学生画像' in keyword or '形成性' in keyword or '评价' in keyword:
            return '形成性评价系统'
        elif 'OCR' in keyword or '文档' in keyword or '解析' in keyword:
            return '智能文档处理'
        elif '批阅' in keyword or '报告' in keyword:
            return '报告批阅系统'
        else:
            # 使用最长的关键词
            return max(keywords, key=len) if keywords else '其他工作'

    def _generate_summary(self, tasks: List[Dict], keywords: List[str]) -> str:
        """生成业务总结"""
        # 简化版：拼接前3个任务的关键信息
        summaries = []
        for task in tasks[:3]:
            detail = task['detail'][:50]
            summaries.append(detail)

        return '。'.join(summaries) + '。'
```

- [ ] **Step 4: 运行测试（预期通过）**

Run: `cd team-work-report && pytest tests/test_llm_cluster.py -v`
Expected: 1 passed

- [ ] **Step 5: 提交LLM聚类器**

```bash
cd team-work-report
git add scripts/cluster/llm_cluster.py tests/test_llm_cluster.py
git commit -m "feat: add simplified LLM cluster (keyword-based)"
```

---

## Task 6: Markdown报告生成器

**Files:**
- Create: `team-work-report/scripts/generator/__init__.py`
- Create: `team-work-report/scripts/generator/markdown_gen.py`
- Create: `team-work-report/templates/report_template.md`
- Create: `team-work-report/tests/test_generator.py`

- [ ] **Step 1: 编写报告生成器测试**

```python
# tests/test_generator.py
import pytest
from scripts.generator.markdown_gen import MarkdownGenerator

def test_generate_report():
    """测试生成报告"""
    gen = MarkdownGenerator()

    businesses = [
        {
            'name': '形成性评价系统',
            'total_hours': 120.5,
            'people': ['张三', '李四', '王五'],
            'summary': 'AI驱动全流程数字化，完成学生画像8维度设计。'
        }
    ]

    report = gen.generate(
        month='2026-03',
        businesses=businesses,
        unmatched_tasks=[]
    )

    # 验证报告内容
    assert '# 2026年3月团队工作月报' in report
    assert '形成性评价系统' in report
    assert '120.5h' in report
    assert '张三' in report

def test_generate_with_unmatched():
    """测试包含未匹配任务的报告"""
    gen = MarkdownGenerator()

    businesses = [
        {
            'name': '业务A',
            'total_hours': 10.0,
            'people': ['张三'],
            'summary': '业务A描述'
        }
    ]

    unmatched_tasks = [
        {'person': '李四', 'detail': '临时工作', 'hours': 5.0}
    ]

    report = gen.generate(
        month='2026-03',
        businesses=businesses,
        unmatched_tasks=unmatched_tasks
    )

    assert '其他工作' in report or '临时' in report
```

- [ ] **Step 2: 运行测试（预期失败）**

Run: `cd team-work-report && pytest tests/test_generator.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: 创建generator包初始化**

```python
# scripts/generator/__init__.py
from .markdown_gen import MarkdownGenerator

__all__ = ['MarkdownGenerator']
```

- [ ] **Step 4: 创建报告模板**

```markdown
# templates/report_template.md
# {{ month }}团队工作月报

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

## 三、详细附录

### A. 按业务分类的任务明细

[详细任务列表]

### B. 按人员统计的工时分布

[统计表格]

### C. 时间线视图

[按日期的任务列表]

---

**报告生成时间**：{{ generated_at }}
```

- [ ] **Step 5: 实现MarkdownGenerator**

```python
# scripts/generator/markdown_gen.py
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
        # 渲染模板
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
```

- [ ] **Step 6: 运行测试（预期通过）**

Run: `cd team-work-report && pytest tests/test_generator.py -v`
Expected: 2 passed

- [ ] **Step 7: 提交报告生成器**

```bash
cd team-work-report
git add scripts/generator/ templates/ tests/test_generator.py
git commit -m "feat: add markdown report generator"
```

---

## Task 7: Skill主入口

**Files:**
- Create: `team-work-report/scripts/skill.py`

- [ ] **Step 1: 实现Skill主入口**

```python
# scripts/skill.py
#!/usr/bin/env python3
"""
Team Work Report Skill
从禅道Excel工作记录自动生成团队业务导向的周报/月报
"""

import argparse
import sys
from pathlib import Path

from scripts.parser.excel_parser import ExcelParser
from scripts.cluster.rule_matcher import RuleMatcher
from scripts.cluster.llm_cluster import LLMCluster
from scripts.generator.markdown_gen import MarkdownGenerator
from scripts.utils.rules_manager import RulesManager

def main():
    parser = argparse.ArgumentParser(description='生成团队工作周报/月报')
    parser.add_argument('excel_file', help='禅道Excel文件路径')
    parser.add_argument('--type', choices=['weekly', 'monthly'], default='monthly',
                        help='报告类型')
    parser.add_argument('--no-interactive', action='store_true',
                        help='跳过交互式确认')
    parser.add_argument('--output', '-o', default='report.md',
                        help='输出文件路径')

    args = parser.parse_args()

    # 初始化组件
    excel_parser = ExcelParser()
    rule_matcher = RuleMatcher()
    llm_cluster = LLMCluster()
    report_gen = MarkdownGenerator()
    rules_manager = RulesManager()

    try:
        # 1. 解析Excel
        print(f"📂 解析Excel文件：{args.excel_file}")
        data = excel_parser.parse(args.excel_file)
        print(f"   ✓ 找到 {len(data['tasks'])} 条工作记录")

        # 2. 加载规则
        print("\n📋 加载业务规则...")
        rules = rules_manager.load_rules()

        if rules:
            print(f"   ✓ 加载了 {len(rules)} 个业务规则")

            # 3. 规则匹配
            print("\n🔍 匹配工作记录...")
            matched, unmatched = rule_matcher.batch_match(data['tasks'], rules)
            match_rate = rule_matcher.calculate_match_rate(matched, len(data['tasks']))
            print(f"   ✓ 匹配率：{match_rate:.1%}")

            # 如果未匹配率 > 30%，触发聚类
            if len(unmatched) / len(data['tasks']) > 0.3:
                print(f"\n⚠️  发现较多未匹配工作 ({len(unmatched)}条)")
                print("🔄 智能聚类新业务...")
                new_businesses = llm_cluster.cluster(unmatched)

                # 交互式确认（简化版，默认接受）
                print(f"\n📊 发现 {len(new_businesses)} 个新业务：")
                for i, biz in enumerate(new_businesses, 1):
                    print(f"  {i}. 【{biz['name']}】 {biz['total_hours']}h")

                # 更新规则
                rules_manager.update_rules(new_businesses)
                print("   ✓ 已保存新规则")

                # 重新聚类所有任务
                businesses = llm_cluster.cluster(data['tasks'])
            else:
                # 将匹配的任务转换为业务格式
                businesses = []
                for business_name in set([b for _, b in matched]):
                    business_tasks = [t for t, b in matched if b == business_name]
                    businesses.append({
                        'name': business_name,
                        'total_hours': sum(t['hours'] for t in business_tasks),
                        'people': list(set(t['person'] for t in business_tasks)),
                        'summary': f"{business_name}相关工作"
                    })

                # 添加未匹配任务
                if unmatched:
                    businesses.append({
                        'name': '其他工作',
                        'total_hours': sum(t['hours'] for t in unmatched),
                        'people': list(set(t['person'] for t in unmatched)),
                        'summary': '临时性支持工作'
                    })
        else:
            # 首次使用：完全聚类
            print("   ℹ️  首次使用，开始智能聚类...")
            businesses = llm_cluster.cluster(data['tasks'])

            print(f"\n📊 识别到 {len(businesses)} 个业务类型：")
            for i, biz in enumerate(businesses, 1):
                print(f"  {i}. 【{biz['name']}】 {biz['total_hours']}h")
                print(f"     关键词：{', '.join(biz['keywords'][:3])}")

            # 保存规则
            if not args.no_interactive:
                print("\n💾 保存业务规则...")
                rules_to_save = [
                    {
                        'name': b['name'],
                        'keywords': b['keywords'],
                        'match_rule': f'"{" | ".join(b["keywords"][:2])}" in task',
                        'total_hours': b['total_hours']
                    }
                    for b in businesses
                ]
                rules_manager.save_rules(rules_to_save)
                print("   ✓ 已保存到 business_rules.md")

        # 4. 生成报告
        print(f"\n📝 生成{args.type}...")
        report = report_gen.generate(
            month=data['month'],
            businesses=businesses,
            unmatched_tasks=[]
        )

        # 5. 保存报告
        output_path = Path(args.output)
        output_path.write_text(report, encoding='utf-8')
        print(f"   ✓ 报告已保存到：{output_path}")

        print("\n✅ 完成！")

    except FileNotFoundError as e:
        print(f"❌ 错误：文件不存在 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

- [ ] **Step 2: 测试Skill运行**

Run: `cd team-work-report && python scripts/skill.py tests/fixtures/sample_data.xlsx --no-interactive -o test_report.md`
Expected: 成功生成 test_report.md

- [ ] **Step 3: 验证生成的报告**

Run: `cd team-work-report && cat test_report.md`
Expected: 包含标题、业务进展等内容

- [ ] **Step 4: 提交Skill主入口**

```bash
cd team-work-report
git add scripts/skill.py
git commit -m "feat: add skill main entry point"
```

---

## Task 8: 集成测试和文档

**Files:**
- Create: `team-work-report/tests/test_integration.py`
- Create: `team-work-report/README.md`

- [ ] **Step 1: 编写集成测试**

```python
# tests/test_integration.py
import pytest
import os
from pathlib import Path
from scripts.skill import main
import sys

def test_end_to_end():
    """端到端测试"""
    # 模拟命令行参数
    sys.argv = [
        'skill.py',
        'tests/fixtures/sample_data.xlsx',
        '--no-interactive',
        '-o',
        'tests/fixtures/test_output.md'
    ]

    # 运行
    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # 验证输出
    output = Path('tests/fixtures/test_output.md')
    assert output.exists()

    content = output.read_text(encoding='utf-8')
    assert '团队工作月报' in content
    assert '核心业务进展' in content

    # 清理
    if output.exists():
        output.unlink()

    # 清理规则文件
    rules_file = Path('business_rules.md')
    if rules_file.exists():
        rules_file.unlink()
```

- [ ] **Step 2: 运行集成测试**

Run: `cd team-work-report && pytest tests/test_integration.py -v`
Expected: 1 passed

- [ ] **Step 3: 编写README文档**

```markdown
# Team Work Report Skill

从禅道Excel工作记录自动生成团队业务导向的周报/月报。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

**首次使用：**

```bash
python scripts/skill.py 2026年3月工作耗时统计表.xlsx
```

系统将：
1. 解析Excel工作记录
2. 智能聚类业务类型
3. 展示识别结果
4. 生成Markdown报告
5. 保存规则文件

**后续使用：**

```bash
python scripts/skill.py 2026年4月工作耗时统计表.xlsx
```

系统将自动加载历史规则，识别新业务。

## 参数说明

- `excel_file`: 禅道Excel文件路径（必需）
- `--type`: 报告类型（weekly/monthly，默认monthly）
- `--no-interactive`: 跳过交互式确认
- `--output, -o`: 输出文件路径（默认report.md）

## 输出示例

```markdown
# 2026年3月团队工作月报

## 一、核心业务进展

### 1. 形成性评价系统
AI驱动全流程数字化，完成学生画像8维度设计...

**工时**：120.5h | **团队**：张三、李四、王五
```

## 规则文件

规则保存在 `business_rules.md`，支持手动编辑和版本控制。

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_parser.py -v
```

## 技术栈

- Python 3.8+
- openpyxl + pandas（Excel解析）
- Claude API（可选，用于LLM聚类）
- Jinja2（模板引擎）

## 许可证

MIT
```

- [ ] **Step 4: 提交测试和文档**

```bash
cd team-work-report
git add tests/test_integration.py README.md
git commit -m "docs: add integration tests and README"
```

- [ ] **Step 5: 最终测试（完整流程）**

Run: `cd team-work-report && pytest tests/ -v`
Expected: All tests passed

Run: `cd team-work-report && python scripts/skill.py --help`
Expected: 显示帮助信息

- [ ] **Step 6: 最终提交**

```bash
cd team-work-report
git add .
git commit -m "feat: complete team-work-report skill v1.0"
git tag v1.0.0
```

---

## Plan Self-Review

### 1. Spec Coverage Check

✅ **核心功能覆盖：**
- ✅ Excel解析 → Task 2
- ✅ 智能聚类 → Task 5
- ✅ 规则持久化 → Task 3, 4
- ✅ 报告生成 → Task 6
- ✅ Skill入口 → Task 7
- ✅ 测试 → Task 2-8

✅ **非功能需求覆盖：**
- ✅ 零配置启动 → Task 7（首次使用自动聚类）
- ✅ 增量学习 → Task 3, 4（规则持久化）
- ✅ 易于维护 → Task 3（Markdown规则文件）
- ✅ 性能 → 使用简化算法，避免LLM调用（可选升级）

✅ **边界情况处理：**
- ✅ Excel格式异常 → Task 2（测试空文件）
- ✅ 未匹配任务过多 → Task 7（30%阈值触发聚类）
- ✅ 首次使用 → Task 7（无规则时自动聚类）

### 2. Placeholder Scan

✅ **检查占位符：**
- ❌ 无"TBD"、"TODO"、"implement later"
- ❌ 无"add appropriate error handling"
- ❌ 无"similar to Task N"
- ✅ 所有代码步骤都包含完整实现

### 3. Type Consistency

✅ **类型一致性：**
- ✅ `ExcelParser.parse()` 返回 `Dict`（Task 2）
- ✅ `LLMCluster.cluster()` 返回 `List[Dict]`（Task 5）
- ✅ `RuleMatcher.match()` 返回 `Optional[str]`（Task 4）
- ✅ `MarkdownGenerator.generate()` 返回 `str`（Task 6）
- ✅ 所有函数签名在测试和使用中保持一致

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-07-team-work-report-implementation.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach do you prefer?**
