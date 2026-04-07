# Team Work Report Skill

从禅道Excel工作记录自动生成团队业务导向的周报/月报。

## 快速开始

### 方式一：全局安装（推荐）

安装为Claude Code全局skill，可在任何目录使用：

```bash
# 克隆仓库
git clone https://github.com/circleone1980/team-work-report.git
cd team-work-report

# 安装到全局skills目录
python install_global.py
```

安装后，在Claude Code中任何位置都可以使用：

```bash
/team-work-report <Excel文件路径>
```

卸载全局skill：

```bash
python install_global.py uninstall
```

### 方式二：本地使用

**安装依赖：**

```bash
pip install -r requirements.txt
```

**使用方法：**

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

**当前测试状态：** 35/35 通过 ✅

## 项目结构

```
team-work-report/
├── SKILL.md                 # Skill定义（全局安装后使用）
├── README.md                # 本文档
├── requirements.txt         # Python依赖
├── install_global.py        # 全局安装脚本
├── scripts/
│   ├── skill.py            # 主入口
│   ├── parser/             # Excel解析模块
│   ├── cluster/            # 聚类模块
│   ├── generator/          # 报告生成模块
│   └── utils/              # 工具类
├── templates/              # Jinja2模板
├── tests/                  # 测试套件
└── examples/               # 示例报告
```

## 技术栈

- **Python 3.8+**
- **openpyxl + pandas**（Excel解析）
- **Claude API**（可选，用于LLM聚类）
- **Jinja2**（模板引擎）

## 核心功能

### 1. 智能聚类
- 基于关键词的自动业务类型识别
- 支持升级为真实LLM API
- 自动发现新业务类型

### 2. 增量学习
- 规则持久化存储
- 支持增量更新
- 团队负责人可调整分类

### 3. 灵活报告
- 周报/月报模式
- Markdown格式输出
- 业务导向的组织结构

## 更新日志

### v1.0.0 (2026-04-07)
- ✅ 首次发布
- ✅ Excel解析功能
- ✅ 关键词聚类算法
- ✅ Markdown报告生成
- ✅ 规则持久化
- ✅ 全局安装支持
- ✅ 35个测试通过

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## GitHub

https://github.com/circleone1980/team-work-report

---

**Made with ❤️ for better team reporting**
