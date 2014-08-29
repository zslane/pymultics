
from multics.globals import *

include.sl_info

SEARCH_PATH_SYMBOLS = [
    "working_dir",
    "referencing_dir",
]

NONDELETABLE_SEARCH_PATH_SYMBOLS = [
    "-home_dir",
    "-process_dir",
]

def _show_usage():
    call.ioa_("Usage: delete_search_rules|dsr [paths]")

def delete_search_rules():
    sl_info_ptr = parm()
    arg_list    = parm()
    full_path   = parm()
    code        = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        _show_usage()
        return
    # end if
    
    paths_to_delete = []
    
    for path in arg_list.args:
        if path not in SEARCH_PATH_SYMBOLS:
            call.sys_.get_abs_path(path, full_path)
            path = full_path.val
        else:
            path = "-" + path
        # end if
        paths_to_delete.append(path)
        
    call.search_paths_.get("object", null(), sl_info_ptr, sl_info_version_1, code)
    if code.val == error_table_.no_search_list:
        return
    # end if
    
    existing_paths = [ p.pathname for p in sl_info_ptr.sl_info.paths ]
    sl_info_ptr.sl_info.num_paths.reset()
    for existing_path in existing_paths:
        if (existing_path in NONDELETABLE_SEARCH_PATH_SYMBOLS) or (existing_path not in paths_to_delete):
            # new_sl_info.paths.insert(-1)
            sl_info_ptr.sl_info.num_paths += 1
            sl_info_ptr.sl_info.paths[sl_info_ptr.sl_info.num_paths - 1].pathname = existing_path
        # end if
    # end for
    call.search_paths_.set("object", null(), sl_info_ptr, code)
    
dsr = delete_search_rules
