
import shutil

from multics.globals import *

@system_privileged
def bind():

    arg_list = parm()
    full_path = parm()
    dir_name = parm()
    entryname = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 1:
        call.ioa_("Usage: bind archive_name")
        return
    # end if
    
    archive_name = arg_list.args.pop(0)
    call.sys_.get_abs_path(archive_name, full_path)
    if (not supervisor.fs.file_exists(full_path.val)) and (not full_path.val.endswith(".archive")):
        full_path.val += ".archive"
    # end if
    if not supervisor.fs.file_exists(full_path.val):
        call.ioa_("archive segment ^a not found.", archive_name)
        return
    # end if
    
    call.sys_.split_path_(full_path.val, dir_name, entryname)
    if not supervisor.fs.is_archive(full_path.val):
        call.ioa_("bind only works on archive segments.")
        return
    # end if
    
    bound_archive_name, _, _ = archive_name.partition(".")
    src = supervisor.fs.native_path(full_path.val)
    dst = supervisor.fs.path2path(dir_name.val, bound_archive_name)
    if src != dst:
        shutil.copyfile(src, dst)
    else:
        call.ioa_("bound archive would overwrite ^a.", archive_name)
    # end if
    
#-- end def bind
