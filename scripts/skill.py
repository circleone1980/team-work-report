#!/usr/bin/env python3
"""
团队工作周报/月报生成工具 - 主入口
集成Excel解析、规则匹配、智能聚类和报告生成功能
"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.parser.excel_parser import ExcelParser
from scripts.cluster.rule_matcher import RuleMatcher
from scripts.cluster.llm_cluster import LLMCluster
from scripts.generator.markdown_gen import MarkdownGenerator
from scripts.utils.rules_manager import RulesManager


def main():
    parser = argparse.ArgumentParser(description='生成团队工作周报/月报')
    parser.add_argument('excel_file', help='禅道Excel文件路径')
    parser.add_argument('--type', choices=['weekly', 'monthly'], default='monthly',
                        help='报告类型：weekly(周报) 或 monthly(月报)，默认monthly')
    parser.add_argument('--no-interactive', action='store_true',
                        help='非交互模式，跳过规则确认')
    parser.add_argument('--output', '-o', default='report.md',
                        help='输出文件路径，默认report.md')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细输出模式')

    args = parser.parse_args()

    # 验证输入文件
    excel_path = Path(args.excel_file)
    if not excel_path.exists():
        print(f"错误：文件不存在：{args.excel_file}")
        sys.exit(1)

    # 初始化组件
    excel_parser = ExcelParser()
    rule_matcher = RuleMatcher()
    llm_cluster = LLMCluster()
    report_gen = MarkdownGenerator()
    rules_manager = RulesManager()

    # 1. 解析Excel
    print(f"解析Excel文件：{args.excel_file}")
    data = excel_parser.parse(str(excel_path))
    print(f"  找到 {len(data['tasks'])} 条工作记录")
    if args.verbose:
        print(f"  月份：{data['month']}")

    # 2. 加载规则
    print("\n加载业务规则...")
    rules = rules_manager.load_rules()
    if rules:
        print(f"  已加载 {len(rules)} 条业务规则")
    else:
        print("  未找到现有规则，将使用智能聚类")

    # 3. 业务分组
    businesses = []
    unmatched_tasks = []

    if rules:
        # 使用规则匹配
        matched, unmatched = rule_matcher.batch_match(data['tasks'], rules)
        match_rate = rule_matcher.calculate_match_rate(matched, len(data['tasks']))

        print(f"\n规则匹配结果：")
        print(f"  已匹配：{len(matched)} 条")
        print(f"  未匹配：{len(unmatched)} 条")
        print(f"  匹配率：{match_rate:.1%}")

        # 如果未匹配率 > 30%，触发重新聚类
        if len(unmatched) / len(data['tasks']) > 0.3:
            print(f"\n  发现较多未匹配工作 ({len(unmatched)}条)，启动智能聚类...")
            businesses = llm_cluster.cluster(data['tasks'])

            # 保存新规则
            if not args.no_interactive:
                print("  更新业务规则...")
                _save_businesses_as_rules(businesses, rules_manager)
        else:
            # 转换匹配结果为业务格式
            business_dict = {}
            for task, business_name in matched:
                if business_name not in business_dict:
                    business_dict[business_name] = {
                        'tasks': [],
                        'people': set(),
                        'hours': 0.0
                    }
                business_dict[business_name]['tasks'].append(task)
                business_dict[business_name]['people'].add(task['person'])
                business_dict[business_name]['hours'] += task.get('hours', 0)

            for business_name, info in business_dict.items():
                businesses.append({
                    'name': business_name,
                    'people': list(info['people']),
                    'total_hours': info['hours'],
                    'summary': _generate_summary(business_name, info['tasks'])
                })

            unmatched_tasks = unmatched

        # 按工时排序
        businesses.sort(key=lambda x: x.get('total_hours', 0), reverse=True)

    else:
        # 首次使用，智能聚类
        print("  首次使用，开始智能聚类...")
        businesses = llm_cluster.cluster(data['tasks'])

        if not args.no_interactive:
            print("  保存业务规则...")
            _save_businesses_as_rules(businesses, rules_manager)

    if args.verbose and businesses:
        print(f"\n识别的业务领域：{', '.join([b['name'] for b in businesses])}")

    # 4. 生成报告
    print(f"\n生成{args.type}报告...")
    report = report_gen.generate(
        month=data['month'],
        businesses=businesses,
        unmatched_tasks=unmatched_tasks
    )

    # 5. 保存报告
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding='utf-8')
    print(f"  报告已保存到：{output_path}")

    print("\n完成！")


def _generate_summary(business_name: str, tasks: list) -> str:
    """生成业务总结"""
    if not tasks:
        return f"{business_name}暂无相关任务"

    count = len(tasks)
    hours = sum(t.get('hours', 0) for t in tasks)

    # 获取前3个任务的简述
    details = [t.get('detail', '')[:50] for t in tasks[:3] if t.get('detail')]

    parts = [f"**{business_name}**共完成{count}项任务，累计工时{hours}小时"]
    if details:
        parts.append(f"主要工作包括：{'; '.join(details)}")

    return "，".join(parts) + "。"


def _save_businesses_as_rules(businesses: list, rules_manager):
    """将业务列表保存为规则"""
    rules_data = []
    for b in businesses:
        keywords = b.get('keywords', [])
        if not keywords:
            # 如果没有关键词，从业务名称提取
            keywords = [b['name']]

        rules_data.append({
            'name': b['name'],
            'keywords': keywords,
            'match_rule': f"'{b['name']}' in task or any(kw in task for kw in {keywords})",
            'total_hours': b.get('total_hours', 0)
        })

    rules_manager.save_rules(rules_data)


if __name__ == '__main__':
    main()
