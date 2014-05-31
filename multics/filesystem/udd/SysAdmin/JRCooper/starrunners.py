
from multics.globals import *

def starrunners():
    # call.ioa_("000000000+111111111+222222222+333333333+444444444+555555555+666666666+777777777+")
    # call.ioa_("1234567890"*8)
    #for i in range(20):
    #    call.ioa_(("%02d " % (i + 1)) + "A"*70)
    call.ioa_("Welcome to Star Runners")
    call.ioa_("Experimental v0.0.1")
    call.ioa_()
    call.test_()
    call.test_.func1()
    while True:
        call.ioa_.nnl("COMMAND> ")
        cmd = call.command_query_()
        if cmd == "q":
            break
        # print cmd
    # end while
    call.ioa_("Exiting game. Good bye.")
