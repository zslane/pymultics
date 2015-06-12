
from multics.globals import *

@system_privileged
def logout():
    arg_list = parm()
    
    #== Store logout options in the root stack frame so they can
    #== be found even after unwinding from a nested command level.
    process = get_calling_process_()
    process.root_stack.assert_create("logout_options", dict)
    
    call.cu_.arg_list(arg_list)
    while len(arg_list.args) > 0:
        arg = arg_list.args.pop(0)
        if arg == "-hold" or arg == "-ho":
            process.root_stack.logout_options['hold'] = True
        elif arg == "-brief" or arg == "-bf":
            process.root_stack.logout_options['brief'] = True
        else:
            call.ioa_("Usage: logout {{-hold}} {{-brief|-bf}}")
            return
        # end if
    # end if
    
    call.sys_.set_exit_code(System.LOGOUT)
    