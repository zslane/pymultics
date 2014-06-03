import string

from multics.globals import *

@system_privileged
def get_pdir_():
    return system.hardware.filesystem.process_dir_dir

@system_privileged
def clock_():
    return system.hardware.clock.current_time()
    
__xlate_table = string.maketrans(string.hexdigits[:16], "BWrtxJNmwpHZbLqz")

def unique_name_(value, xlate_table=[]):
    return "!" + "{0:09x}".format(value)[-9:].translate(__xlate_table)
        
def active_function():
    call.ioa_("active function called {0}", unique_name_(123456789))
