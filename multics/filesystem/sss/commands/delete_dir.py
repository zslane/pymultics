
from multics.globals import *

include.query_info

def delete_dir():
    declare (get_wdir_ = entry . returns (char(168)))
    arg_list    = parm()
    dir_to_kill = parm()
    answer      = parm()
    code        = parm()
    
    current_dir = get_wdir_()
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        call.ioa_("Usage: dd [directory]")
        return
        
    dir_ref = arg_list.args.pop()
    call.sys_.get_rel_directory(dir_ref, current_dir, dir_to_kill, code)
    if code.val != 0:
        call.ioa_("No such directory")
        return
    # end if
    
    query_info.version = query_info_version_5
    query_info.suppress_name_sw = False
    query_info.suppress_spacing = True
    query_info.yes_or_no_sw = True
    call.command_query_(query_info, answer, "delete_dir", "Do you want to delete the directory\n{0:12}{1}??  ", "", dir_to_kill.name)
    if answer.val.lower() in ["yes", "y"]:
        call.hcs_.delete_branch_(dir_to_kill.name, code)
        if code.val != 0:
            call.ioa_("Could not delete directory")
        
#-- end def delete_dir

dd = delete_dir
