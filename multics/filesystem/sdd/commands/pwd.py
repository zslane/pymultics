
from multics.globals import *

def pwd():
    declare (current_dir = parm)
    call.sys_.get_current_directory(current_dir)
    call.ioa_(current_dir.name)
    