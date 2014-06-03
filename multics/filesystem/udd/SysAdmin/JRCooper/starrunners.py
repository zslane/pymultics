
from multics.globals import *

include.query_info

def starrunners():
    declare (cmd = parm)
    
    MAIN = "starrunners"
    
    # call.ioa_("000000000+111111111+222222222+333333333+444444444+555555555+666666666+777777777+")
    # call.ioa_("1234567890"*8)
    #for i in range(20):
    #    call.ioa_(("%02d " % (i + 1)) + "A"*70)
    call.ioa_("Welcome to Star Runners")
    call.ioa_("Experimental v0.0.1")
    call.ioa_()
    call.test_()
    call.test_.func1()
    query_info.suppress_name_sw = True
    query_info.suppress_spacing = True
    while True:
        call.ioa_.nnl("COMMAND> ")
        call.command_query_(query_info, cmd, MAIN)
        if cmd.string == "q":
            break
        # print cmd
    # end while
    call.ioa_("Exiting game. Good bye.")
