# 团队工作周报/月报生成工具

> 自动从禅道Excel导出生成结构化的团队工作报告

## 项目介绍

这是一个智能的团队工作报告生成工具，能够从禅道导出的Excel表格中自动提取工作记录，通过规则匹配和AI智能聚类，生成结构清晰的周报或月报文档。

### 核心功能

- **Excel解析**：自动解析禅道导出的Excel工作记录表格
- **智能分组**：基于规则匹配和LLM聚类，将工作任务自动分组到业务领域
- **业务规则学习**：自动保存和复用业务分类规则，提升后续处理效率
- **Markdown报告**：生成格式清晰的Markdown格式报告
- **双模式支持**：支持周报和月报两种报告类型

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本用法

```bash
# 生成月报（默认）
python scripts/skill.py 你的文件.xlsx

# 生成周报
python scripts/skill.py 你的文件.xlsx --type weekly

# 指定输出文件
python scripts/skill.py 你的文件.xlsx -o output.md

# 非交互模式（跳过规则确认）
python scripts/skill.py 你的文件.xlsx --no-interactive
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `excel_file` | Excel文件路径（必需） | - |
| `--type` | 报告类型：weekly/monthly | monthly |
| `--output`, `-o` | 输出文件路径 | report.md |
| `--no-interactive` | 非交互模式，跳过规则确认 | False |
| `--verbose`, `-v` | 详细输出模式 | False |
| `--help` | 显示帮助信息 | - |

## 项目结构

```
team-work-report/
├── scripts/
│   └── skill.py              # 主入口程序
├── parser/
│   ├── __init__.py
│   └── excel_parser.py       # Excel解析器
├── cluster/
│   ├── __init__.py
│   ├── rule_matcher.py       # 规则匹配器
│   └── llm_cluster.py        # LLM智能聚类
├── generator/
│   ├── __init__.py
│   └── markdown_gen.py       # Markdown报告生成器
├── templates/
│   └── monthly_report.md     # 月报模板
├── utils/
│   ├── __init__.py
│   └── rules_manager.py      # 业务规则管理器
├── tests/
│   ├── fixtures/             # 测试数据
│   ├── test_integration.py   # 集成测试
│   ├── test_parser.py        # 解析器测试
│   ├── test_rule_matcher.py  # 规则匹配测试
│   ├── test_llm_cluster.py   # 聚类测试
│   ├── test_generator.py     # 生成器测试
│   └── test_rules_manager.py # 规则管理测试
├── requirements.txt          # 依赖清单
├── README.md                 # 本文档
└── skill.md                  # Claude Code技能定义
```

## 输出示例

生成的报告包含以下结构：

```markdown
# 团队工作月报 - 2026年3月

## 核心业务进展

### 1. 前端开发（40小时）
**参与人员**：张三、李四

**工作概述**：完成了页面开发工作

**任务列表**
- 完成登录页面开发 - 张三（8小时）
- 实现数据可视化组件 - 李四（12小时）

### 2. 后端开发（35小时）
...

## 其他工作

- 文档整理与更新 - 王五（5小时）
...
```

## 技术栈

- **Python 3.8+**
- **openpyxl** - Excel文件解析
- **pandas** - 数据处理
- **anthropic** - Claude API集成（智能聚类）
- **jinja2** - 模板引擎
- **pytest** - 测试框架

## 开发与测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_integration.py -v

# 查看测试覆盖率
pytest tests/ --cov=. --cov-report=html
```

### 测试数据

项目包含测试用的示例数据：
- `tests/fixtures/sample_data.xlsx` - 标准测试数据
- `tests/fixtures/empty.xlsx` - 空表格测试数据

## 配置

### API密钥

智能聚类功能需要配置Claude API密钥：

```bash
# 设置环境变量
export ANTHROPIC_API_KEY="your-api-key"

# 或在项目中创建 .env 文件
echo "ANTHROPIC_API_KEY=your-api-key" > .env
```

### 业务规则

首次运行时，工具会自动生成 `business_rules.md` 文件，保存学习的业务分类规则。后续运行会复用这些规则提高效率。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 版本历史

- **v1.0.0** - 初始版本
  - Excel解析功能
  - 规则匹配和智能聚类
  - Markdown报告生成
  - 完整测试覆盖
