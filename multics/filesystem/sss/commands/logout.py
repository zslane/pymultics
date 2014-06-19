
from multics.globals import *

@system_privileged
def logout():
    declare (arg_list = parm)
    
    call.sys_.set_exit_code(System.LOGOUT)
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 1:
        arg = arg_list.args.pop(0)
        if arg == "-disconnect" or arg == "-d":
            system.hardware.io.disconnect_terminal()
            