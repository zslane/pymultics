
from multics.globals import *

def ls():
    declare (current_dir = parm,
             branch      = parm,
             segment     = parm,
             code        = parm)
             
    call.sys_.get_current_directory(current_dir)
    call.hcs_.get_directory_contents(current_dir.name, branch, segment, code)
    if code.va == 0:
        if len(branch.list) + len(segment.list) == 0:
            call.ioa_("Directory empty")
        else:
            call.ioa_("{0} segments in directory:", len(segment.list))
            for branch_name in branch.list:
                call.ioa_("  {0}", branch_name)
            for segment_name in segment.list:
                call.ioa_("  {0}", segment_name)
    