
from multics.globals import *

from sl_info import *

def print_search_paths():
    declare (resolve_path_symbol_ = entry . returns (char(168)))
    sl_info_ptr = parm()
    sl_list_ptr = parm()
    arg_list    = parm()
    code        = parm()
    
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
            call.ioa_("Usage: print_search_paths|psp {{sl_name}} {{-expanded|-exp}}")
            return
        # end if
    # end while
    
    if sl_name == "":
        call.search_paths_.list(null(), sl_list_ptr, code)
        sl_names = []
        sl_aliases = {}
        list_link = sl_list_ptr.data
        while list_link:
            sl_name = list_link.names[0]
            sl_names.append(sl_name)
            sl_aliases[sl_name] = list_link.names[1:]
            list_link = list_link.link
        # end for
    else:
        sl_names = [sl_name]
        sl_aliases = {}
    # end if
    
    for sl_name in sl_names:
        call.search_paths_.get(sl_name, null(), sl_info_ptr, sl_info_version_1, code)
        aliases = sl_aliases.get(sl_name, [])
        aliases_string = ", ".join(aliases)
        if aliases_string:
            aliases_string = " (%s)" % (aliases_string)
        # end if
        if expand:
            path_list = [ resolve_path_symbol_(p.pathname) for p in sl_info_ptr.data.paths ]
        else:
            path_list = [ p.pathname for p in sl_info_ptr.data.paths ]
        # end if
        paths_string = "\n    ".join(path_list)
        call.ioa_("{0}{1}:\n    {2}", sl_name, aliases_string, paths_string)

psp = print_search_paths
