import os

from multics.globals import *

@system_privileged
def add_name():
    arg_list  = parm()
    full_path = parm()
    code      = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) < 2:
        call.ioa_("Usage: add_name|an [path] [names]")
        return
    # end if
    
    path = arg_list.args.pop(0)
    names = arg_list.args
    
    call.sys_.get_abs_path(path, full_path)
    if supervisor.fs.file_exists(full_path.val):
        for name in names:
            supervisor.fs.add_name(full_path.val, name)
    else:
        call.ioa_("add_name: Segment not found. ^a", path)

an = add_name
