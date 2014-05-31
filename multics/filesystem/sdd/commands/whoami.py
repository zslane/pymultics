
from multics.globals import *

def whoami():
    person_id, project_id = call.user_info_.whoami()
    call.ioa_("{0}.{1}", person_id, project_id)
    