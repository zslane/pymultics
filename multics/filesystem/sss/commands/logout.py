
from multics.globals import *

@system_privileged
def logout():
    arg_list = parm()
    
    process = get_calling_process_()
    process.stack.assert_create("logout_options", dict)
    
    call.cu_.arg_list(arg_list)
    while len(arg_list.args) > 0:
        arg = arg_list.args.pop(0)
        if arg == "-hold" or arg == "-ho":
            process.stack.logout_options['hold'] = True
        elif arg == "-brief" or arg == "-bf":
            process.stack.logout_options['brief'] = True
        else:
            call.ioa_("Usage: logout {{-hold}} {{-brief|-bf}}")
            return
        # end if
    # end if
    
    call.sys_.set_exit_code(System.LOGOUT)
    