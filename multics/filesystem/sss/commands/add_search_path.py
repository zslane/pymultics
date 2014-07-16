
from multics.globals import *

# from sl_info import *
include.sl_info

@system_privileged
def add_search_path():
    sl_info_ptr = parm()
    arg_list    = parm()
    full_path   = parm()
    code        = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) < 2:
        call.ioa_("""Usage: add_search_path|asp [search_list_name] [path] {{-control_args}}
    -first
    -last
    -before [path]
    -after [path]""")
        return
    # end if
    
    sl_name = arg_list.args.pop(0)
    new_path = arg_list.args.pop(0)
    call.sys_.get_abs_path(new_path, full_path)
    new_path = full_path.val
    
    call.search_paths_.get(sl_name, null(), sl_info_ptr, sl_info_version_1, code)
    if code.val == error_table_.no_search_list:
        sl_info_ptr.sl_info = alloc(sl_info_p) # make a fresh sl_info object
    # end if
    
    insert_where = len(sl_info_ptr.sl_info.paths) # append to end by default
    
    i = 0
    while i < len(arg_list.args):
        if arg_list.args[i] == "-first":
            i += 1
            insert_where = 0
        elif arg_list.args[i] == "-last":
            i += 1
            insert_where = len(sl_info_ptr.sl_info.paths) # append to end
        elif arg_list.args[i] == "-before":
            i += 1
            if i < len(arg_list.args):
                insert_where = _find_index(sl_info_ptr.sl_info.paths, arg_list.args[i])
                if insert_where == -1:
                    call.ioa_("^a not found in search list ^a", arg_list.args[i], sl_name)
                    return
                # end if
                i += 1
            else:
                call.ioa_("-before requires a path")
                return
            # end if
        elif arg_list.args[i] == "-after":
            i += 1
            if i < len(arg_list.args):
                insert_where = _find_index(sl_info_ptr.sl_info.paths, arg_list.args[i])
                if insert_where == -1:
                    call.ioa_("^a not found in search list ^a", arg_list.args[i], sl_name)
                    return
                else:
                    insert_where += 1
                # end if
                i += 1
            else:
                call.ioa_("-after requires a path")
                return
            # end if
        # end if
    # end while
    
    sl_info_ptr.sl_info.paths.insert(insert_where)
    sl_info_ptr.sl_info.paths[insert_where].pathname = new_path
    
    call.search_paths_.set(sl_name, null(), sl_info_ptr, code)
    if code.val == error_table_.action_not_performed:
        call.ioa_("Invalid path ^a", new_path)
    # print code.val, [ p.pathname for p in sl_info_ptr.sl_info.paths ]
    
asp = add_search_path

def _find_index(sl_info_path_list, path_to_find):
    for i, path in enumerate(sl_info_path_list):
        if path.pathname == path_to_find:
            return i
    return -1
    