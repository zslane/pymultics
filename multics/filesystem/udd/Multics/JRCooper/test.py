
from multics.globals import *

def test():

    declare (

        admin_info           = PL1.Structure(
            game_admin       = char(21),
            user_info_line   = char(30),
            com_query_line   = char(30),
            star_comn        = fixed.bin . init (3),
            star_coms        = Dim(Dynamic.star_comn) (char(21)),
            names            = Dim('*') (fixed.dec(4, 2)),
        ),
        
        segment              = parm,
        code                 = parm,
        
        get_wdir_            = entry . returns (char(168)),
    )

    print admin_info
    admin_info.names.size += 5
    admin_info.star_comn += 2
    admin_info.star_coms[0] = "JRCooper"
    admin_info.star_coms[1] = "Foo"
    print admin_info
    
    call.hcs_.make_seg(get_wdir_(), "test.data", segment(admin_info), code)
    if code.val == 0:
        call.hcs_.delentry_seg(segment.ptr, code)
    # call.term_.single_refname("test", code)
    