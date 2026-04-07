---
name: team-work-report
description: 从禅道Excel工作记录自动生成团队业务导向的周报/月报。当用户有禅道导出的工作记录Excel文件需要生成报告时使用此skill。
version: 1.0.0
author: Team
license: MIT
triggers:
  - /team-work-report
  - /团队工作报
  - /周报
  - /月报
---

# Team Work Report Skill

自动从禅道Excel工作记录生成团队业务导向的周报/月报。

## 功能特性

- **零配置启动**：首次使用自动识别业务类型
- **智能聚类**：基于关键词的自动业务聚类（可升级为LLM）
- **增量学习**：用户确认后持久化规则，持续优化
- **分层报告**：简洁总结 + 详细附录
- **交互式确认**：团队负责人可调整分类
- **多格式支持**：周报/月报模式切换

## 使用方法

### 基本用法

```bash
# 在Claude Code中使用
/team-work-report <Excel文件路径>

# 或使用命令行
python scripts/skill.py <excel_file> [options]
```

### 参数说明

- `excel_file` (必需): 禅道导出的Excel工作记录文件路径
- `--type {weekly,monthly}`: 报告类型（默认：monthly）
- `--no-interactive`: 非交互模式，跳过用户确认
- `--output, -o`: 输出文件路径（默认：report.md）

### 示例

```bash
# 生成本月月报
/team-work-report "2026年3月工作耗时统计表.xlsx"

# 生成周报（非交互模式）
python scripts/skill.py data.xlsx --type weekly --no-interactive

# 指定输出文件
python scripts/skill.py data.xlsx --type monthly -o monthly_report.md
```

## 输出格式

生成的报告包含：

1. **核心业务进展** - 按业务类型组织的工作总结
2. **其他工作** - 未分类或临时性工作
3. **详细附录** - 完整的任务明细

### 报告示例

```markdown
# 2026-03团队工作月报

## 一、核心业务进展

### 1. 形成性评价系统
AI驱动全流程数字化，完成学生画像8维度设计...

**工时**: 120.5h | **团队**: 张三、李四、王五

### 2. 实验报告批阅
打通多格式（doc、docx、pdf）文档解析链路...

**工时**: 85.0h | **团队**: 赵六、钱七
```

## 技术架构

### 核心模块

1. **Excel解析器** (`scripts/parser/excel_parser.py`)
   - 解析禅道Excel格式
   - 提取人员、项目、工时数据

2. **规则管理器** (`scripts/utils/rules_manager.py`)
   - 持久化业务分类规则
   - 支持增量更新

3. **智能聚类器** (`scripts/cluster/llm_cluster.py`)
   - 基于关键词的自动聚类
   - 可升级为真实LLM API

4. **报告生成器** (`scripts/generator/markdown_gen.py`)
   - Jinja2模板引擎
   - 生成结构化Markdown

### 增量学习流程

1. **首次使用**: 自动聚类所有任务 → 用户确认 → 保存规则
2. **后续使用**: 加载规则 → 匹配任务 → 仅聚类未匹配项（>30%）→ 更新规则

## 依赖

```
openpyxl>=3.1.0
pandas>=2.0.0
anthropic>=0.18.0
jinja2>=3.1.0
python-dateutil>=2.8.0
```

## 配置

### 规则文件

规则保存在 `business_rules.md`，格式：

```markdown
# 业务分类规则

## 元数据
- 版本：v1.0
- 更新时间：2026-04-07

## 业务定义

### 1. 形成性评价系统
- **关键词**: 形成性, 学生画像, 8维度
- **匹配规则**: "形成性" in task
- **历史工时**: 120.5h
```

## 开发

### 测试

```bash
pytest tests/ -v
```

当前测试覆盖：35个测试全部通过

### 项目结构

```
team-work-report/
├── SKILL.md              # Skill定义
├── README.md             # 使用文档
├── requirements.txt      # 依赖清单
├── scripts/
│   ├── skill.py         # 主入口
│   ├── parser/          # Excel解析
│   ├── cluster/         # 聚类和匹配
│   ├── generator/       # 报告生成
│   └── utils/           # 工具类
├── templates/           # Jinja2模板
└── tests/              # 测试套件
```

## 版本历史

### v1.0.0 (2026-04-07)
- ✅ 首次发布
- ✅ Excel解析功能
- ✅ 关键词聚类算法
- ✅ Markdown报告生成
- ✅ 规则持久化
- ✅ 35个测试通过

## 许可证

MIT License

## GitHub

https://github.com/circleone1980/team-work-report
