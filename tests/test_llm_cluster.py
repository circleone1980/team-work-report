"""
LLM聚类器测试
"""
import pytest
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.cluster.llm_cluster import LLMCluster


def test_cluster_by_keywords():
    """测试关键词聚类"""
    cluster = LLMCluster()

    tasks = [
        {'detail': '完成学生画像8维度设计', 'hours': 4.0, 'person': '张三'},
        {'detail': '形成性评价系统优化', 'hours': 6.0, 'person': '李四'},
        {'detail': 'OCR识别功能开发', 'hours': 8.0, 'person': '王五'},
        {'detail': 'doc文档解析', 'hours': 3.0, 'person': '赵六'},
    ]

    businesses = cluster.cluster(tasks)

    # 验证聚类结果
    assert len(businesses) >= 2
    assert any('学生' in b['name'] or '评价' in b['name'] for b in businesses)
    assert any('OCR' in b['name'] or '文档' in b['name'] or '泰擎' in b['name'] for b in businesses)

    # 验证工时统计
    for business in businesses:
        assert 'total_hours' in business
        assert 'people' in business
        assert 'keywords' in business


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
