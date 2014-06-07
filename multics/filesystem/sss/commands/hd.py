
from multics.globals import *

def hd():
    declare (home_dir = parm,
             code     = parm)
             
    call.user_info_.homedir(home_dir)
    call.sys_.change_current_directory(home_dir.path, code)
