"""
集成测试 - 端到端测试整个工作流
"""
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestEndToEnd:
    """端到端集成测试"""

    def test_end_to_end_with_sample_data(self, tmp_path):
        """端到端测试：使用示例数据生成报告"""
        from scripts.skill import main

        # 使用测试固件中的示例数据
        sample_file = project_root / 'tests' / 'fixtures' / 'sample_data.xlsx'
        output_file = tmp_path / 'test_output.md'

        # 模拟命令行参数
        test_argv = [
            'skill.py',
            str(sample_file),
            '--no-interactive',
            '-o',
            str(output_file)
        ]

        with patch.object(sys, 'argv', test_argv):
            # 运行主程序
            main()

        # 验证输出文件存在
        assert output_file.exists()

        # 验证输出内容
        content = output_file.read_text(encoding='utf-8')

        # 检查报告标题
        assert '团队工作月报' in content or '团队工作周报' in content

        # 检查核心章节
        assert '核心业务进展' in content or '工作进展' in content or '##' in content

    def test_help_option(self):
        """测试 --help 选项"""
        from scripts.skill import main

        with patch.object(sys, 'argv', ['skill.py', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_nonexistent_file(self):
        """测试不存在的文件"""
        from scripts.skill import main

        with patch.object(sys, 'argv', ['skill.py', 'nonexistent.xlsx', '--no-interactive']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


class TestComponentIntegration:
    """组件集成测试"""

    def test_parser_to_cluster_flow(self):
        """测试从解析到聚类的流程"""
        from scripts.parser.excel_parser import ExcelParser

        parser = ExcelParser()

        sample_file = project_root / 'tests' / 'fixtures' / 'sample_data.xlsx'
        data = parser.parse(str(sample_file))

        assert data['tasks']
        assert len(data['tasks']) > 0
        assert 'month' in data

    def test_rules_manager_flow(self, tmp_path):
        """测试规则管理器流程"""
        from scripts.utils.rules_manager import RulesManager

        # 使用临时目录测试
        rules_file = tmp_path / 'test_rules.md'

        manager = RulesManager(rules_file=str(rules_file))

        # 测试保存规则
        test_rules = [
            {
                'name': '测试业务',
                'keywords': ['测试', 'test'],
                'match_rule': "'测试' in task",
                'total_hours': 10
            }
        ]

        manager.save_rules(test_rules)
        assert rules_file.exists()

        # 测试加载规则 - load_rules返回字典格式 {业务名: {...}}
        loaded = manager.load_rules()
        assert len(loaded) == 1
        assert '测试业务' in loaded
        assert loaded['测试业务']['keywords'] == ['测试', 'test']


class TestMarkdownGeneration:
    """Markdown生成测试"""

    def test_markdown_generator(self):
        """测试Markdown生成器"""
        from scripts.generator.markdown_gen import MarkdownGenerator

        gen = MarkdownGenerator()

        test_businesses = [
            {
                'name': '前端开发',
                'people': ['张三', '李四'],
                'total_hours': 40,
                'summary': '完成了页面开发工作'
            }
        ]

        report = gen.generate(
            month='2026年3月',
            businesses=test_businesses,
            unmatched_tasks=[]
        )

        assert '2026年3月' in report
        assert '前端开发' in report
        assert '张三' in report or '李四' in report
        assert '##' in report  # Markdown标题格式
