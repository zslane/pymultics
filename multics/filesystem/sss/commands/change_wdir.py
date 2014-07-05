
from multics.globals import *

def change_wdir():
    arg_list = parm()
    homedir  = parm()
    code     = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        call.user_info_.homedir(homedir)
        new_dir = homedir.val
    else:
        new_dir = arg_list.args.pop()
    # end if
    
    call.sys_.change_current_directory(new_dir, code)
    if code.val != 0:
        call.ioa_("No such directory")
        
#-- end def change_wdir

cwd = change_wdir
