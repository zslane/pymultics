
from multics.globals import *

# include.pdt

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
    # end if
    
    project_id = arg_list.args.pop()
    pdt_file = project_id + ".pdt"
    
    call.hcs_.initiate(system.fs.system_control_dir, pdt_file, pdt, code)
    call.user_info_.whoami(person, project, acct)
    if not ((pdt.ptr and person.id in pdt.ptr.admins) or (project.id == "SysAdmin")):
        call.ioa_("You are not authorized to upload {0}", pdt_file)
        return
    # end if
    
    src_dir = get_wdir_()
    
    if not system.fs.file_exists(system.fs.path2path(src_dir, pdt_file)):
        call.ioa_("File not found {0}", pdt_file)
        return
    # end if
    
    msg = ProcessMessage("upload_pmf_request", **{'src_dir':src_dir, 'src_file':pdt_file})
    call.sys_.add_process_msg("Initializer.SysDaemon", msg, code)
    if code.val != 0:
        call.ioa_("Upload failed. {0}", code.val)
    else:
        call.ioa_("{0} uploaded", pdt_file)
