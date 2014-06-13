
from multics.globals import *

MAIN = "shutdown"
    
def shutdown():
    declare (shutdown_started_ = entry . returns (bit(1)))
    
    declare (person   = parm,
             project  = parm,
             acct     = parm,
             before   = parm,
             result   = parm,
             arg_list = parm)
    
    call.user_info_.whoami(person, project, acct)
    if project.id != "SysAdmin":
        call.ioa_("You are not authorized to use the {0} command", MAIN)
        return
    # end if
    
    DEFAULT_SHUTDOWN_TIME = 10 * 60 # 10 minutes
    
    how_long = DEFAULT_SHUTDOWN_TIME
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
                if shutdown_started_():
                    call.sys_.cancel_shutdown()
                else:
                    call.ioa_("No shutdown in progress")
                # end if
                return 0
            else:
                call.ioa_("Usage: shutdown {{-in [time] [units]}} {{-m [message]}} {{-cancel|-c}}")
                return 0
            # end if
        # end while
    # end if
    
    call.sys_.start_shutdown(how_long, message)
