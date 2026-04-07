import os
import pytest
import tempfile
from scripts.utils.rules_manager import RulesManager


@pytest.fixture
def temp_rules_file():
    """创建临时规则文件"""
    fd, path = tempfile.mkstemp(suffix='.md')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def manager(temp_rules_file):
    """创建RulesManager实例"""
    return RulesManager(rules_file=temp_rules_file)


class TestRulesManager:
    """测试RulesManager类"""

    def test_load_empty_rules(self, manager):
        """测试加载空规则文件"""
        # 文件不存在时返回空字典
        manager_no_file = RulesManager(rules_file='non_existent_file.md')
        rules = manager_no_file.load_rules()
        assert rules == {}

    def test_save_and_load_rules(self, manager):
        """测试保存和加载规则"""
        businesses = [
            {
                'name': '系统开发',
                'keywords': ['开发', '编码', '实现'],
                'match_rule': r'.*(开发|编码|实现).*',
                'total_hours': 120.5
            },
            {
                'name': '会议沟通',
                'keywords': ['会议', '讨论', '沟通'],
                'match_rule': r'.*(会议|讨论|沟通).*',
                'total_hours': 45.0
            }
        ]

        # 保存规则
        manager.save_rules(businesses)

        # 加载规则
        loaded_rules = manager.load_rules()

        # 验证
        assert len(loaded_rules) == 2
        assert '系统开发' in loaded_rules
        assert '会议沟通' in loaded_rules

        # 验证系统开发的数据
        dev_rules = loaded_rules['系统开发']
        assert dev_rules['keywords'] == ['开发', '编码', '实现']
        assert dev_rules['match_rule'] == r'.*(开发|编码|实现).*'

        # 验证会议沟通的数据
        meeting_rules = loaded_rules['会议沟通']
        assert meeting_rules['keywords'] == ['会议', '讨论', '沟通']
        assert meeting_rules['match_rule'] == r'.*(会议|讨论|沟通).*'

    def test_update_rules(self, manager):
        """测试更新规则（新增业务）"""
        # 先保存现有规则
        existing_businesses = [
            {
                'name': '系统开发',
                'keywords': ['开发', '编码'],
                'match_rule': r'.*(开发|编码).*'
            }
        ]
        manager.save_rules(existing_businesses)

        # 添加新业务
        new_businesses = [
            {
                'name': '文档编写',
                'keywords': ['文档', '说明'],
                'match_rule': r'.*(文档|说明).*'
            }
        ]
        manager.update_rules(new_businesses)

        # 验证原有业务保留，新业务添加
        loaded_rules = manager.load_rules()
        assert len(loaded_rules) == 2
        assert '系统开发' in loaded_rules
        assert '文档编写' in loaded_rules

    def test_update_rules_existing_business(self, manager):
        """测试更新已存在的业务（不应重复）"""
        # 先保存现有规则
        existing_businesses = [
            {
                'name': '系统开发',
                'keywords': ['开发', '编码'],
                'match_rule': r'.*(开发|编码).*'
            }
        ]
        manager.save_rules(existing_businesses)

        # 尝试添加同名业务
        new_businesses = [
            {
                'name': '系统开发',
                'keywords': ['开发', '编码', '实现'],
                'match_rule': r'.*(开发|编码|实现).*'
            }
        ]
        manager.update_rules(new_businesses)

        # 验证没有重复
        loaded_rules = manager.load_rules()
        assert len(loaded_rules) == 1
        assert '系统开发' in loaded_rules
        # 原有规则保持不变
        assert loaded_rules['系统开发']['keywords'] == ['开发', '编码']

    def test_save_rules_format(self, manager):
        """测试保存规则的文件格式"""
        businesses = [
            {
                'name': '系统开发',
                'keywords': ['开发', '编码'],
                'match_rule': r'.*(开发|编码).*',
                'total_hours': 100.0
            }
        ]
        manager.save_rules(businesses)

        # 读取文件内容验证格式
        with open(manager.rules_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert '# 业务分类规则' in content
        assert '## 元数据' in content
        assert '版本：v1.0' in content
        assert '## 业务定义' in content
        assert '### 1. 系统开发' in content
        assert '- **关键词**：开发, 编码' in content
