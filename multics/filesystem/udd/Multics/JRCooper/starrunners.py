
from multics.globals import *

declare (

    argn                 = parm,
    argp                 = parm,
    
    DO_dir               = char (4) . init (">sss"),
    DO                   = char (2) . init ("do"),
    
    input                = char (256) . varying . init (""),
    shiptype             = char (14) . init (""),
    dname                = char (14) . init (">udd>m>g>dbd"),
    ename                = char (10) . init ("sv4.4.ship"),
    xname                = char (10) . init ("sv4.4.univ"),
    aname                = char (10) . init ("sv1.2.info"),
    ring_brackets        = Dim(3) (fixed.bin(3)) . init ([5, 5, 5]),
    code                 = parm,
    allowed_chars        = char (87) . init ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 !$%&'()*:=-[]{}<>.,/?_|^"),
    enter_admin_loop     = bit (1) . init ("0b0"),
    video_mode           = bit (1) . init ("0b0"),
    accept_notifications = bit (1) . init ("0b0"),
    on_the_list          = bit (1) . init ("0b0"),
    list_players         = bit (1) . init ("0b0"),
    target               = char (10) . init (""),
    x                    = fixed.bin . init (0),
    y                    = fixed.bin . init (0),
    z                    = fixed.bin . init (0),
          
    univptr              = ptr . init (null()),
    my                   = ptr . init (null()),
    enemy                = ptr . init (null()),
    adminptr             = parm, #ptr . init (null()),
    
    MAIN                 = char (11) . init ("starrunners"),
    version              = char (5) . init ("4.4"),
    
    admin_info           = PL1.Structure(
        game_admin       = char(21),
        user_info_line   = char(30),
        com_query_line   = char(30),
        star_comn        = fixed.bin,
        star_coms        = Dim('*') (char(21))
    ),
)

def starrunners():

# /***** LET'S GET THE SHOW ON THE ROAD -- PRELIMINARY STUFF *****/

# /* SET GAME MODES: -admin, -video, -list_players CONTROL_ARGS */
    call.cu_.arg_count(argn, code)
    if code.val != 0:
        call.com_err_(code.val, MAIN)
        return
    # end if
    for x in range(argn.val):
        call.cu_.arg_ptr(x, argp, code)
        arg = argp.val
        if arg == "-admin": enter_admin_loop = True
        elif arg == "-video": video_mode = True
        elif arg == "-list_players" or arg == "-lp": list_players = True
        elif arg == "-accept_notifications" or arg == "-ant": accept_notifications = True
        elif arg == "-refuse_notifications" or arg == "-rnt": accept_notifications = False
        elif arg[0] == "-":
            call.ioa_("{0}: Specified control argument is not accepted. {1}", MAIN, arg)
            return
        # end if
    # end for
    
# /* ENTER ADMIN LOOP IF -admin CONTROL_ARG WAS SUPPLIED, AND USER HAS ACCESS */
    call.term_.single_refname(DO, code)
    call.hcs_.initiate(DO_dir, DO, null(), code)
    call.hcs_.initiate(dname, aname, adminptr, code)
    if code.val != 0 and adminptr.ptr == null():
        call.ioa_("\nAdministrative matrix not found.  Game locked.")
        
        #== The following bit of code was not in the original source, but I have
        #== nothing showing how the 'Administrative matrix' was created. Therefore
        #== we create it with this snippet of code based on my best guess as to
        #== what would have typically been in it. Note that I have no recollection
        #== what the user_info_line and com_query_line contained, or what their
        #== purpose was in the code later on.
        call.hcs_.make_seg(dname, aname, adminptr(admin_info), code)
        if code.val == 0:
            with adminptr.ptr:
                adminptr.ptr.game_admin = "JRCooper"
            # end with
            call.ioa_("Administrative matrix created.")
        return
        
    # end if
    print adminptr.ptr

star = starrunners
