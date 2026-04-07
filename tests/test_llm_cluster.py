import pytest
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
    assert len(businesses) >= 1

    # 验证工时统计
    for business in businesses:
        assert 'total_hours' in business
        assert 'people' in business
        assert 'keywords' in business
        assert 'name' in business


def test_cluster_empty_tasks():
    """测试空任务列表"""
    cluster = LLMCluster()

    businesses = cluster.cluster([])

    assert len(businesses) == 0


def test_cluster_single_task():
    """测试单个任务"""
    cluster = LLMCluster()

    tasks = [
        {'detail': '完成学生画像8维度设计', 'hours': 4.0, 'person': '张三'},
    ]

    businesses = cluster.cluster(tasks)

    assert len(businesses) == 1
    assert businesses[0]['total_hours'] == 4.0
    assert '张三' in businesses[0]['people']


def test_cluster_sort_by_hours():
    """测试按工时排序"""
    cluster = LLMCluster()

    tasks = [
        {'detail': 'OCR识别功能开发', 'hours': 8.0, 'person': '王五'},
        {'detail': 'doc文档解析', 'hours': 3.0, 'person': '赵六'},
        {'detail': '完成学生画像8维度设计', 'hours': 4.0, 'person': '张三'},
    ]

    businesses = cluster.cluster(tasks)

    # 验证按工时降序排列
    hours = [b['total_hours'] for b in businesses]
    assert hours == sorted(hours, reverse=True)


def test_extract_keywords():
    """测试关键词提取"""
    cluster = LLMCluster()

    # 测试逗号分隔的文本
    text = "完成学生画像8维度设计，优化形成性评价系统"
    keywords = cluster._extract_keywords(text)

    assert len(keywords) > 0
    # 关键词应该包含任务描述
    assert any('学生' in kw or '画像' in kw for kw in keywords)


def test_generate_business_name():
    """测试业务名称生成"""
    cluster = LLMCluster()

    # 测试不同关键词的业务名称生成
    name1 = cluster._generate_business_name('学生画像', ['学生画像', '维度'])
    assert name1  # 确保返回非空字符串

    name2 = cluster._generate_business_name('OCR', ['OCR', '识别'])
    assert name2


def test_generate_summary():
    """测试业务总结生成"""
    cluster = LLMCluster()

    tasks = [
        {'detail': '完成学生画像8维度设计'},
        {'detail': '形成性评价系统优化'},
    ]

    summary = cluster._generate_summary(tasks, ['学生画像', '形成性'])

    assert summary  # 确保返回非空字符串
