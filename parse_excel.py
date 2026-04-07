#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
解析禅道工作耗时统计表
"""
from openpyxl import load_workbook
import json

def parse_work_report(file_path):
    """解析工作耗时统计表"""
    wb = load_workbook(file_path)
    ws = wb.active

    # 读取所有数据
    all_data = []
    for row in ws.iter_rows(values_only=True):
        all_data.append(list(row))

    # 解析每个人的工作情况
    people_data = []
    i = 1  # 跳过header

    while i < len(all_data):
        row = all_data[i]

        # 如果第一列有值，说明是新的一行人员数据
        if row[0] is not None:
            person = {
                'name': row[0],
                'total_hours': row[1],
                'projects': []
            }

            # 收集这个人的所有项目（从当前行和后续行）
            current_row = i
            while current_row < len(all_data):
                current = all_data[current_row]

                # 如果是新的人员，停止
                if current_row > i and current[0] is not None:
                    break

                # 提取项目信息（列2-3, 4-5）
                if current[2] is not None and current[3] is not None:
                    person['projects'].append({
                        'name': current[2],
                        'hours': current[3],
                        'tasks': []
                    })

                if current[4] is not None and current[5] is not None:
                    person['projects'].append({
                        'name': current[4],
                        'hours': current[5],
                        'tasks': []
                    })

                # 提取工作详情（最后一列）
                if current[6] is not None:
                    # 尝试匹配到最近的项目
                    if person['projects']:
                        person['projects'][-1]['tasks'].append({
                            'detail': current[6],
                            'hours': current[7]
                        })

                current_row += 1

            people_data.append(person)
            i = current_row
        else:
            i += 1

    return people_data

if __name__ == '__main__':
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else '2026年3月工作耗时统计表.xlsx'

    data = parse_work_report(file_path)

    # 打印结果
    for person in data:
        print(f"\n{'='*60}")
        print(f"姓名: {person['name']}")
        print(f"总耗时: {person['total_hours']} 小时")
        print(f"\n项目列表:")
        for proj in person['projects']:
            print(f"  - {proj['name']}: {proj['hours']} 小时")
            if proj['tasks']:
                print(f"    工作详情:")
                for task in proj['tasks'][:3]:  # 只显示前3条
                    print(f"      * {task['detail'][:50]}... ({task['hours']}h)")

    # 保存为JSON
    with open('work_report.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n\n数据已保存到 work_report.json")
