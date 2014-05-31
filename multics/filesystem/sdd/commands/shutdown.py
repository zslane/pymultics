import datetime

from multics.globals import *

def shutdown():
    message = ""
    arg_list = call.cu_.arg_list()
    if not arg_list:
        shutdown_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    else:
        acceptible_units = ["minutes", "seconds"]
        i = 0
        while arg_list:
            arg = arg_list.pop(0)
            i += 1
            if arg == "-in":
                if len(arg_list) >= 2:
                    amount = arg_list.pop(0)
                    units = arg_list.pop(0)
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
                if arg_list:
                    _, message = call.cu_.arg_string(i)
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
                    
    return System.SHUTDOWN
    