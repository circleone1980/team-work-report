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
    assert len(businesses) >= 2
    assert any('学生' in b['name'] or '评价' in b['name'] for b in businesses)
    assert any('OCR' in b['name'] or '文档' in b['name'] for b in businesses)

    # 验证工时统计
    for business in businesses:
        assert 'total_hours' in business
        assert 'people' in business
        assert 'keywords' in business


def test_extract_keywords():
    """测试关键词提取"""
    cluster = LLMCluster()

    # 使用逗号分隔的文本以匹配实现行为
    text = "完成学生画像8维度设计，优化形成性评价系统"
    keywords = cluster._extract_keywords(text)

    assert len(keywords) > 0
    # 验证关键词包含相关词汇
    all_keywords_str = ' '.join(keywords)
    assert '学生' in all_keywords_str or '画像' in all_keywords_str
    assert '形成性' in all_keywords_str or '评价' in all_keywords_str


def test_generate_business_name():
    """测试业务名称生成"""
    cluster = LLMCluster()

    # 测试形成性评价系统
    name1 = cluster._generate_business_name('学生画像', ['学生画像', '维度'])
    assert name1 == '形成性评价系统'

    # 测试智能文档处理
    name2 = cluster._generate_business_name('OCR', ['OCR', '识别'])
    assert name2 == '智能文档处理'

    # 测试文档解析
    name3 = cluster._generate_business_name('doc', ['doc', '文档', '解析'])
    assert name3 == '智能文档处理'


def test_generate_summary():
    """测试业务总结生成"""
    cluster = LLMCluster()

    tasks = [
        {'detail': '完成学生画像8维度设计'},
        {'detail': '形成性评价系统优化'},
    ]

    summary = cluster._generate_summary(tasks, ['学生画像', '形成性'])

    assert '学生画像' in summary or '形成性' in summary
    assert summary.endswith('。')


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
