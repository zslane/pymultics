
from multics.globals import *

_time_left = -1
_shutdown_message = ""

def shutdown():
    declare (before   = parm,
             result   = parm,
             messenger = parm,
             mbx_segment = parm,
             code        = parm,
             arg_list = parm)
    
    how_long = 5 * 60
    message = ""
    
    call.cu_.arg_list(arg_list)
    if arg_list.args:
        acceptible_units = ["min", "minute", "mins", "minutes", "sec", "second", "secs", "seconds"]
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
                        call.ioa_("shutdown time units must be one of:\n  {0}", (", ".join(acceptible_units)))
                        return 0
                    # end if
                    if units == "minutes":
                        how_long = int(amount) * 60
                    else:
                        how_long = int(amount)
                    # end if
                else:
                    call.ioa_("shutdown -in argument takes two arguments")
                    return 0
                # end if
            elif arg == "-m":
                if arg_list.args:
                    call.cu_.arg_string(before, result, i)
                    message = result.val
                    break
                else:
                    call.ioa_("shutdown -m argument requires an argument")
                    return 0
                # end if
            elif arg == "-cancel" or arg == "-c":
                _cancel_shutdown()
                return 0
            else:
                call.ioa_("Usage: shutdown {{-in [time] [units]}} {{-m [message]}} {{-cancel|-c}}")
                return 0
            # end if
        # end while
    # end if
    
    global _time_left
    _time_left = how_long
    global _shutdown_message
    _shutdown_message = message
    
    _shutdown_task()
    
def _send_shutdown_message(msgtype, how_long=-1):
    announcement = ""
    if msgtype == "shutdown_announcement":
        if how_long > 0:
            announcement = "System is shutting down in %d %s. %s" % ((how_long / 60) if how_long > 60 else how_long, "minutes" if how_long > 60 else "seconds", _shutdown_message)
        else:
            announcement = "System shutdown cancelled."
    
    msg = ProcessMbxMessage(msgtype, **{'from':"Multics.Supervisor", 'to':"*.*", 'text':announcement})
    
    try:
        call.sys_.lock_process_mbx_("Messenger.SysDaemon", mbx_segment, code)
        if code.val != 0:
            return
        # end if
        
        message_mbx = mbx_segment.ptr
        with message_mbx:
            message_mbx.messages.append(msg)
        # end with
        
    finally:
        call.sys_.unlock_process_mbx_(mbx_segment.ptr, code)
    # end try
    
    # call.sys_.signal_shutdown()
    
def _shutdown_task():
    call.timer_manager_.reset_alarm_call(_shutdown_task)
    
    global _time_left
    if _time_left > 0:
        _send_shutdown_message("shutdown_announcement", _time_left)
        if _time_left > 600: # 10 mins
            next_time = 600
            _time_left -= 600
        elif _time_left > 60: # 1 min
            next_time = 60
            _time_left -= 60
        elif _time_left > 15:
            next_time = 10
            _time_left -= 10
        else:
            next_time = _time_left
            _time_left = 0
        # end if
        
        call.timer_manager_.alarm_call(next_time, _shutdown_task)
        
    elif _time_left == 0:
        declare (flags = bit(2) . init("0b11"))
        _send_shutdown_message("shutdown")
        
def _cancel_shutdown():
    CANCELLED = -1
    
    # global _time_left
    # _time_left = CANCELLED
    # global _shutdown_message
    # _shutdown_message = ""
    
    call.timer_manager_.reset_alarm_call(_shutdown_task)
    _send_shutdown_message("shutdown_announcement", CANCELLED)
    