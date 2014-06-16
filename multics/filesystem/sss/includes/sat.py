
from multics.globals import *

class SystemAdministratorTable(object):

    def __init__(self):
        self.projects = {}
        
    def add_project(self, project_id, pdt_path, alias):
        self.projects[project_id] = {
            'project_id': project_id,
            'pdt_path': pdt_path,
            'alias': alias,
            'admins': [],
        }
        
    def get_admins(self, project_id):
        return self.projects[project_id]['admins']
        
    def add_admin(self, project_id, person_id):
        try:
            self.projects[project_id]['admins'].append(person_id)
        except:
            pass
        
    def remove_admin(self, project_id, person_id):
        try:
            self.projects[project_id]['admins'].remove(person_id)
        except:
            pass
            