
from multics.globals import *

def home_dir():
    home_dir = parm()
    code     = parm()
    
    call.user_info_.homedir(home_dir)
    call.sys_.change_current_directory(home_dir.path, code)

#-- end def home_dir

hd = home_dir
