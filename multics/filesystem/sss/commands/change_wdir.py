
from multics.globals import *

def change_wdir():
    arg_list = parm()
    code     = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 1:
        new_dir = arg_list.args.pop()
        call.sys_.change_current_directory(new_dir, code)
        if code.val != 0:
            call.ioa_("No such directory")
    else:
        call.ioa_("Usage: cwd [directory ref]")
        
#-- end def change_wdir

cwd = change_wdir