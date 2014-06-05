
from multics.globals import *

class ProjectDefinitionTable(object):

    def __init__(self, project_id, alias="", admins=[]):
        self.project_id = project_id
        self.alias = alias
        self.admins = admins
        self.users = {}
        
    def recognizes(self, person_id):
        return person_id in self.users
        
    def get_user_quota(self, person_id):
        try:
            return self.users[person_id]
        except:
            raise MulticsCondition(error_table_.no_such_user)
            
    def add_user(self, person_id, cp_path=""):
        self.users[person_id] = ProjectUserConfig(person_id, cp_path)
        
    def remove_user(self, person_id):
        try:
            del self.users[person_id]
        except:
            raise MulticsCondition(error_table_.no_such_user)        
        
    def __repr__(self):
        project_id = self.project_id
        if self.alias:
            project_id += " (%s)" % (self.alias)
        admins = str(self.admins)
        users = str(self.users.keys())
        return "<%s.%s project_id: %s, admins = %s, users = %s>" % (__name__, self.__class__.__name__, project_id, admins, users)
        
class ProjectUserConfig(object):

    def __init__(self, person_id, cp_path):
        self.person_id = person_id
        self.cp_path = cp_path
        