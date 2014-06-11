
from multics.globals import *

def defer_messages():
    call.sys_.accept_messages_(False)
    call.ioa_("Deferring messages")
    