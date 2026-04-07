"""
Excel解析器测试
"""
import pytest
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.parser.excel_parser import ExcelParser


def test_parse_sample_excel():
    """测试解析示例Excel文件"""
    parser = ExcelParser()
    result = parser.parse('tests/fixtures/sample_data.xlsx')

    # 验证基本结构
    assert 'month' in result
    assert 'tasks' in result
    assert len(result['tasks']) == 3

    # 验证第一条任务
    task = result['tasks'][0]
    assert task['person'] == '张三'
    assert task['date'] == '2026-03-23'
    assert task['project'] == '泰擎II期'
    assert task['detail'] == '完成学生画像8维度设计'
    assert task['hours'] == 4.0


def test_parse_empty_excel():
    """测试空Excel文件"""
    parser = ExcelParser()
    result = parser.parse('tests/fixtures/empty.xlsx')
    assert result['tasks'] == []


def test_parse_invalid_file():
    """测试无效文件路径"""
    parser = ExcelParser()
    with pytest.raises(FileNotFoundError):
        parser.parse('nonexistent.xlsx')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
