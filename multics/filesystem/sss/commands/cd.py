
from multics.globals import *

def cd():
    declare (arg_list    = parm,
             get_wdir_   = entry . returns (char(168)),
             dir_to_make = parm,
             parent_dir  = parm,
             branch      = parm,
             code        = parm)
             
    current_dir = get_wdir_()
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        call.ioa_("Usage: cd [directory]")
        return
        
    dir_ref = arg_list.args.pop()
    call.sys_.get_rel_directory(dir_ref, current_dir, dir_to_make, code)
    # call.ioa_("Make directory {0}", dir_to_make.name)
    call.sys_.split_path_(dir_to_make.name, parent_dir, branch)
    # print parent_dir.name, branch.name
    call.hcs_.create_branch_(parent_dir.name, branch.name, None, code)
    if code.val != 0:
        if code.val == error_table_.namedup:
            call.ioa_("Directory already exists")
        else:
            call.ioa_("Could not create directory {0}", branch.name)
        