
from multics.globals import *

# include.pdt

@system_privileged
def up_pmf():

    declare (get_wdir_ = entry . returns (char(168)))
    arg_list        = parm()
    person          = parm()
    project         = parm()
    acct            = parm()
    sys_admin_table = parm()
    code            = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 1:
        call.ioa_("Usage: up_pmf [project_id]")
        return
    # end if
    
    project_id = arg_list.args.pop()
    pdt_file = project_id + ".pdt"
    
    call.hcs_.initiate(supervisor.fs.system_control_dir, "system_administrator_table", "", 0, 0, sys_admin_table, code)
    call.user_info_.whoami(person, project, acct)
    if not ((sys_admin_table.ptr and
             project.id in sys_admin_table.ptr.projects and
             person.id in sys_admin_table.ptr.projects[project_id]['admins']) or
            (project.id == "SysAdmin")):
        call.ioa_("You are not authorized to upload {0}", pdt_file)
        return
    # end if
    
    src_dir = get_wdir_()
    
    if not supervisor.fs.file_exists(supervisor.fs.path2path(src_dir, pdt_file)):
        call.ioa_("File not found {0}", pdt_file)
        return
    # end if
    
    if sys_admin_table.ptr == null():
        call.ioa_("Warning: no system_administrator_table found; will not be updated by the answering service")
    # end if
    
    msg = ProcessMessage("upload_pmf_request", **{'src_dir':src_dir, 'src_file':pdt_file})
    call.sys_.add_process_msg("Initializer.SysDaemon", msg, code)
    if code.val != 0:
        call.ioa_("Upload failed. {0}", code.val)
    else:
        call.ioa_("{0} uploaded", pdt_file)
