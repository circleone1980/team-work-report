"""
Tests for ExcelParser class.
"""
import pytest
import pandas as pd
from scripts.parser.excel_parser import ExcelParser
import os


@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a sample Excel file for testing."""
    file_path = tmp_path / "test_sample.xlsx"

    data = [
        ['姓名', '总工时', '项目', '工时', '工作明细', '明细工时', '日期', '每日工时'],
        ['张三', 40, '项目A', 20, '需求分析', 10, '2026-03-01:完成需求文档', 8],
        ['', '', '', '', '开发工作', 10, '2026-03-02:完成API开发', 8],
        ['李四', 35, '项目B', 15, '测试工作', 15, '2026-03-01:编写测试用例', 7],
        ['', '', '项目C', 20, '前端开发', 20, '2026-03-03:完成页面开发', 8],
    ]

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False, header=False)

    return str(file_path)


@pytest.fixture
def empty_excel_file(tmp_path):
    """Create an empty Excel file for testing."""
    file_path = tmp_path / "empty.xlsx"
    df = pd.DataFrame([['姓名', '总工时']])
    df.to_excel(file_path, index=False, header=False)
    return str(file_path)


@pytest.fixture
def parser():
    """Create an ExcelParser instance."""
    return ExcelParser()


class TestExcelParser:
    """Test ExcelParser functionality."""

    def test_parse_sample_excel(self, parser, sample_excel_file):
        """Test parsing a sample Excel file."""
        result = parser.parse(sample_excel_file)

        assert 'month' in result
        assert 'tasks' in result
        assert result['month'] == '2026-03'
        assert len(result['tasks']) >= 2

        # Check first task
        first_task = result['tasks'][0]
        assert first_task['person'] == '张三'
        assert first_task['project'] == '项目A'
        assert first_task['date'] == '2026-03-01'
        assert first_task['hours'] == 20.0

    def test_parse_empty_excel(self, parser, empty_excel_file):
        """Test parsing an empty Excel file."""
        result = parser.parse(empty_excel_file)

        assert 'month' in result
        assert 'tasks' in result
        assert len(result['tasks']) == 0

    def test_extract_date(self, parser):
        """Test date extraction from text."""
        assert parser._extract_date('2026-03-01:完成需求文档') == '2026-03-01'
        assert parser._extract_date('2026/03/01 some text') is None
        assert parser._extract_date('no date here') is None
        assert parser._extract_date('') is None

    def test_get_tasks_by_person(self, parser, sample_excel_file):
        """Test grouping tasks by person."""
        data = parser.parse(sample_excel_file)
        result = parser.get_tasks_by_person(data)

        assert '张三' in result
        assert '李四' in result
        assert len(result['张三']) >= 1

    def test_get_tasks_by_project(self, parser, sample_excel_file):
        """Test grouping tasks by project."""
        data = parser.parse(sample_excel_file)
        result = parser.get_tasks_by_project(data)

        assert '项目A' in result
        assert '项目B' in result or '项目C' in result

    def test_get_total_hours_by_person(self, parser, sample_excel_file):
        """Test calculating total hours per person."""
        data = parser.parse(sample_excel_file)
        result = parser.get_total_hours_by_person(data)

        assert '张三' in result
        assert result['张三'] > 0

    def test_get_total_hours_by_project(self, parser, sample_excel_file):
        """Test calculating total hours per project."""
        data = parser.parse(sample_excel_file)
        result = parser.get_total_hours_by_project(data)

        assert '项目A' in result
        assert result['项目A'] > 0

    def test_parse_invalid_file(self, parser):
        """Test parsing a non-existent file."""
        with pytest.raises(FileNotFoundError):
            parser.parse('non_existent_file.xlsx')

    def test_month_extraction(self, parser, sample_excel_file):
        """Test that month is correctly extracted from dates."""
        result = parser.parse(sample_excel_file)

        assert result['month'] == '2026-03'
