
from multics.globals import *

def ls():
    branch_list, segment_list, code = call.hcs_.get_directory_contents(call.sys_.get_current_directory())
    if code == 0:
        if len(branch_list) + len(segment_list) == 0:
            call.ioa_("Directory empty")
        else:
            call.ioa_("{0} segments in directory:".format(len(segment_list)))
            for branch in branch_list:
                call.ioa_("  {0}".format(branch))
            for segment in segment_list:
                call.ioa_("  {0}".format(segment))
    