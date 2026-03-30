"""Helpers for building task display lists."""

from core.task_resolution import format_task_display


def build_task_displays_for_project(project_tasks, global_tasks, client_name, project_name):
    """Build display values for a selected client/project context."""
    all_tasks = list(global_tasks) + list(project_tasks)
    return [format_task_display(task, client_name, project_name) for task in all_tasks]

