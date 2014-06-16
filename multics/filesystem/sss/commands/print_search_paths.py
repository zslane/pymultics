
from multics.globals import *

from sl_info import *
include.sl_list

def print_search_paths():
    declare (sl_info_ptr = parm,
             sl_list_ptr = parm,
             arg_list    = parm,
             code        = parm,
             get_wdir_   = entry . returns (char(168)))
             
    expand = False
    sl_name = ""
    
    call.cu_.arg_list(arg_list)
    while arg_list.args:
        arg = arg_list.args.pop(0)
        if arg == "-expanded" or arg == "-exp":
            expand = True
        elif not arg.startswith("-"):
            sl_name = arg
        else:
            call.ioa_("Usage: print_search_paths {{sl_name}} {{-expanded|-exp}}")
            return
        # end if
    # end while
    
    if sl_name == "":
        call.search_paths_.list(null(), sl_list_ptr, code)
        print sl_list_ptr.data
        sl_names = []
        sl_aliases = {}
        for names in sl_list_ptr.data.link:
            sl_name = names[0]
            sl_names.append(sl_name)
            sl_aliases[sl_name] = names[1:]
        # end for
    else:
        sl_names = [sl_name]
        sl_aliases = {}
    # end if
    
    if expand:
        process = get_calling_process_()
        home_dir = process.pit().homedir
        try:
            working_dir = get_wdir_()
        except:
            working_dir = ">sc1"
        # end try
    # end if
    
    print "sl_names:", sl_names
    for sl_name in sl_names:
        call.search_paths_.get(sl_name, null(), sl_info_ptr, sl_info_version_1, code)
        print [ p.pathname for p in sl_info_ptr.data.paths ]
        aliases = sl_aliases.get(sl_name, [])
        aliases_string = ", ".join(aliases)
        if aliases_string:
            aliases_string = " (%s)" % (aliases_string)
        # end if
        if expand:
            path_list = [ _resolve_path_symbol(home_dir, working_dir, p.pathname) for p in sl_info_ptr.data.paths ]
        else:
            path_list = [ p.pathname for p in sl_info_ptr.data.paths ]
        # end if
        paths_string = "\n    ".join(path_list)
        call.ioa_("{0}{1}:\n    {2}", sl_name, aliases_string, paths_string)
    
def _resolve_path_symbol(home_dir, working_dir, path):
    if path == "-home_dir":
        return home_dir
    elif path == "-working_dir":
        return working_dir
    else:
        return path
    # end if
