
from multics.globals import *

def sm():
    declare (cu_       = entry . returns (varying),
             arg_count = parm,
             code      = parm)
             
    call.cu_.arg_count(arg_count)
    if arg_count.val < 2:
        call.ioa_("Usage: sm [recipient] [message]")
    else:
        recipient, message = cu_.arg_string(1)
        call.sys_.send_message_(recipient[0], message, code)
        if code.val != 0:
            call.ioa_("Could not send message to {0}", recipient[0])
            