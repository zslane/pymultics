
from multics.globals import *

def accept_messages():
    arg_list    = parm()
    homedir     = parm()
    person      = parm()
    project     = parm()
    acct        = parm()
    mbx_segment = parm()
    messages    = parm()
    code        = parm()
    
    brief = False
    short = False
    print_messages = False
    hold_messages = False
    unhold_messages = False
    
    call.cu_.arg_list(arg_list)
    for arg in arg_list.args:
        if arg == "-brief" or arg == "-bf":
            short = brief = True
        elif arg == "-short" or arg == "-sh":
            short = True
        elif arg == "-print" or arg == "-pr":
            print_messages = True
        elif arg == "-hold" or arg == "-hd":
            hold_messages = True
            unhold_messages = False
        elif arg == "-nohold":
            hold_messages = False
            unhold_messages = True
        else:
            call.ioa_("Usage: accept_messages|am {-print|-pr} {-hold|-hd} {-nohold} {-brief|-bf} {-short|-sh}")
            return
        # end if
    # end for
    
    from mbx import Mailbox
    
    call.user_info_.homedir(homedir)
    call.user_info_.whoami(person, project, acct)
    
    call.hcs_.make_seg(homedir.val, person.id + ".mbx", "", 0, mbx_segment(Mailbox()), code)
    if code.val == 0:
        if not brief:
            call.ioa_("Created mailbox ^a>^a.mbx", homedir.val, person.id)
        # end if
        print "Created mailbox %s>%s.mbx" % (homedir.val, person.id)
    # end if
    
    user_id = person.id + "." + project.id
    call.sys_.lock_user_mbx_(user_id, homedir.val, mbx_segment, code)
    if mbx_segment.ptr != null():
        with mbx_segment.ptr:
        
            # mbx_segment.ptr.set_state("accept_messages")
            # if hold_messages:
                # mbx_segment.ptr.set_state("hold_messages")
            # elif unhold_messages:
                # mbx_segment.ptr.remove_state("hold_messages")
            # # end if
            # hold_messages = mbx_segment.ptr.has_state("hold_messages")
            call.sys_.accept_messages_(True)
            if hold_messages:
                call.sys_.hold_messages_(True)
            elif unhold_messages:
                call.sys_.hold_messages_(False)
            # end if
            flag = parm()
            call.sys_.messages_held_(flag)
            hold_messages = flag.val
            
            if print_messages:
                prev_sender = ""
                for message in mbx_segment.ptr.messages[:]:
                    #== Only look at previously unread messages.
                    if (message['type'] == "interactive_message") and (message['status'] == "unread"):
                        if message['from'] == prev_sender and short:
                            call.ioa_("^a =: ^a", message['time'].ctime())
                        else:
                            call.ioa_("From ^a ^a: ^a", message['from'], message['time'].ctime(), message['text'])
                        # end if
                        prev_sender = message['from']
                        
                        if hold_messages:
                            message['status'] = "hold"
                        else:
                            mbx_segment.ptr.messages.remove(message)
                        # end if
                    # end if
                # end for
            # end if
        # end with
        
        call.sys_.unlock_user_mbx_(mbx_segment.ptr, code)
        if not brief:
            call.ioa_("Accepting messages")
        
#-- end def accept_messages

am = accept_messages
