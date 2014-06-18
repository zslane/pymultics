import os
from pprint import pprint

from multics.globals import *

include.pit

def test():

    # include.my_info
    
    declare (

        get_pdir_            = entry . returns (char (168)),
        argn                 = parm,
        argp                 = parm,
        adminptr             = parm, #ptr . init (null()),
        
        admin_info           = PL1.Structure(
            game_admin       = char(21),
            user_info_line   = char(30),
            com_query_line   = char(30),
            star_comn        = fixed.bin . init (3),
            star_coms        = Dim(Dynamic.star_comn) (char(21)),
            names            = Dim('*') (fixed.dec(4, 2)),
        ),
        
        segment              = parm,
        segment2             = parm,
        # code                 = parm,
        
        get_wdir_            = entry . returns (char(168)),
    )

    print "-"*80
    call.cu_.arg_count(argn, code)
    if code.val != 0:
        call.com_err_(code.val, MAIN)
        return
    # end if
    print "argn.val =", argn.val
    # exec( globals()['_global_decls'] , globals(), locals() )
    exec "global enter_admin_loop" in globals()
    print enter_admin_loop
    print video_mode
    print list_players
    for x in range(argn.val):
        call.cu_.arg_ptr(x, argp, code)
        arg = argp.val
        if arg == "-admin": enter_admin_loop = True
        # elif arg == "-video": video_mode = True
        # elif arg == "-list_players" or arg == "-lp": list_players = True
        # elif arg == "-accept_notifications" or arg == "-ant": accept_notifications = True
        # elif arg == "-refuse_notifications" or arg == "-rnt": accept_notifications = False
        # elif arg[0] == "-":
            # call.ioa_("{0}: Specified control argument is not accepted. {1}", MAIN, arg)
            # return
        # end if
    # end for
    
    # print type(enter_admin_loop)
    print admin_info
    admin_info.names.size += 5
    admin_info.star_comn += 2
    admin_info.star_coms[0] = "JRCooper"
    admin_info.star_coms[1] = "Foo"
    print admin_info
    print enter_admin_loop
    call.ioa_("enter_adming_loop = {0}", enter_admin_loop)
    