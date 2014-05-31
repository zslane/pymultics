
from multics.globals import *

def who():
    users = call.sys_.get_users()
    call.ioa_("{0} user{1} logged in", len(users), "s" if len(users) > 1 else "")
    line = ""
    for i, user_id in enumerate(users):
        line += "{0:<25}".format(user_id)
        if (i + 1) % 3 == 0:
            call.ioa_("  {0}", line)
            line = ""
    if line:
        call.ioa_("  {0}", line)
    