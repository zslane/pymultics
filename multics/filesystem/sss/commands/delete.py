
from multics.globals import *

include.query_info

def delete(*func_args):
    arg_list  = parm()
    directory = parm()
    full      = parm()
    segment   = parm()
    answer    = parm("")
    code      = parm()
    
    if func_args:
        arg_list.args = list(func_args)
    else:
        call.cu_.arg_list(arg_list)
    # end if
    if len(arg_list.args) == 0:
        call.ioa_("Usage: delete [file]")
        return
    # end if
    
    filename = arg_list.args.pop(0)
    
    #== Handle control arguments
    if arg_list.args:
        pass
    # end if
    
    call.sys_.get_abs_path(filename, full)
    call.sys_.split_path_(full.path, directory, segment)
    call.hcs_.delentry_name(directory.name, segment.name, code)
    if code.val != 0:
        call.ioa_("delete: Segment not found. ^a", full.path)
    # end if
#-- end def delete

dl = delete
