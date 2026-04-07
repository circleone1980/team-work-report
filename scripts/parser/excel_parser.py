"""
Excel解析器 - 解析禅道导出的工作记录Excel文件
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import re


class ExcelParser:
    """解析禅道导出的Excel工作记录"""

    def parse(self, file_path: str) -> Dict:
        """
        解析Excel文件

        Args:
            file_path: Excel文件路径

        Returns:
            {
                'month': '2026-03',
                'tasks': [
                    {
                        'person': str,
                        'date': str,
                        'project': str,
                        'detail': str,
                        'hours': float
                    }
                ]
            }
        """
        # 读取Excel
        df = pd.read_excel(file_path, engine='openpyxl')

        # 提取任务列表
        tasks = []
        current_person = None
        current_project = None
        current_task = None
        month = None

        for _, row in df.iterrows():
            # 提取姓名（列0）
            if pd.notna(row.iloc[0]):
                current_person = str(row.iloc[0]).strip()

            # 提取迭代/项目（列2）
            if pd.notna(row.iloc[2]):
                current_project = str(row.iloc[2]).strip()

            # 提取任务（列4）
            if pd.notna(row.iloc[4]):
                current_task = str(row.iloc[4]).strip()

            # 提取工作内容（列6）和耗时（列7）
            if pd.notna(row.iloc[6]):
                detail = str(row.iloc[6]).strip()
                hours = float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0.0

                # 提取日期（从detail中）
                date = self._extract_date(detail)

                if date and not month:
                    month = date[:7]  # 提取年月

                task = {
                    'person': current_person,
                    'date': date,
                    'project': current_project,
                    'task': current_task,
                    'detail': detail,
                    'hours': hours
                }
                tasks.append(task)

        return {
            'month': month or datetime.now().strftime('%Y-%m'),
            'tasks': tasks
        }

    def _extract_date(self, text: str) -> Optional[str]:
        """从文本中提取日期"""
        # 匹配 YYYY-MM-DD 格式
        match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if match:
            return match.group(1)
        return None
