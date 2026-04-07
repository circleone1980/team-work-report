"""
Markdown Generator for team work reports.
"""
from typing import Dict, List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template
import os


class MarkdownGenerator:
    """Generate Markdown reports from parsed Excel data."""

    def __init__(self, template_dir: str = None):
        """
        Initialize the generator.

        Args:
            template_dir: Directory containing Jinja2 templates.
                         Defaults to 'templates' in the current directory.
        """
        if template_dir is None:
            # Default to templates directory relative to this file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(script_dir))
            template_dir = os.path.join(base_dir, 'templates')

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(
        self,
        data: Dict,
        template_name: str = 'team_report.md.j2'
    ) -> str:
        """
        Generate Markdown report from parsed data.

        Args:
            data: Parsed data from ExcelParser
            template_name: Name of the Jinja2 template file

        Returns:
            Generated Markdown content as string
        """
        # Prepare statistics
        stats = self._calculate_stats(data)

        # Prepare project summaries
        projects = self._prepare_project_summaries(data)

        # Prepare person details
        people = self._prepare_person_details(data)

        # Load template
        template = self.env.get_template(template_name)

        # Render
        return template.render(
            month=data.get('month', datetime.now().strftime('%Y-%m')),
            stats=stats,
            projects=projects,
            people=people,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def _calculate_stats(self, data: Dict) -> Dict:
        """Calculate overall statistics."""
        tasks = data.get('tasks', [])

        # Get unique people and projects
        people_set = set()
        projects_set = set()
        total_hours = 0

        for task in tasks:
            people_set.add(task.get('person', 'Unknown'))
            projects_set.add(task.get('project', 'Unknown'))
            total_hours += task.get('hours', 0)

        return {
            'total_people': len(people_set),
            'total_hours': round(total_hours, 1),
            'total_projects': len(projects_set),
            'total_tasks': len(tasks)
        }

    def _prepare_project_summaries(self, data: Dict) -> List[Dict]:
        """Prepare project summaries with people and hours."""
        tasks = data.get('tasks', [])

        # Group by project
        project_data = {}
        for task in tasks:
            project = task.get('project', 'Unknown')
            if project not in project_data:
                project_data[project] = {
                    'name': project,
                    'total_hours': 0,
                    'people': {},  # name -> hours
                    'task_count': 0
                }

            project_data[project]['total_hours'] += task.get('hours', 0)
            project_data[project]['task_count'] += 1

            person = task.get('person', 'Unknown')
            if person not in project_data[project]['people']:
                project_data[project]['people'][person] = 0
            project_data[project]['people'][person] += task.get('hours', 0)

        # Convert to list format
        result = []
        for proj in project_data.values():
            result.append({
                'name': proj['name'],
                'total_hours': round(proj['total_hours'], 1),
                'people_count': len(proj['people']),
                'task_count': proj['task_count'],
                'people': [
                    {'name': name, 'hours': round(hours, 1)}
                    for name, hours in sorted(
                        proj['people'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                ]
            })

        return sorted(result, key=lambda x: x['total_hours'], reverse=True)

    def _prepare_person_details(self, data: Dict) -> List[Dict]:
        """Prepare detailed information for each person."""
        tasks = data.get('tasks', [])

        # Group by person
        person_data = {}
        for task in tasks:
            person = task.get('person', 'Unknown')
            if person not in person_data:
                person_data[person] = {
                    'name': person,
                    'total_hours': 0,
                    'projects': {},  # project -> hours
                    'tasks': []
                }

            person_data[person]['total_hours'] += task.get('hours', 0)

            project = task.get('project', 'Unknown')
            if project not in person_data[person]['projects']:
                person_data[person]['projects'][project] = 0
            person_data[person]['projects'][project] += task.get('hours', 0)

            person_data[person]['tasks'].append({
                'date': task.get('date', ''),
                'project': project,
                'detail': task.get('detail', ''),
                'hours': task.get('hours', 0)
            })

        # Convert to list format
        result = []
        for person in person_data.values():
            # Sort tasks by date
            sorted_tasks = sorted(
                person['tasks'],
                key=lambda x: x.get('date', '9999-99-99')
            )

            result.append({
                'name': person['name'],
                'total_hours': round(person['total_hours'], 1),
                'project_count': len(person['projects']),
                'task_count': len(person['tasks']),
                'projects': [
                    {'name': proj, 'hours': round(hours, 1)}
                    for proj, hours in sorted(
                        person['projects'].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                ],
                'tasks': sorted_tasks
            })

        return sorted(result, key=lambda x: x['total_hours'], reverse=True)

    def save(self, content: str, output_path: str) -> None:
        """
        Save generated Markdown to file.

        Args:
            content: Markdown content to save
            output_path: Path to output file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def generate_and_save(
        self,
        data: Dict,
        output_path: str,
        template_name: str = 'team_report.md.j2'
    ) -> str:
        """
        Generate and save Markdown report.

        Args:
            data: Parsed data from ExcelParser
            output_path: Path to output file
            template_name: Name of the Jinja2 template file

        Returns:
            Generated Markdown content
        """
        content = self.generate(data, template_name)
        self.save(content, output_path)
        return content
