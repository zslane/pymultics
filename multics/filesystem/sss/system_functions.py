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
def shutdown_started_():
    return supervisor.shutdown_started()
    
@system_privileged
def resolve_path_symbol_(path_symbol, frame_id=None):
    process = get_calling_process_()
    symbols = {
        '-home_dir':        process.pit().homedir,
        '-working_dir':     process.directory_stack[-1],
        '-process_dir':     process.dir(),
        '-referencing_dir': supervisor.get_referencing_dir(frame_id),
        '-bound_archives':  supervisor.get_referencing_dir(frame_id),
    }
    return symbols.get(path_symbol, path_symbol)
    
__xlate_table = string.maketrans(string.hexdigits[:16], "BWrtxJNmwpHZbLqz")

def unique_name_(value, xlate_table=[]):
    #== Below is the actual Multics algorithm:
    #==   Grab the value 5 bits at a time and use each 5-bit value as
    #==   an index into the table of characters. The string of chars
    #==   assigned to table comes straight from unique_chars_.pl1
    # table = "BCDFGHJKLMNPQWXZbcdfghjklmnpqwxz"
    # c = ["!"]
    # b = "{0:036b}".format(value)[-36:]
    # for i in range(0, len(b), 5):
        # c.append(table[int(b[i:i+5], 2)])
    # return "".join(c)
    return "!" + "{0:09x}".format(value)[-9:].translate(__xlate_table)

def active_function():
    call.ioa_("active function called ^a", unique_name_(123456789))
