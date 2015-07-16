
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
    dir_name  = parm()
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
        if '>' in script_file or '<' in script_file:
            #== The user specified the location of the script file as an absolute or relative path
            call.sys_.get_abs_path(script_file, full_path)
            call.sys_.split_path_(full_path.val, dir_name, null())
        else:
            #== Search exec_com search list for a directory containing the specified ec script
            call.search_paths_.find_dir("exec_com", null(), script_file, dir_name, code)
            if code.val != 0:
                call.com_err_(code.val, "exec_com", "^a using exec_com search list.", script_file)
                return code.val
            # end if
        # end if
        script_dirs = [dir_name.val]
    # end if
    
    for script_dir in script_dirs:
        native_path = supervisor.fs.path2path(script_dir, script_file)
        if supervisor.fs.file_exists(native_path):
            print "exec_com: Running %s script" % (script_dir + ">" + script_file)
            with open(native_path, "r") as f:
                lines = f.readlines()
            # end with
            
            ec_settings = {
                'command_line_echo': True,
            }
            
            for command_line in lines:
                command_line = command_line.strip()
                if command_line:
                    if command_line.startswith("&-"):
                        continue # skip comment lines
                        
                    elif command_line.startswith("&"):
                        process_ec_command(command_line, ec_settings, code)
                        if code.val != 0:
                            call.com_err_(code.val, "exec_com", "^a", command_line)
                            return code.val
                        # end if
                    else:
                        if ec_settings['command_line_echo']:
                            call.ioa_(command_line)
                        # end if
                        call.cu_.cp(command_line, code)
                        if code.val != 0:
                            return code.val
                        # end if
                    # end if
                # end if
            # end for
        # for
    # end if
    return 0

#-- end def exec_com

def process_ec_command(command_line, ec_settings, code):
    args = command_line.split()
    command = args.pop(0)
    
    if command == "&command_line":
        if not args:
            code.val = error_table_.noarg
            return
        # end if
        flag = args.pop(0)
        if flag == "on":
            ec_settings['command_line_echo'] = True
        elif flag == "off":
            ec_settings['command_line_echo'] = False
        else:
            code.val = error_table_.bad_arg
            return
        # end if
        
    # end if
    code.val = 0
    
#-- end def process_ec_command

ec = exec_com
