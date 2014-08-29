
from multics.globals import *

include.sl_info

SEARCH_PATH_SYMBOLS = [
    "home_dir",
    "process_dir",
    "working_dir",
    "referencing_dir",
]

def _show_usage():
    call.ioa_("""Usage: add_search_rules|asr [path1] {{-control_arg path2}} ...
    -before [path2]
    -after [path2]""")

def add_search_rules():
    sl_info_ptr = parm()
    arg_list    = parm()
    full_path   = parm()
    code        = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        _show_usage()
        return
    # end if
    
    call.search_paths_.get("object", null(), sl_info_ptr, sl_info_version_1, code)
    if code.val == error_table_.no_search_list:
        sl_info_ptr.sl_info = alloc(sl_info_p) # make a fresh sl_info object
    # end if
    
    while arg_list.args:
        if not arg_list.args[0].startswith("-"):
            new_path = arg_list.args.pop(0)
            if new_path not in SEARCH_PATH_SYMBOLS:
                call.sys_.get_abs_path(new_path, full_path)
                new_path = full_path.val
            else:
                new_path = "-" + new_path
            # end if
            
            if arg_list.args and arg_list.args[0].startswith("-"):
                if len(arg_list.args) == 1:
                    _show_usage()
                    return
                
                insert_where = _process_ctrl_arg(sl_info_ptr, arg_list.args)
                if insert_where == -1:
                    #== Error message printed by _process_ctrl_arg()
                    return
            else:
                insert_where = len(sl_info_ptr.sl_info.paths) # append to end by default
                
            sl_info_ptr.sl_info.paths.insert(insert_where)
            sl_info_ptr.sl_info.paths[insert_where].pathname = new_path
            
            call.search_paths_.set("object", null(), sl_info_ptr, code)
            if code.val == error_table_.action_not_performed:
                call.ioa_("Invalid path ^a", new_path)
            # print code.val, [ p.pathname for p in sl_info_ptr.sl_info.paths ]
        else:
            _show_usage()
            return
        # end if
    # end while
    
asr = add_search_rules

def _process_ctrl_arg(sl_info_ptr, args):
    full_path = parm()
    insert_arg = args.pop(0)
    path2 = args.pop(0)
    if path2 not in SEARCH_PATH_SYMBOLS[2:]:
        call.sys_.get_abs_path(path2, full_path)
        path2 = full_path.val
    elif path2 in SEARCH_PATH_SYMBOLS[:2]:
        call.ioa_("^a not allowed as part of control arg", path2)
        return -1
    else:
        path2 = "-" + path2
    # end if
    
    insert_where = _find_index(sl_info_ptr.sl_info.paths, path2)
    if insert_where == -1:
        call.ioa_("^a not found in search rules", path2)
        return -1
    # end if
    
    if insert_arg == "-before":
        pass
    elif insert_arg == "-after":
        insert_where += 1
    else:
        call.ioa_("Valid control arguments are -before and -after")
        return -1
    # end if
    
    return insert_where

def _find_index(sl_info_path_list, path_to_find):
    for i, path in enumerate(sl_info_path_list):
        if path.pathname == path_to_find:
            return i
    return -1
    