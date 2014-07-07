
from multics.globals import *

def delete_messages():
    mbx_segment = parm()
    code        = parm()
    
    process = get_calling_process_()
    user_id = process.uid()
    homedir = process.homedir()
    
    call.sys_.lock_user_mbx_(user_id, homedir, mbx_segment, code)
    if mbx_segment.ptr != null():
        with mbx_segment.ptr:
            for message in mbx_segment.ptr.messages[:]:
                if message['type'] == "interactive_message":
                    mbx_segment.ptr.messages.remove(message)
                # end if
            # end for
        # end with
        call.sys_.unlock_user_mbx_(mbx_segment.ptr, code)

#-- end def delete_messages

dlm = delete_messages
