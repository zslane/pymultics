
from multics.globals import *

def who():
    users    = parm()
    daemons  = parm()
    arg_list = parm()
    
    show_header = True
    show_users = True
    show_daemons = True
    sort_by_name = False
    sort_by_proj = False
    
    call.cu_.arg_list(arg_list)
    for arg in arg_list.args:
        if arg == "-brief" or arg == "-br":
            show_header = False
        elif arg == "-interactive" or arg == "-ia":
            show_users = True
            show_daemons = False
        elif arg == "-daemon" or arg == "-dmn":
            show_daemons = True
            show_users = False
        elif arg == "-name" or arg == "-nm":
            sort_by_name = True
            sort_by_proj = False
        elif arg == "-project" or arg == "-pj":
            sort_by_proj = True
            sort_by_name = False
        elif arg.startswith("-"):
            call.ioa_("Unrecognized control argument {0}", arg)
            call.ioa_("  valid: -brief|-br, -interactive|-ia, -daemon|-dmn, -name|-nm, -project|-pr")
            return
        # end if
    # end for
    
    if show_users:
        call.sys_.get_users(users)
    else:
        users.list = []
    # end if
    
    if show_daemons:
        call.sys_.get_daemons(daemons)
    else:
        daemons.list = []
    # end if
    
    who_list = []
    if show_daemons:
        who_list.extend(daemons.list)
    if show_users:
        who_list.extend(users.list)
    # end if
    
    if sort_by_name:
        who_list = sorted(who_list)
    elif sort_by_proj:
        who_list = sorted(who_list, key=lambda x: x.split(".")[1])
    # end if
    
    if show_header:
        _display_header(show_users, len(users.list), show_daemons, len(daemons.list))
    # end if
    
    # call.ioa_("{0} user{1} logged in", len(users.list), "s" if len(users.list) > 1 else "")
    line = ""
    for i, user_id in enumerate(who_list):
        line += "{0:<25}".format(user_id)
        if (i + 1) % 3 == 0:
            call.ioa_("  {0}", line)
            line = ""
        # end if
    # end for
    if line:
        call.ioa_("  {0}", line)
    
@system_privileged
def _display_header(show_users, num_users, show_daemons, num_daemons):
    import os
    load = len(os.listdir(supervisor.fs.path2path(supervisor.fs.process_dir_dir)))
    
    stat_list = []
    if show_users:
        stat_list.append("{0} users".format(num_users))
    if show_daemons:
        stat_list.append("{0} daemons".format(num_daemons))
        
    call.ioa_("Virtual Multics {0}, load {1:0.1f}/{2:0.2f}; {3} users\n  {4}.",
        supervisor.version,
        load,
        supervisor.site_config['maximum_load'],
        num_users + num_daemons,
        ", ".join(stat_list))
        