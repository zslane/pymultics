
from multics.globals import *

def new_proc():
    #== Store new_proc options in the root stack frame so they can
    #== be found even after unwinding from a nested command level.
    process = get_calling_process_()
    process.root_stack.assert_create("new_proc_options", dict)
    process.root_stack.new_proc_options = {'authorization':""}
    call.sys_.set_exit_code(System.NEW_PROCESS)
    