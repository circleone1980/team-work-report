#!/usr/bin/env python3
"""
Team Work Report Skill
从禅道Excel工作记录自动生成团队业务导向的周报/月报
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
                        help='报告类型')
    parser.add_argument('--no-interactive', action='store_true',
                        help='跳过交互式确认')
    parser.add_argument('--output', '-o', default='report.md',
                        help='输出文件路径')

    args = parser.parse_args()

    # 初始化组件
    excel_parser = ExcelParser()
    rule_matcher = RuleMatcher()
    llm_cluster = LLMCluster()
    report_gen = MarkdownGenerator()
    rules_manager = RulesManager()

    try:
        # 1. 解析Excel
        print(f"解析Excel文件：{args.excel_file}")
        data = excel_parser.parse(args.excel_file)
        print(f"   找到 {len(data['tasks'])} 条工作记录")

        # 1.5. 确认团队成员（仅在交互模式下）
        all_people = list(set([task['person'] for task in data['tasks']]))
        default_members = ['谢强', '王利刚', '邓新', '郭晓雨', '蒋伟杰']

        if not args.no_interactive:
            print(f"\n团队成员确认：")
            print(f"   默认成员：{', '.join(default_members)}")
            print(f"   Excel中的所有人员：{', '.join(sorted(all_people))}")

            # 检查默认成员是否都在Excel中
            missing = [m for m in default_members if m not in all_people]
            if missing:
                print(f"   警告：默认成员 {', '.join(missing)} 不在Excel数据中")

            response = input("\n是否需要调整成员？（输入新成员列表，用逗号分隔；直接回车使用默认）: ").strip()
            if response:
                selected_members = [m.strip() for m in response.split('，') if m.strip()]
                if not selected_members:
                    selected_members = [m.strip() for m in response.split(',') if m.strip()]
            else:
                selected_members = default_members
        else:
            selected_members = default_members

        # 过滤只保留指定成员的工作记录
        original_count = len(data['tasks'])
        data['tasks'] = [task for task in data['tasks'] if task['person'] in selected_members]
        filtered_count = len(data['tasks'])

        print(f"\n过滤工作记录：")
        print(f"   选中成员：{', '.join(selected_members)}")
        print(f"   保留 {filtered_count}/{original_count} 条记录")

        if filtered_count == 0:
            print("错误：没有找到选中成员的工作记录")
            sys.exit(1)

        # 2. 加载规则
        print("\n加载业务规则...")
        rules = rules_manager.load_rules()

        if rules:
            print(f"   加载了 {len(rules)} 个业务规则")

            # 3. 规则匹配
            print("\n匹配工作记录...")
            matched, unmatched = rule_matcher.batch_match(data['tasks'], rules)
            match_rate = rule_matcher.calculate_match_rate(matched, len(data['tasks']))
            print(f"   匹配率：{match_rate:.1%}")

            # 如果未匹配率 > 30%，触发聚类
            if len(unmatched) / len(data['tasks']) > 0.3:
                print(f"\n发现较多未匹配工作 ({len(unmatched)}条)")
                print("智能聚类新业务...")
                new_businesses = llm_cluster.cluster(unmatched)

                # 交互式确认（简化版，默认接受）
                print(f"\n发现 {len(new_businesses)} 个新业务：")
                for i, biz in enumerate(new_businesses, 1):
                    print(f"  {i}. 【{biz['name']}】 {biz['total_hours']}h")

                # 更新规则
                rules_manager.update_rules([
                    {
                        'name': b['name'],
                        'keywords': b['keywords'],
                        'match_rule': f'"{" | ".join(b["keywords"][:2])}" in task',
                        'total_hours': b['total_hours']
                    }
                    for b in new_businesses
                ])
                print("   已保存新规则")

                # 重新聚类所有任务
                businesses = llm_cluster.cluster(data['tasks'])
            else:
                # 将匹配的任务转换为业务格式
                businesses = []
                for business_name in set([b for _, b in matched]):
                    business_tasks = [t for t, b in matched if b == business_name]
                    businesses.append({
                        'name': business_name,
                        'total_hours': sum(t['hours'] for t in business_tasks),
                        'people': list(set(t['person'] for t in business_tasks)),
                        'summary': f"{business_name}相关工作"
                    })

                # 添加未匹配任务
                if unmatched:
                    businesses.append({
                        'name': '其他工作',
                        'total_hours': sum(t['hours'] for t in unmatched),
                        'people': list(set(t['person'] for t in unmatched)),
                        'summary': '临时性支持工作'
                    })
        else:
            # 首次使用：完全聚类
            print("   首次使用，开始智能聚类...")
            businesses = llm_cluster.cluster(data['tasks'])

            print(f"\n识别到 {len(businesses)} 个业务类型：")
            for i, biz in enumerate(businesses, 1):
                print(f"  {i}. 【{biz['name']}】 {biz['total_hours']:.1f}h")
                if 'keywords' in biz:
                    print(f"     关键词：{', '.join(biz['keywords'][:3])}")
                elif 'sample_tasks' in biz and biz['sample_tasks']:
                    print(f"     示例：{biz['sample_tasks'][0][:60]}...")

            # 保存规则（仅当有keywords字段时）
            if not args.no_interactive:
                print("\n保存业务规则...")
                rules_to_save = []
                for b in businesses:
                    if 'keywords' in b:
                        rules_to_save.append({
                            'name': b['name'],
                            'keywords': b['keywords'],
                            'match_rule': f'"{" | ".join(b["keywords"][:2])}" in task',
                            'total_hours': b['total_hours']
                        })

                if rules_to_save:
                    rules_manager.save_rules(rules_to_save)
                    print("   已保存到 business_rules.md")
                else:
                    print("   跳过规则保存（无关键词数据）")

        # 4. 生成报告
        print(f"\n生成{args.type}...")
        report = report_gen.generate(
            month=data['month'],
            businesses=businesses,
            unmatched_tasks=[]
        )

        # 5. 保存报告
        # 如果用户没有指定输出路径（使用默认值），则输出到Excel文件所在目录
        if args.output == 'report.md':  # 默认值
            excel_path = Path(args.excel_file)
            output_path = excel_path.parent / f"{excel_path.stem}_报告.md"
        else:
            output_path = Path(args.output)

        output_path.write_text(report, encoding='utf-8')
        print(f"   报告已保存到：{output_path}")

        return output_path

        print("\n完成！")

    except FileNotFoundError as e:
        print(f"错误：文件不存在 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
