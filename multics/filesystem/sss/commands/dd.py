
from multics.globals import *

def dd():
    declare (arg_list    = parm,
             current_dir = parm,
             dir_to_kill = parm,
             code        = parm)
             
    call.sys_.get_current_directory(current_dir)
    dir_to_list = current_dir
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        call.ioa_("Usage: dd [directory]")
        return
        
    dir_ref = arg_list.args.pop()
    call.sys_.get_rel_directory(dir_ref, current_dir.name, dir_to_kill, code)
    if code.val != 0:
        call.ioa_("No such directory")
        return
    # end if
    
    # call.ioa_("Delete directory {0}", dir_to_kill.name)
    call.hcs_.delete_branch_(dir_to_kill.name, code)
    if code.val != 0:
        call.ioa_("Could not delete directory")
        