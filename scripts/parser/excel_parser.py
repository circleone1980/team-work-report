"""
Excel Parser for Zentao exported work records.
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import re


class ExcelParser:
    """Parse Zentao exported Excel work records."""

    def parse(self, file_path: str) -> Dict:
        """
        Parse Excel file and extract work records.

        Args:
            file_path: Path to the Excel file

        Returns:
            Dict containing month and tasks list
        """
        # Read Excel file
        df = pd.read_excel(file_path, engine='openpyxl')

        # Extract task list
        tasks = []
        current_person = None
        month = None

        for _, row in df.iterrows():
            # Extract name from first column
            if pd.notna(row.iloc[0]):
                current_person = str(row.iloc[0]).strip()

            # Extract project and work details
            if pd.notna(row.iloc[2]) and pd.notna(row.iloc[3]):
                project = str(row.iloc[2]).strip()
                detail = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ""
                hours = float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0.0

                # Extract date
                date_str = str(row.iloc[6]).strip() if pd.notna(row.iloc[6]) else ""
                date = self._extract_date(date_str)

                if date and not month:
                    month = date[:7]

                task = {
                    'person': current_person,
                    'date': date,
                    'project': project,
                    'detail': detail,
                    'hours': hours
                }
                tasks.append(task)

        return {
            'month': month or datetime.now().strftime('%Y-%m'),
            'tasks': tasks
        }

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text string."""
        if not text:
            return None
        match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        return match.group(1) if match else None

    def get_tasks_by_person(self, data: Dict) -> Dict[str, List[Dict]]:
        """Group tasks by person."""
        result = {}
        for task in data.get('tasks', []):
            person = task.get('person', 'Unknown')
            if person not in result:
                result[person] = []
            result[person].append(task)
        return result

    def get_tasks_by_project(self, data: Dict) -> Dict[str, List[Dict]]:
        """Group tasks by project."""
        result = {}
        for task in data.get('tasks', []):
            project = task.get('project', 'Unknown')
            if project not in result:
                result[project] = []
            result[project].append(task)
        return result

    def get_total_hours_by_person(self, data: Dict) -> Dict[str, float]:
        """Calculate total hours per person."""
        result = {}
        for task in data.get('tasks', []):
            person = task.get('person', 'Unknown')
            result[person] = result.get(person, 0) + task.get('hours', 0)
        return result

    def get_total_hours_by_project(self, data: Dict) -> Dict[str, float]:
        """Calculate total hours per project."""
        result = {}
        for task in data.get('tasks', []):
            project = task.get('project', 'Unknown')
            result[project] = result.get(project, 0) + task.get('hours', 0)
        return result
