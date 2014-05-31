
from multics.globals import *

def sm():
    if call.cu_.arg_count() < 2:
        call.ioa_("Usage: sm [recipient] [message]")
    else:
        recipient, message = call.cu_.arg_string(1)
        code = call.sys_.send_message_(recipient[0], message)
        if code != 0:
            call.ioa_("Could not send message to {0}", recipient[0])
            