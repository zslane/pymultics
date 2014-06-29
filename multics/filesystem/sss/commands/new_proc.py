
from multics.globals import *

def new_proc():
    arg_list = parm()
    process = get_calling_process_()
    process.stack.assert_create("new_proc_options", dict)
    process.stack.new_proc_options = {'authorization':""}
    call.sys_.set_exit_code(System.NEW_PROCESS)
    