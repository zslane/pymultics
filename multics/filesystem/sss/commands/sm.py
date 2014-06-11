import datetime

from multics.globals import *

def sm():
    declare (before    = parm,
             result    = parm,
             arg_count = parm,
             code      = parm)
             
    def send_msg(recipient, message, code):
        declare (mbx_segment = parm,
                 long_name   = parm,
                 person      = parm,
                 project     = parm,
                 acct        = parm)
        
        call.sys_.get_userid_long(recipient, long_name, code)
        if code.val != 0:
            return
        # end if
        recipient = long_name.val
        call.sys_.lock_process_mbx_(recipient, mbx_segment, code)
        if code.val != 0:
            return
        # end if
        process_mbx = mbx_segment.ptr
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
        call.cu_.arg_string(before, result, 1)
        recipient = before.list[0]
        message = result.val
        send_msg(recipient, message, code)
        if code.val == error_table_.no_such_user:
            call.ioa_("send_message: A user named {0} is not logged in.", recipient)
        elif code.val == error_table_.lock_wait_time_exceeded:
            call.ioa_("send_message: Attempt to reach {0} timed out.", recipient)
        elif code.val != 0:
            call.ioa_("Could not send message to {0}", recipient)
            call.ioa_("{0}", code.val)
            