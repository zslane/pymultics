
from multics.globals import *

def accept_messages():
    call.sys_.accept_messages_(True)
    call.ioa_("Accepting messages")
#-- end def accept_messages

am = accept_messages
