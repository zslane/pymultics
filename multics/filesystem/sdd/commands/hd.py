
from multics.globals import *

def hd():
    declare (home_dir = parm,
             code     = parm)
             
    call.sys_.get_home_directory(home_dir)
    call.sys_.change_current_directory(home_dir.path, code)
