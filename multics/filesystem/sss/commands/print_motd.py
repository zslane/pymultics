
from multics.globals import *

@system_privileged
def print_motd():
    homedir = parm()
    person  = parm()
    project = parm()
    acct    = parm()
    code    = parm()
    
    #== Open user's Person_id.motd file if it exists
    call.user_info_.homedir(homedir)
    call.user_info_.whoami(person, project, acct)
    user_motd_path = vfile_(homedir.val + ">" + person.id + ".motd")
    try:
        uf = open(user_motd_path)
        user_file_text = uf.read()
        uf.close()
    except:
        user_file_text = ""
    # end try
    
    #== Open system motd file if it exists
    try:
        f = open(vfile_(supervisor.fs.system_control_dir + ">motd"))
        file_text = f.read()
        f.close()
    except:
        file_text = ""
    # end try
    
    diff = _find_differences(file_text, user_file_text)
    call.ioa_(diff)
    
    #== Save the current system motd in the user's .motd file if it
    #== is different from the user's version (create it if necessary)
    try:
        if diff:
            uf = open(user_motd_path, "w")
            uf.write(file_text)
            uf.close()
        # end if
    except:
        pass
    
#-- end def print_motd

def _find_differences(file_text, user_file_text):
    sys_motd_lines = file_text.split("\n")
    user_motd_lines = user_file_text.split("\n")
    diff_lines = []
    while sys_motd_lines and user_motd_lines:
        sys_line = sys_motd_lines.pop(0)
        user_line = user_motd_lines.pop(0)
        if user_line != sys_line:
            diff_lines.append(sys_line)
        # end if
    # end while
    if sys_motd_lines:
        diff_lines.extend(sys_motd_lines)
    # end if
    return "\n".join(diff_lines)
    
#-- end def _find_differences

pmotd = print_motd
