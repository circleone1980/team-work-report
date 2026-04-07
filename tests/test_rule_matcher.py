"""
规则匹配器测试
"""
import pytest
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.cluster.rule_matcher import RuleMatcher


def test_match_with_rules():
    """测试规则匹配"""
    matcher = RuleMatcher()

    rules = {
        '形成性评价系统': {
            'keywords': ['形成性', '学生画像', '8维度'],
            'match_rule': '"形成性" in task or "学生画像" in task',
            'total_hours': 120.5
        },
        '实验报告批阅': {
            'keywords': ['报告批阅', 'doc'],
            'match_rule': '"报告批阅" in task or "doc" in task',
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
