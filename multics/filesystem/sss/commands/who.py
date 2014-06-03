
from multics.globals import *

def who():
    declare (users = parm)
    
    call.sys_.get_users(users)
    call.ioa_("{0} user{1} logged in", len(users.list), "s" if len(users.list) > 1 else "")
    line = ""
    for i, user_id in enumerate(users.list):
        line += "{0:<25}".format(user_id)
        if (i + 1) % 3 == 0:
            call.ioa_("  {0}", line)
            line = ""
    if line:
        call.ioa_("  {0}", line)
    