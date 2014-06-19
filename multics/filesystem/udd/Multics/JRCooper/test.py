import os
from pprint import pprint

from multics.globals import *

# include.my_info
# my_info_ptr = pointer

# declare (
    # my_info_structure = PL1.Structure . based (my_info_ptr) (
        # x = fixed.bin,
        # y = float.bin,
        # z = char(30),
    # )
# )
# adminptr = pointer

def test():

    include.my_info
    adminptr = pointer
    
    declare (

        get_pdir_            = entry . returns (char (168)),
        argn                 = parm,
        argp                 = parm,
        adminptr             = parm,
        
        admin_info           = PL1.Structure . based(adminptr) (
            game_admin       = char(21),
            user_info_line   = char(30),
            com_query_line   = char(30),
            star_comn        = fixed.bin . init (3),
            star_coms        = Dim(Dynamic.star_comn) (char(21)),
            names            = Dim('*') (fixed.dec(4, 2)),
        ),
        
        segment              = parm,
        segment2             = parm,
        code                 = parm,
        
        get_wdir_            = entry . returns (char(168)),
    )
    
    # call.ioa_("{0}", admin_info)
    # admin_info.names.size += 5
    # admin_info.star_comn += 2
    # admin_info.star_coms[0] = "JRCooper"
    # admin_info.star_coms[1] = "Foo"
    # call.ioa_("{0}", admin_info)
    
    call.ioa_("Initial:\n{0}", my_info)
    my_info_ptr.data = None
    call.ioa_("After setting my_info_ptr to None:\n{0}", my_info)
    my_info_ptr.reset()
    call.ioa_("After resetting my_info_ptr:\n{0}", my_info)
    
    working_dir = get_wdir_()
    
    # call.hcs_.initiate(working_dir, "test.data", adminptr, code)
    # call.ioa_("code = {0}, adminptr = {0}", code.val, adminptr.ptr)
    # print type(admin_info)
    # return

    call.ioa_("working_dir = {0}", working_dir)
    call.hcs_.initiate(working_dir, "test.data", my_info_ptr, code)
    if code.val != 0 and my_info_ptr.seg == null():
        call.ioa_("File test.data not found ({0}).\nCreating it.", code.val)
        call.hcs_.make_seg(working_dir, "test.data", my_info_ptr, code)
        print type(my_info)
        call.ioa_("code = {0}", code.val)
        call.ioa_("{0}", my_info)
        call.ioa_("Setting values...")
        my_info.x = 10
        my_info.y = 20.0
        my_info.z = '30'
        call.ioa_("{0}", my_info)
    else:
        call.ioa_("File test.data found.")
        call.ioa_("{0}", my_info)
        call.ioa_("Deleting it.")
        call.hcs_.delentry_seg(my_info_ptr.seg, code)
        call.ioa_("code = {0}", code.val)
        