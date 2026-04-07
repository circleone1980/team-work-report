"""
Markdown报告生成器测试
"""
import pytest
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

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
    assert '# 2026-03团队工作月报' in report
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
