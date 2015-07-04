
from multics.globals import *

dcl ( cu_ = entry )

def break_test():
    #== There are two ways of calling cu_.arg_list_ptr(). One is as a function
    #== that returns a python list of the argument strings. The other is as a
    #== procedure taking one parm and setting it to a cu_.arglist instance
    #== filled with the argument info. While cu_.arglist is not actually
    #== defined as a PL1.Structure (it is just a python object class), the
    #== structure declared below shows its attributes in Multics PL/I form.
    
    dcl ( arg_list_ptr = ptr )
    
    dcl ( argl = PL1.Structure . based (arg_list_ptr="argl") (
            argc = fixed.bin (16),
            type = fixed.bin (18),
            desc = fixed.bin (16),
            aptr = Dim(Dynamic.argc) (char ('*'))
        ))
        
    call. cu_.arg_list_ptr (arg_list_ptr)
    # call. ioa_ ("^r", arg_list_ptr.val)
    call. ioa_ ("^r", argl)
    
    arg_list_ptr = cu_.arg_list_ptr ()
    
    #== Get number of iterations
    if arg_list_ptr:
        num_iterations = int(arg_list_ptr.pop(0))
    else:
        num_iterations = 10
        
    #== Get iteration delay (in seconds)
    if arg_list_ptr:
        delay = real(arg_list_ptr.pop(0))
    else:
        delay = 1
    
    call. ioa_ ("Running ^d iterations for ^d seconds each:", num_iterations, delay)
    for x in do_range(1, num_iterations):
        check_conditions_()
        call. ioa_ ("Iteration ^d", x)
        call. timer_manager_.sleep (delay, 0)
        