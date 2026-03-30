"""Project lookup helpers used by UI callbacks."""


def resolve_project_id_by_names(projects, client_name, project_name):
    """Resolve a project id from client/project names using project rows."""
    for project in projects:
        proj_client_name = project[9] if len(project) > 9 else None
        if proj_client_name == client_name and project[2] == project_name:
            return project[0]
    return None

