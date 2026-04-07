"""
集成测试 - 端到端测试完整流程
"""
import pytest
import os
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.skill import main


def test_end_to_end():
    """端到端测试"""
    # 清理之前的输出
    output_file = Path('tests/fixtures/test_output.md')
    rules_file = Path('business_rules.md')
    if output_file.exists():
        output_file.unlink()
    if rules_file.exists():
        rules_file.unlink()

    # 模拟命令行参数
    sys.argv = [
        'skill.py',
        'tests/fixtures/sample_data.xlsx',
        '--no-interactive',
        '-o',
        'tests/fixtures/test_output.md'
    ]

    # 运行
    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    # 验证输出
    assert output_file.exists()

    content = output_file.read_text(encoding='utf-8')
    assert '团队工作月报' in content
    assert '核心业务进展' in content

    # 清理
    if output_file.exists():
        output_file.unlink()
    if rules_file.exists():
        rules_file.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
