import pytest
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

    # 测试匹配
    task1 = {'detail': '完成学生画像8维度设计'}
    assert matcher.match(task1, rules) == '形成性评价系统'

    task2 = {'detail': 'doc文档解析功能'}
    assert matcher.match(task2, rules) == '实验报告批阅'

    task3 = {'detail': '临时性支持工作'}
    assert matcher.match(task3, rules) is None

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
