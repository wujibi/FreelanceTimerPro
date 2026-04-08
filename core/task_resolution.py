"""Task resolution helpers used by UI callbacks."""

GLOBAL_TASK_PREFIX = "[GLOBAL] "
INVALID_TASK_FORMAT_ERROR = "Invalid task format"
TASK_NOT_FOUND_ERROR_PREFIX = "Could not find task: "


def _normalize_task_label(value):
    """Normalize display labels for resilient matching."""
    return " ".join((value or "").split()).casefold()


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
        task_name = task_text.replace(GLOBAL_TASK_PREFIX, "").strip()
        normalized_task_name = _normalize_task_label(task_name)
        for task in global_tasks:
            if _normalize_task_label(task[2]) == normalized_task_name:
                return task[0], task_name, None
        return None, task_name, f"{TASK_NOT_FOUND_ERROR_PREFIX}{task_name}"

    parts = task_text.split(" - ")
    if len(parts) < 3:
        return None, None, INVALID_TASK_FORMAT_ERROR

    task_name = " - ".join(parts[2:]).strip()
    normalized_client_name = _normalize_task_label(client_name)
    normalized_project_name = _normalize_task_label(project_name)
    normalized_task_name = _normalize_task_label(task_name)
    for task in all_tasks:
        if (
            _normalize_task_label(task[9]) == normalized_client_name
            and _normalize_task_label(task[8]) == normalized_project_name
            and _normalize_task_label(task[2]) == normalized_task_name
        ):
            return task[0], task_name, None

    return None, task_name, f"{TASK_NOT_FOUND_ERROR_PREFIX}{task_name}"

