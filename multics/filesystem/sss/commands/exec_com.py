
from multics.globals import *

@system_privileged
def exec_com():
    declare (get_wdir_ = entry . returns (char(168)))
    
    declare (arg_list  = parm,
             homedir   = parm,
             full_path = parm,
             code      = parm)
    
    call.cu_.arg_list(arg_list)
    if arg_list.args == []:
        return 0
    # end if
    
    script_file = arg_list.args.pop(0)
    if not script_file.endswith(".ec"):
        script_file += ".ec"
    # end if
    
    if arg_list.args and arg_list.args[0] == "new_proc":
        call.user_info_.homedir(homedir)
        native_path = system.fs.path2path(homedir.val, script_file)
    else:
        call.sys_.get_abs_path(script_file, full_path)
        native_path = system.fs.path2path(full_path.val)
    # end if
    
    if system.fs.file_exists(native_path):
        print "exec_com: Running %s script" % (script_file)
        with open(native_path, "r") as f:
            lines = f.readlines()
        # end with
        for command_line in lines:
            command_line = command_line.strip()
            if command_line:
                call.cu_.cp(command_line, code)
                if code.val != 0:
                    return code.val
                # end if
            # end if
        # end for
    # end if
    return 0
