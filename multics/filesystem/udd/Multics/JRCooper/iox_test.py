
from multics.globals import *

dcl (iox_ = entry)

class iox_test(Subroutine):

    def procedure(self):
        buff = parm . init("")
        n_read = parm()
        code   = parm()
        
        # Here we define variables to use inside the lambda
        random_number = parm . init(0)
        with on_quit (lambda:( # <-- equivalent to starting a PL1 'do' block
            random_number (value = mod(clock(), 100) + 1), # <-- This is how to perform variable assignments inside a lambda
            call. ioa_("^/This"), # <-- separate 'statements' (i.e., expressions) with commas
            call. ioa_("is"),
            call. ioa_("an ad-hoc"),
            call. ioa_("quit handler: ^d", random_number.val),
            )): # end lambda
            
            call. ioa_("Enter characters or . to finish:")
            while buff.val != ".":
                call. iox_.get_chars(iox_.user_input, buff, 1, n_read, code)
            # end while
            call. ioa_("^/Done")
        
    def say_quit(self):
        call. ioa_("^/Quitter")
        