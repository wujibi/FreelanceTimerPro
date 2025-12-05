def on_timer_client_select(self, event):
    """When client is selected in timer, populate projects for that client"""
    client_name = self.timer_client_combo.get()
    if client_name:
        # Get client ID
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_name:
                client_id = client[0]
                break

        if client_id:
            # Get projects for this client
            self.populate_projects_for_client(client_id, self.timer_project_combo)

        # Clear project and task selections when client changes
        self.timer_project_combo.set("")
        self.task_combo.set("")
        self.task_combo['values'] = []


def on_timer_project_select(self, event):
    """When project is selected in timer, populate tasks for that project"""
    project_name = self.timer_project_combo.get()
    if project_name:
        # Get project ID
        projects = self.project_model.get_all()
        project_id = None
        for project in projects:
            if project[2] == project_name:  # project name is at index 2
                project_id = project[0]
                break

        if project_id:
            # Get tasks for this project
            self.populate_tasks_for_project(project_id, self.task_combo)

        # Clear task selection when project changes
        self.task_combo.set("")


def on_manual_client_select(self, event):
    """When client is selected in manual entry, populate projects for that client"""
    client_name = self.manual_client_combo.get()
    if client_name:
        # Get client ID
        clients = self.client_model.get_all()
        client_id = None
        for client in clients:
            if client[1] == client_name:
                client_id = client[0]
                break

        if client_id:
            # Get projects for this client
            self.populate_projects_for_client(client_id, self.manual_project_combo)

        # Clear project and task selections when client changes
        self.manual_project_combo.set("")
        self.manual_task_combo.set("")
        self.manual_task_combo['values'] = []


def on_manual_project_select(self, event):
    """When project is selected in manual entry, populate tasks for that project"""
    project_name = self.manual_project_combo.get()
    if project_name:
        # Get project ID
        projects = self.project_model.get_all()
        project_id = None
        for project in projects:
            if project[2] == project_name:  # project name is at index 2
                project_id = project[0]
                break

        if project_id:
            # Get tasks for this project
            self.populate_tasks_for_project(project_id, self.manual_task_combo)

        # Clear task selection when project changes
        self.manual_task_combo.set("")


def populate_projects_for_client(self, client_id, project_combo):
    """Populate project combo with projects for the specified client"""
    projects = self.project_model.get_by_client(client_id)
    project_names = [project[2] for project in projects]  # project name is at index 2
    project_combo['values'] = project_names


def populate_tasks_for_project(self, project_id, task_combo):
    """Populate task combo with tasks for the specified project"""
    tasks = self.task_model.get_by_project(project_id)
    task_names = [task[2] for task in tasks]  # task name is at index 2
    task_combo['values'] = task_names
