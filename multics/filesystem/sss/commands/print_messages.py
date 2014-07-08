
from multics.globals import *

def print_messages():
    mbx_segment = parm()
    code        = parm()
    
    print_all = True
    
    process = get_calling_process_()
    user_id = process.uid()
    homedir = process.homedir()
    
    held_count = 0
    
    call.sys_.lock_user_mbx_(user_id, homedir, mbx_segment, code)
    if mbx_segment.ptr != null():
        with mbx_segment.ptr:
            for message in mbx_segment.ptr.messages[:]:
                if message['type'] == "interactive_message":
                    holding = mbx_segment.ptr.has_state("hold_messages")
                    #== Print unread interactive messages
                    if message['status'] == "unread" or print_all:
                        if message['status'] == "hold" or holding:
                            held_count += 1
                            count_str = "{0}. ".format(held_count)
                        else:
                            count_str = ""
                        # end if
                        call.ioa_("{0}From {1} {2}: {3}", count_str, message['from'], message['time'].ctime(), message['text'])
                        if message['status'] == "unread": message['status'] = "read"
                    # end if
                    if holding:
                        message['status'] = "hold"
                    # end if
                    #== Delete messages marked as read; messages marked as unread or hold will remain
                    if message['status'] == "read":
                        mbx_segment.ptr.messages.remove(message)
                    # end if
                # end if
            # end for
        # end with
        call.sys_.unlock_user_mbx_(mbx_segment.ptr, code)

#-- end def print_messages

pm = print_messages
