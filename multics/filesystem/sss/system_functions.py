import string

from multics.globals import *

def get_pdir_():
    process = get_calling_process_()
    return process.dir()

def get_process_id_():
    process = get_calling_process_()
    return process.id()
    
def get_wdir_():
    process = get_calling_process_()
    return process.directory_stack[-1]
    
@system_privileged
def clock_():
    return supervisor.hardware.clock.current_time()
    
@system_privileged
def clock():
    return supervisor.hardware.clock.current_time()
    
@system_privileged
def shutdown_started_():
    return supervisor.shutdown_started()
    
def resolve_path_symbol_(path_symbol):
    process = get_calling_process_()
    symbols = {
        '-home_dir':    process.pit().homedir,
        '-working_dir': process.directory_stack[-1],
        '-process_dir': process.dir(),
    }
    return symbols.get(path_symbol, path_symbol)
    
__xlate_table = string.maketrans(string.hexdigits[:16], "BWrtxJNmwpHZbLqz")

def unique_name_(value, xlate_table=[]):
    return "!" + "{0:09x}".format(value)[-9:].translate(__xlate_table)

def active_function():
    call.ioa_("active function called ^a", unique_name_(123456789))
