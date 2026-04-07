#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
解析禅道工作耗时统计表 - 版本2
修复编码问题，更准确的数据结构
"""
from openpyxl import load_workbook
import json
import re

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
                'name': str(row[0]).strip() if row[0] else '',
                'total_hours': float(row[1]) if row[1] else 0,
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
                # 第一个项目对
                if len(current) > 3 and current[2] is not None and current[3] is not None:
                    project = {
                        'project_name': str(current[2]).strip(),
                        'project_hours': float(current[3]) if current[3] else 0,
                        'detail_name': str(current[4]).strip() if len(current) > 4 and current[4] else '',
                        'detail_hours': float(current[5]) if len(current) > 5 and current[5] else 0,
                        'tasks': []
                    }
                    person['projects'].append(project)

                # 检查是否有第6-7列（某些人可能有更多项目）
                if len(current) > 5 and current[4] is not None and current[5] is not None:
                    # 如果第4列不是任务详情，而是另一个项目
                    if current[6] is None or not str(current[6]).strip().startswith('2026-'):
                        project = {
                            'project_name': str(current[2]).strip() if current[2] else '',
                            'project_hours': float(current[3]) if current[3] else 0,
                            'detail_name': str(current[4]).strip(),
                            'detail_hours': float(current[5]) if current[5] else 0,
                            'tasks': []
                        }
                        # 检查是否已存在相同项目
                        existing = next((p for p in person['projects'] if p['project_name'] == project['project_name']), None)
                        if not existing:
                            person['projects'].append(project)

                # 提取工作详情（最后一列）
                if len(current) > 7 and current[6] is not None:
                    task_detail = str(current[6]).strip()
                    task_hours = float(current[7]) if current[7] else 0

                    # 将任务分配到最后一个项目
                    if person['projects'] and task_detail:
                        # 从任务详情中提取日期
                        date_match = re.match(r'(\d{4}-\d{2}-\d{2}):', task_detail)
                        task_date = date_match.group(1) if date_match else ''

                        person['projects'][-1]['tasks'].append({
                            'date': task_date,
                            'detail': task_detail,
                            'hours': task_hours
                        })

                current_row += 1

            people_data.append(person)
            i = current_row
        else:
            i += 1

    return people_data

def analyze_projects(people_data):
    """分析项目分布"""
    project_stats = {}

    for person in people_data:
        for proj in person['projects']:
            proj_name = proj['project_name']
            if proj_name not in project_stats:
                project_stats[proj_name] = {
                    'total_hours': 0,
                    'people': []
                }
            project_stats[proj_name]['total_hours'] += proj['project_hours']
            if person['name'] not in [p['name'] for p in project_stats[proj_name]['people']]:
                project_stats[proj_name]['people'].append({
                    'name': person['name'],
                    'hours': proj['project_hours']
                })

    return project_stats

if __name__ == '__main__':
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else '2026年3月工作耗时统计表.xlsx'

    data = parse_work_report(file_path)
    project_stats = analyze_projects(data)

    # 保存为JSON
    with open('work_report.json', 'w', encoding='utf-8') as f:
        json.dump({
            'people': data,
            'project_stats': project_stats
        }, f, ensure_ascii=False, indent=2)

    print(f"解析完成！")
    print(f"- 总人数: {len(data)}")
    print(f"- 项目类型: {len(project_stats)}")
    print(f"\n项目列表:")
    for proj_name, stats in sorted(project_stats.items(), key=lambda x: x[1]['total_hours'], reverse=True):
        print(f"  - {proj_name}: {stats['total_hours']:.1f}h ({len(stats['people'])}人)")
    print(f"\n详细数据已保存到 work_report.json")
