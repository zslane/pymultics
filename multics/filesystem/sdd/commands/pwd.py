
from multics.globals import *

def pwd():
    current_dir_name = call.sys_.get_current_directory()
    call.ioa_(current_dir_name)
    