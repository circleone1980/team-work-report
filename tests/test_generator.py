"""
Tests for MarkdownGenerator class.
"""
import pytest
import os
import tempfile
from scripts.generator.markdown_generator import MarkdownGenerator


@pytest.fixture
def sample_data():
    """Create sample parsed data."""
    return {
        'month': '2026-03',
        'tasks': [
            {
                'person': '张三',
                'date': '2026-03-01',
                'project': '项目A',
                'detail': '完成需求文档',
                'hours': 8.0
            },
            {
                'person': '张三',
                'date': '2026-03-02',
                'project': '项目A',
                'detail': '完成API开发',
                'hours': 8.0
            },
            {
                'person': '李四',
                'date': '2026-03-01',
                'project': '项目B',
                'detail': '编写测试用例',
                'hours': 7.0
            },
            {
                'person': '李四',
                'date': '2026-03-03',
                'project': '项目C',
                'detail': '完成页面开发',
                'hours': 8.0
            },
        ]
    }


@pytest.fixture
def generator():
    """Create a MarkdownGenerator instance."""
    return MarkdownGenerator()


class TestMarkdownGenerator:
    """Test MarkdownGenerator functionality."""

    def test_generate_basic_report(self, generator, sample_data):
        """Test basic report generation."""
        result = generator.generate(sample_data)

        assert isinstance(result, str)
        assert len(result) > 0
        assert '2026-03' in result
        assert '张三' in result
        assert '李四' in result
        assert '项目A' in result
        assert '项目B' in result

    def test_generate_includes_overview(self, generator, sample_data):
        """Test that report includes overview section."""
        result = generator.generate(sample_data)

        assert '概述' in result
        assert '统计概览' in result
        assert '参与人数' in result
        assert '总工时' in result

    def test_generate_includes_project_summary(self, generator, sample_data):
        """Test that report includes project summary."""
        result = generator.generate(sample_data)

        assert '项目汇总' in result
        assert '项目A' in result
        assert '项目B' in result

    def test_generate_includes_person_details(self, generator, sample_data):
        """Test that report includes person details."""
        result = generator.generate(sample_data)

        assert '人员详情' in result
        assert '张三' in result
        assert '李四' in result

    def test_stats_calculation(self, generator, sample_data):
        """Test statistics calculation."""
        stats = generator._calculate_stats(sample_data)

        assert stats['total_people'] == 2
        assert stats['total_hours'] == 31.0
        assert stats['total_projects'] == 3
        assert stats['total_tasks'] == 4

    def test_project_summaries(self, generator, sample_data):
        """Test project summaries preparation."""
        projects = generator._prepare_project_summaries(sample_data)

        assert len(projects) == 3

        # Find projectA
        project_a = next((p for p in projects if p['name'] == '项目A'), None)
        assert project_a is not None
        assert project_a['total_hours'] == 16.0
        assert project_a['people_count'] == 1
        assert project_a['task_count'] == 2

    def test_person_details(self, generator, sample_data):
        """Test person details preparation."""
        people = generator._prepare_person_details(sample_data)

        assert len(people) == 2

        # Find 张三
        person_zhang = next((p for p in people if p['name'] == '张三'), None)
        assert person_zhang is not None
        assert person_zhang['total_hours'] == 16.0
        assert person_zhang['project_count'] == 1
        assert person_zhang['task_count'] == 2
        assert len(person_zhang['tasks']) == 2

    def test_save_report(self, generator, sample_data):
        """Test saving report to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'output', 'test_report.md')

            generator.save('# Test Report', output_path)

            assert os.path.exists(output_path)

            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            assert content == '# Test Report'

    def test_generate_and_save(self, generator, sample_data):
        """Test generate and save combined method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'report.md')

            content = generator.generate_and_save(sample_data, output_path)

            assert os.path.exists(output_path)

            with open(output_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            assert saved_content == content

    def test_empty_data(self, generator):
        """Test handling empty data."""
        empty_data = {'month': '2026-03', 'tasks': []}
        result = generator.generate(empty_data)

        assert '2026-03' in result
        assert '0' in result  # Should show 0 for counts

    def test_template_exists(self, generator):
        """Test that the template file exists."""
        template_path = os.path.join(generator.template_dir, 'team_report.md.j2')
        assert os.path.exists(template_path)

    def test_generated_markdown_structure(self, generator, sample_data):
        """Test that generated Markdown has correct structure."""
        result = generator.generate(sample_data)

        # Check for proper Markdown headers
        assert '# ' in result  # H1
        assert '## ' in result  # H2
        assert '### ' in result  # H3

        # Check for lists
        assert '- ' in result

        # Check for horizontal rules
        assert '---' in result
