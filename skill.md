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
---

# Team Work Report Skill

自动从禅道Excel工作记录生成团队业务导向的周报/月报。

## 功能特性
- 零配置启动：首次使用自动识别业务类型
- 智能聚类：LLM语义理解，提取业务关键词
- 增量学习：用户确认后持久化规则
- 分层报告：简洁总结 + 详细附录
- 交互式确认：团队负责人可调整分类
