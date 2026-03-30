"""Task resolution helpers used by UI callbacks."""

GLOBAL_TASK_PREFIX = "[GLOBAL] "
INVALID_TASK_FORMAT_ERROR = "Invalid task format"
TASK_NOT_FOUND_ERROR_PREFIX = "Could not find task: "


def format_global_task_display(task_name):
    """Return display text for a global task."""
    return f"{GLOBAL_TASK_PREFIX}{task_name}"


def format_project_task_display(client_name, project_name, task_name):
    """Return display text for a project-scoped task."""
    return f"{client_name} - {project_name} - {task_name}"


def format_task_display(task_row, client_name=None, project_name=None):
    """Return display text for a task tuple/row from the data layer."""
    if task_row[1] is None:
        return format_global_task_display(task_row[2])

    if client_name is None:
        client_name = task_row[9] if len(task_row) > 9 else "Unknown"
    if project_name is None:
        project_name = task_row[8] if len(task_row) > 8 else "Unknown"
    return format_project_task_display(client_name, project_name, task_row[2])


def resolve_task_id_for_timer(task_text, client_name, project_name, all_tasks, global_tasks):
    """Resolve selected timer task text into a task id.

    Returns:
        tuple[int | None, str | None, str | None]: (task_id, task_name, error_message)
    """
    if task_text.startswith(GLOBAL_TASK_PREFIX):
        task_name = task_text.replace(GLOBAL_TASK_PREFIX, "")
        for task in global_tasks:
            if task[2] == task_name:
                return task[0], task_name, None
        return None, task_name, f"{TASK_NOT_FOUND_ERROR_PREFIX}{task_name}"

    parts = task_text.split(" - ")
    if len(parts) < 3:
        return None, None, INVALID_TASK_FORMAT_ERROR

    task_name = " - ".join(parts[2:])
    for task in all_tasks:
        if task[9] == client_name and task[8] == project_name and task[2] == task_name:
            return task[0], task_name, None

    return None, task_name, f"{TASK_NOT_FOUND_ERROR_PREFIX}{task_name}"

