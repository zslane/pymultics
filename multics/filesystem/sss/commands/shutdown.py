import datetime

from multics.globals import *

def shutdown():
    declare (before   = parm,
             result   = parm,
             messenger = parm,
             mbx_segment = parm,
             code        = parm,
             arg_list = parm)
    
    message = "System is shutting down. "
    shutdown_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    
    call.cu_.arg_list(arg_list)
    if arg_list.args:
        acceptible_units = ["minutes", "seconds"]
        i = 0
        while arg_list.args:
            arg = arg_list.args.pop(0)
            i += 1
            if arg == "-in":
                if len(arg_list.args) >= 2:
                    amount = arg_list.args.pop(0)
                    units = arg_list.args.pop(0)
                    i += 2
                    if units not in acceptible_units:
                        call.ioa_("shutdown time units must be {0}", (" or ".join(acceptible_units)))
                        return 0
                    # end if
                    delta = {units:int(amount)}
                    shutdown_time = datetime.datetime.now() + datetime.timedelta(**delta)
                else:
                    call.ioa_("shutdown -in argument takes two arguments")
                    return 0
                # end if
            elif arg == "-m":
                if arg_list.args:
                    call.cu_.arg_string(before, result, i)
                    message += result.val
                    break
                else:
                    call.ioa_("shutdown -m argument requires an argument")
                    return 0
                # end if
            else:
                call.ioa_("Usage: shutdown {{-in [time] [units]}} {{-m [message]}}")
                return 0
            # end if
        # end while
    # end if
    
    print shutdown_time.ctime(), message
    msg = ProcessMbxMessage("shutdown_announcement", **{'from':"Multics.Supervisor", 'to':"*.*", 'text':message})
        
    try:
        call.sys_.lock_process_mbx_("Messenger.SysDaemon", mbx_segment, code)
        if code.val != 0:
            return
        # end if
        
        message_mbx = mbx_segment.ptr
        with message_mbx:
            # message_mbx.messages.append({'type':"shutdown_announcement", 'from':"Multics.Supervisor", 'to': "*.*", 'time':datetime.datetime.now(), 'text':message})
            message_mbx.messages.append(msg)
        # end with
        
    finally:
        call.sys_.unlock_process_mbx_(mbx_segment.ptr, code)
    # end try
    
    raise ShutdownCondition
    