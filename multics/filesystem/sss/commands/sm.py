import datetime

from multics.globals import *

def sm():
    declare (cu_       = entry . returns (varying),
             arg_count = parm,
             code      = parm)
             
    def send_msg(recipient, message, code):
        declare (mbx_segment = parm,
                 person      = parm,
                 project     = parm,
                 acct        = parm)
        call.sys_.lock_process_mbx_(recipient, mbx_segment, code)
        if code.val != 0:
            return
        process_mbx = mbx_segment.ptr
        print process_mbx.filepath
        call.user_info_.whoami(person, project, acct)
        user_id = person.id + "." + project.id
        with process_mbx:
            process_mbx.messages.append({'type':"user_message", 'from':user_id, 'time':datetime.datetime.now(), 'text':message})
        # end with
        call.sys_.unlock_process_mbx_(process_mbx, code)
    
    call.cu_.arg_count(arg_count)
    if arg_count.val < 2:
        call.ioa_("Usage: sm [recipient] [message]")
    else:
        recipient, message = cu_.arg_string(1)
        send_msg(recipient[0], message, code)
        if code.val == error_table_.no_such_user:
            call.ioa_("send_message: A user named {0} is not logged in.", recipient[0])
        elif code.val == error_table_.lock_wait_time_exceeded:
            call.ioa_("send_message: Attempt to reach {0} timed out.", recipient[0])
        elif code.val != 0:
            call.ioa_("Could not send message to {0}", recipient[0])
            call.ioa_("{0}", code.val)
            