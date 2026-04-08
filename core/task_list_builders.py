"""Helpers for building task display lists."""

from core.task_resolution import format_task_display


def build_task_displays_for_project(project_tasks, global_tasks, client_name, project_name):
    """Build display values for a selected client/project context."""
    all_tasks = list(global_tasks) + list(project_tasks)
    return [format_task_display(task, client_name, project_name) for task in all_tasks]


def build_task_display_id_map_for_project(project_tasks, global_tasks, client_name, project_name):
    """Build {display_text: task_id} for exact dropdown-to-id resolution."""
    all_tasks = list(global_tasks) + list(project_tasks)
    mapping = {}
    for task in all_tasks:
        mapping[format_task_display(task, client_name, project_name)] = task[0]
    return mapping

