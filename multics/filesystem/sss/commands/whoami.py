
from multics.globals import *

def whoami():
    declare (person  = parm,
             project = parm)
             
    call.user_info_.whoami(person, project)
    call.ioa_("{0}.{1}", person.id, project.id)
    