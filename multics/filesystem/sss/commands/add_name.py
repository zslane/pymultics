import os

from multics.globals import *

@system_privileged
def add_name():
    declare (arg_list  = parm,
             full_path = parm,
             code      = parm)
             
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 2:
        call.ioa_("Usage: add_name [path] [name]")
        return
    # end if
    
    path = arg_list.args.pop(0)
    name = arg_list.args.pop(0)
    
    call.sys_.get_abs_path(path, full_path)
    if system.fs.file_exists(full_path.val):
        system.fs.add_name(full_path.val, name)
