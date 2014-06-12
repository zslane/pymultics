import datetime

from multics.globals import *

def shutdown():
    declare (before   = parm,
             result   = parm,
             messenger = parm,
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
    call.sys_.get_daemon("Messenger.SysDaemon", messenger)
    message_mbx = messenger.ptr.mbx()
    with message_mbx:
        message_mbx.messages.append({'type':"shutdown_announcement", 'from':"Multics.Supervisor", 'to': "*.*", 'time':datetime.datetime.now(), 'text':message})
    # end with
    
    raise ShutdownCondition
    