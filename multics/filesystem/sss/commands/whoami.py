
from multics.globals import *

def whoami():
    person  = parm()
    project = parm()
    acct    = parm()
    
    call.user_info_.whoami(person, project, acct)
    call.ioa_("{0}.{1}", person.id, project.id)
    