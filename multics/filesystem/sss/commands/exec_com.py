
from multics.globals import *

@system_privileged
def exec_com():
    declare (get_wdir_ = entry . returns (char(168)))
    
    arg_list  = parm()
    person    = parm()
    project   = parm()
    acct      = parm()
    homedir   = parm()
    full_path = parm()
    code      = parm()
    
    call.cu_.arg_list(arg_list)
    if arg_list.args == []:
        return 0
    # end if
    
    script_file = arg_list.args.pop(0)
    if not script_file.endswith(".ec"):
        script_file += ".ec"
    # end if
    
    if arg_list.args and arg_list.args[0] == "new_proc":
        if arg_list.args != []:
            process_type_string = arg_list.args.pop(0)
        # end if
        
        #== Start with site directory for start_up.ec scripts
        script_dirs = [supervisor.fs.user_dir_dir]
        
        #== Add project directory
        call.user_info_.whoami(person, project, acct)
        script_dirs.append(supervisor.fs.merge_path(supervisor.fs.user_dir_dir, project.id))
        
        #== Add user's home directory
        call.user_info_.homedir(homedir)
        script_dirs.append(homedir.val)
    else:
        call.sys_.get_abs_path(script_file, full_path)
        script_dirs = [full_path.val]
    # end if
    
    for script_dir in script_dirs:
        native_path = supervisor.fs.path2path(script_dir, script_file)
        if supervisor.fs.file_exists(native_path):
            print "exec_com: Running %s script" % (script_dir + ">" + script_file)
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
        # for
    # end if
    return 0
