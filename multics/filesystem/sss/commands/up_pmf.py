import os
import re
import shutil
from pprint import pprint

from multics.globals import *

include.pdt

@system_privileged
def up_pmf():

    declare (arg_list    = parm,
             person      = parm,
             project     = parm,
             acct        = parm,
             pdt         = parm,
             code        = parm,
             get_wdir_   = entry . returns (char(168)))
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 1:
        call.ioa_("Usage: up_pmf [project_id]")
        return
        
    project_id = arg_list.args.pop()
    pdt_file = project_id + ".pdt"
    
    call.hcs_.initiate(system.hardware.filesystem.system_control_dir, pdt_file, pdt, code)
    call.user_info_.whoami(person, project, acct)
    if not ((pdt.ptr and person.id in pdt.ptr.admins) or (project.id == "SysAdmin")):
        call.ioa_("You are not authorized to upload {0}", pdt_file)
        return
    
    src_dir = get_wdir_()
    dst_dir = system.hardware.filesystem.system_control_dir
    src_pdt_path = system.hardware.filesystem.path2path(src_dir, pdt_file)
    dst_pdt_path = system.hardware.filesystem.path2path(dst_dir, pdt_file)
    
    if not os.path.exists(src_pdt_path):
        call.ioa_("File not found {0}", pdt_file)
        return
        
    shutil.move(src_pdt_path, dst_pdt_path)
    
    call.ioa_("{0} uploaded", pdt_file)
