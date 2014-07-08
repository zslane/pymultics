
from multics.globals import *

def defer_messages():
    mbx_segment = parm()
    code        = parm()
    
    process = get_calling_process_()
    user_id = process.uid()
    homedir = process.homedir()
    
    call.sys_.lock_user_mbx_(user_id, homedir, mbx_segment, code)
    if mbx_segment.ptr != null():
        with mbx_segment.ptr:
            mbx_segment.ptr.remove_state("accept_messages")
        # end with
        call.sys_.unlock_user_mbx_(mbx_segment.ptr, code)
    # end if
    call.ioa_("Deferring messages")
#-- end def defer_messages

dm = defer_messages
