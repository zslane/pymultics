import datetime
import re

from multics.globals import *

include.query_info

@system_privileged
def send_message():
    before    = parm()
    result    = parm()
    arg_count = parm()
    long_name = parm()
    # users     = parm()
    input     = parm("")
    code      = parm(0)
    
    process   = get_calling_process_()
    sender    = process.uid()
    
    def send_msg(sender, recipient, long_name, message, code):
        msg = ProcessMessage("interactive_message", **{'from':sender, 'to':long_name, 'text':message})
        call.sys_.add_process_msg("Messenger.SysDaemon", msg, code)
        if code.val == error_table_.lock_wait_time_exceeded:
            call.ioa_("send_message: Attempt to reach {0} timed out.", recipient)
        elif code.val != 0:
            call.ioa_("Could not send message to {0}", recipient)
            call.ioa_("{0}", code.val)
        
    #-- end def send_msg
    
    call.cu_.arg_count(arg_count)
    if arg_count.val == 0:
        call.ioa_("Usage: send_message|sm [recipient] [message]")
    else:
        call.cu_.arg_string(before, result, 1)
        recipient = before.list[0]
        message = result.val
        
        call.sys_.get_userid_long(recipient, long_name, code)
        if code.val == error_table_.no_such_user:
            call.ioa_("{0} is not a registered user.", recipient)
            return
        # end if
        
        matching = long_name.val.replace(".", r"\.").replace("*", r"(\w+)")
        for user_process in supervisor.get_interactive_processes():
            if re.match(matching, user_process.uid()):
                user_process.stack.assert_create("accepting_messages", bool)
                if not user_process.stack.accepting_messages:
                    call.ioa_("{0} is not accepting messages. Message sent to user's mailbox.", user_process.uid())
                # end if
            # end if
        # end for
        
        if message:
            send_msg(sender, recipient, long_name.val, message, code)
        else:
            call.ioa_("Input:")
            query_info.version = query_info_version_5
            query_info.suppress_spacing = True
            query_info.suppress_name_sw = True
            while code.val == 0 and input.val != ".":
                call.command_query_(query_info, input, "send_message")
                if input.val != ".":
                    send_msg(sender, recipient, long_name.val, input.val, code)
            
#-- end def send_message

sm = send_message
