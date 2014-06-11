import string

from multics.globals import *

@system_privileged
def get_pdir_():
    process = get_calling_process_()
    return process.dir()

@system_privileged
def get_process_id_():
    process = get_calling_process_()
    return process.id()

@system_privileged
def get_lock_id_():
    process = get_calling_process_()
    return process.stack.lock_id
    
@system_privileged
def get_wdir_():
    process = get_calling_process_()
    return process.directory_stack[-1]
    
@system_privileged
def clock_():
    return system.hardware.clock.current_time()
    
__xlate_table = string.maketrans(string.hexdigits[:16], "BWrtxJNmwpHZbLqz")

def unique_name_(value, xlate_table=[]):
    return "!" + "{0:09x}".format(value)[-9:].translate(__xlate_table)

def active_function():
    call.ioa_("active function called {0}", unique_name_(123456789))
