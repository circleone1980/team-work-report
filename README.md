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
