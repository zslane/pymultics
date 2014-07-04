
from multics.globals import *

def accept_messages():
    homedir = parm()
    person  = parm()
    project = parm()
    acct    = parm()
    segment = parm()
    code    = parm()
    
    call.user_info_.homedir(homedir)
    call.user_info_.whoami(person, project, acct)
    
    call.hcs_.make_seg(homedir.val, person.id + ".mbx", "", 0, segment(dict), code)
    if code.val == 0:
        print "Created user mailbox file %s>%s.mbx" % (homedir.val, person.id)
    # end if
    
    call.sys_.accept_messages_(True)
    call.ioa_("Accepting messages")
#-- end def accept_messages

am = accept_messages
