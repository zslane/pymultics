
from multics.globals import *

class set_acl(SystemSubroutine):
    def __init__(self, supervisor):
        super(set_acl, self).__init__(self.__class__.__name__, supervisor)

    def procedure(self, acl_entry, acl, whom):
        pass
        