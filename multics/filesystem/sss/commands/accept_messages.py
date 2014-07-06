
from multics.globals import *

def accept_messages():
    arg_list = parm()
    homedir  = parm()
    person   = parm()
    project  = parm()
    acct     = parm()
    segment  = parm()
    messages = parm()
    flag     = parm()
    code     = parm()
    
    print_messages = False
    hold_messages = False
    unhold_messages = False
    
    call.cu_.arg_list(arg_list)
    for arg in arg_list.args:
        if arg == "-print" or arg == "-pr":
            print_messages = True
        elif arg == "-hold" or arg == "-hd":
            hold_messages = True
            unhold_messages = False
        elif arg == "-nohold":
            hold_messages = False
            unhold_messages = True
        else:
            call.ioa_("Usage: accept_messages|am {{-print|-pr}} {{-hold|-hd}} {{-nohold}}")
            return
        # end if
    # end for
            
    from mbx import Mailbox
    
    call.user_info_.homedir(homedir)
    call.user_info_.whoami(person, project, acct)
    
    call.hcs_.make_seg(homedir.val, person.id + ".mbx", "", 0, segment(Mailbox()), code)
    if code.val == 0:
        print "Created user mailbox file %s>%s.mbx" % (homedir.val, person.id)
    # end if
    
    call.sys_.accept_messages_(True)
    call.hcs_.initiate(homedir.val, person.id + ".mbx", "", 0, 0, segment, code)
    print segment.ptr.messages
    
    if hold_messages:
        call.sys_.hold_messages_(True)
    if unhold_messages:
        call.sys_.hold_messages_(False)
    
    call.sys_.messages_held_(flag)
    hold_messages = flag.val
    
    if print_messages:
        user_id = person.id + "." + project.id
        call.sys_.lock_user_mbx_(user_id, homedir.val, segment, code)
        mbx_segment = segment
        if mbx_segment.ptr != null():
            with mbx_segment.ptr:
                for message in mbx_segment.ptr.messages[:]:
                    if message['type'] == "interactive_message" and message['status'] == "unread":
                        call.ioa_("Message from {0} on {1}: {2}", message['from'], message['time'].ctime(), message['text'])
                        if hold_messages:
                            message['status'] = "hold"
                        else:
                            mbx_segment.ptr.messages.remove(message)
                        # end if
                    # end if
                # end for
            # end with
            call.sys_.unlock_user_mbx_(mbx_segment.ptr, code)
        # end if
    else:
        call.ioa_("Accepting messages")
        
#-- end def accept_messages

am = accept_messages
