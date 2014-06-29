
from multics.globals import *

class set_acl(SystemSubroutine):
    def __init__(self, system_services):
        super(set_acl, self).__init__(self.__class__.__name__, system_services)

    def procedure(self, acl_entry, acl, whom):
        pass
        