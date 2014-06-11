
from multics.globals import *

class get_group_id_(SystemExecutable):
    def __init__(self, supervisor):
        super(get_group_id_, self).__init__(self.__class__.__name__, supervisor)
        
    def procedure(self):
        process = get_calling_process_()
        pit = process.pit()
        person_id = pit.login_name
        project_id = pit.project
        tag = pit.instance_tag
        return "%s.%s.%s" % (person_id, project_id, tag)
        
    def tag_star(self):
        process = get_calling_process_()
        pit = process.pit()
        person_id = pit.login_name
        project_id = pit.project
        tag = "*"
        return "%s.%s.%s" % (person_id, project_id, tag)
