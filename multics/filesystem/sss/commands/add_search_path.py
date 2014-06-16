
from multics.globals import *

from sl_info import *
include.sl_list

@system_privileged
def add_search_path():
    declare (sl_info_ptr = parm,
             arg_list    = parm,
             code        = parm)
             
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) < 2:
        call.ioa_("Usage: add_search_path [search_list_name] [path] {{-control_args}}")
        return
    # end if
    
    before = ""
    
    sl_name = arg_list.args.pop(0)
    new_path = arg_list.args.pop(0)
    
    call.search_paths_.get(sl_name, null(), sl_info_ptr, sl_info_version_1, code)
    print [ p.pathname for p in sl_info_ptr.data.paths ]
    info = sl_info_path()
    info.pathname = new_path
    if not system.fs.file_exists(new_path):
        info.code = error_table_.no_directory_entry
    # end if
    sl_info_ptr.data.paths.append(info)
    call.ioa_("{0}", [ p.pathname for p in sl_info_ptr.data.paths ])
    print [ p.pathname for p in sl_info_ptr.data.paths ]
    