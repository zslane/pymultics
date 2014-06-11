
from multics.globals import *

def ls():
    declare (arg_list    = parm,
             get_wdir_   = entry . returns (char(168)),
             dir_to_list = parm,
             branch      = parm,
             segment     = parm,
             code        = parm)
             
    current_dir = get_wdir_()
    dir_to_list.name = current_dir
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) > 0:
        dir_ref = arg_list.args.pop()
        call.sys_.get_rel_directory(dir_ref, current_dir, dir_to_list, code)
        if code.val != 0:
            call.ioa_("No such directory")
            return
        # end if
    # end if
    call.hcs_.get_directory_contents(dir_to_list.name, branch, segment, code)
    if code.val == 0:
        if len(branch.list) + len(segment.list) == 0:
            call.ioa_("Directory empty")
        else:
            call.ioa_("{0} segments in directory: {1}", len(branch.list) + len(segment.list), dir_to_list.name)
            for branch_name in branch.list:
                call.ioa_("d {0}", branch_name)
            for segment_name in segment.list:
                call.ioa_("  {0}", segment_name)
    