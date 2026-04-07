"""
规则管理器测试
"""
import pytest
import os
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
