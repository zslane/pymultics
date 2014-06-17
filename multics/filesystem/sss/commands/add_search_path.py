
from multics.globals import *

from sl_info import *

@system_privileged
def add_search_path():
    declare (sl_info_ptr = parm,
             arg_list    = parm,
             code        = parm)
             
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) < 2:
        call.ioa_("""Usage: add_search_path [search_list_name] [path] {{-control_args}}
    -first
    -last
    -before [path]
    -after [path]""")
        return
    # end if
    
    sl_name = arg_list.args.pop(0)
    new_path = arg_list.args.pop(0)
    
    call.search_paths_.get(sl_name, null(), sl_info_ptr, sl_info_version_1, code)
    if code.val == error_table_.no_search_list:
        sl_info_ptr.data = sl_info_structure()
    # end if
    
    insert_where = len(sl_info_ptr.data.paths) # append to end by default
    
    i = 0
    while i < len(arg_list.args):
        if arg_list.args[i] == "-first":
            i += 1
            insert_where = 0
        elif arg_list.args[i] == "-last":
            i += 1
            insert_where = len(sl_info_ptr.data.paths) # append to end
        elif arg_list.args[i] == "-before":
            i += 1
            if i < len(arg_list.args):
                insert_where = _find_index(sl_info_ptr.data.paths, arg_list.args[i])
                if insert_where == -1:
                    call.ioa_("{0} not found in search list {1}", arg_list.args[i], sl_name)
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
                insert_where = _find_index(sl_info_ptr.data.paths, arg_list.args[i])
                if insert_where == -1:
                    call.ioa_("{0} not found in search list {1}", arg_list.args[i], sl_name)
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
    
    info = sl_info_path()
    info.pathname = new_path
    sl_info_ptr.data.paths.insert(insert_where, info)
    call.search_paths_.set(sl_name, null(), sl_info_ptr, code)
    if code.val == error_table_.action_not_performed:
        call.ioa_("Invalid path {0}", new_path)
    print code.val, [ p.pathname for p in sl_info_ptr.data.paths ]
    
def _find_index(sl_info_path_list, path_to_find):
    for i, path in enumerate(sl_info_path_list):
        if path.pathname == path_to_find:
            return i
    return -1
    