
from multics.globals import *

class set_acl(Subroutine):
    def __init__(self):
        super(set_acl, self).__init__(self.__class__.__name__)

    def procedure(self, acl_entry, acl, whom):
        pass
        