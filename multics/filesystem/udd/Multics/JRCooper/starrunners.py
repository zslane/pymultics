
from multics.globals import *

include.pit

dcl (get_pdir_          = entry . returns (char (168)))
dcl (acl                = char (2) . init ("rw"))
dcl (ring_brackets      = Dim(3) (fixed.bin(3)) . init ([5, 5, 5]))
dcl (whom               = char (5) . init ("*.*.*"))
dcl (DO_dir             = char (4) . init (">sss"))
dcl (DO                 = char (2) . init ("do"))
dcl (dname              = char (14) . init (">udd>m>g>dbd"))
dcl (ename              = char (10) . init ("sv4.4.ship"))
dcl (xname              = char (10) . init ("sv4.4.univ"))
dcl (aname              = char (10) . init ("sv1.2.info"))
dcl (helpfile           = char (25) . init (">udd>m>game>s>star.help"))
dcl (allowed_chars      = char (87) . init ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 !$%&'()*:=-[]{}<>.,/?_|^"))

dcl (

   argn                 = parm,
   argp                 = parm,
   input                = parm,
   code                 = parm,
   univptr              = parm,
   my                   = parm,
   enemy                = parm,
   adminptr             = parm,
   
   admin_info           = PL1.Structure(
       game_admin       = char(21),
       user_info_line   = char(30),
       com_query_line   = char(30),
       star_comn        = fixed.bin,
       star_coms        = Dim(Dynamic.star_comn) (char(21))
   ),
   
   universe             = PL1.Structure(
       number           = fixed.bin,
       pdir             = Dim(10) (char (32)),
       user             = Dim(10) (char (21)),
       unique_id        = Dim(10) (fixed.bin),
       holes            = fixed.bin,
       black_hole       = Dim(5) (char (8)),
       password         = char (10),
       robot            = Dim(20) (PL1.Structure(
           name         = char (5),
           energy       = fixed.bin,
           condition    = char (7),
           location     = char (8),
           controller   = char (21)
       )),
       notifications    = Dim(50) (PL1.Structure(
           person_id    = char (21),
           project_id   = char (9)
       )),
       lock             = fixed.bin (36)
   ),
   
   ship                 = PL1.Structure(
       user             = char (32),
       unique_id        = fixed.bin,
       name             = char (10),
       type             = char (14),
       energy_cur       = fixed.bin,
       energy_old       = fixed.bin,
       energy_max       = fixed.bin,
       shields_cur      = fixed.bin,
       shields_old      = fixed.bin,
       shields_max      = fixed.bin,
       torps_cur        = fixed.bin,
       torps_old        = fixed.bin,
       torps_max        = fixed.bin,
       life_cur         = fixed.bin,
       life_old         = fixed.bin,
       condition        = char (12),
       location         = char (8),
       message          = char (256),
       fromname         = char (10),
       fromtype         = char (14),
       deathmes         = char (4),
       deadname         = char (10),
       deadtype         = char (14),
       cloak_on         = bit (1),
       tractor_on       = bit (1),
       tracname         = char (10),
       monitored_by     = char (10),
       monname          = char (10),
       montype          = char (14),
       monloc           = char (8),
       black_hole       = char (8),
       psionics         = bit (1),
       psi_num          = fixed.bin,
       psi_name         = Dim(10) (char (10)),
       psi_type         = Dim(10) (char (14)),
       psi_mes          = Dim(10) (char (8)),
       lock             = bit (36)
   ),
)
    
def starrunners():

    MAIN                 = "starrunners"
    version              = "4.4"
    pdir                 = ""
    edir                 = ""
    acl_entry            = ""
    shiptype             = ""
    person               = ""
    project              = ""
    access               = "no"
    enter_admin_loop     = False
    video_mode           = False
    accept_notifications = False
    on_the_list          = False
    list_players         = False
    target               = ""
    x                    = 0
    y                    = 0
    z                    = 0
    
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
    call.ioa_ ("\nStarrunners {0}", version)
    
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
    # admin_info = adminptr.ptr
    print adminptr.ptr
    
    call.do (adminptr.ptr.user_info_line)
    call.do (adminptr.ptr.com_query_line)
    call.hcs_.initiate ((get_pdir_ ()), "pit", pit_ptr, code)
    pit = pit_ptr.data
    person = pit.login_name;
    project = pit.project;
    if enter_admin_loop:
        if person == adminptr.ptr.game_admin:
            star_admin()
            return
        else:
            call.ioa_("This command is for Starrunners Administrators only.")
            return
        # end if
    # end if
    
# /* SET UP GAME ENVIRONMENT */
    call.ioa_ ("\nStarrunners {0}", version)
    for x in range(adminptr.ptr.star_comn):
        if person == adminptr.ptr.star_coms[x]: access = "yes"
    # end for
    call.hcs_.initiate(dname, xname, univptr, code)
    if code.val != 0 and univptr.ptr == null():
        call.ioa_("\nI'm sorry, but the STARRUNNERS universe is closed.\nPlease feel free to try later.  Thank you...")
        return
    # end if
    if univptr.ptr.number == 9:
        call.ioa_("\nI'm sorry, but the STARRUNNERS universe is filled to maximum capacity.\nPlease feel free to try later.  Thank you...")
        return
    # end if
    

# /***** STAR ADMIN SYSTEM *****/

def star_admin():
    dcl (password = parm)
    MAIN          = "star_admin"
    version       = "1.2"
    from datetime import datetime as date

    input.val = "";
    call.ioa_("\nStar Admin {0}\n", version)
    call.read_password_("Password:", password)
    if password.val != date.now().strftime("%m%d%Y"):
        call.ioa_("{0}: Incorrect password supplied.", MAIN)
        return
    # end if
    password.val = ""
    while True:
        call.ioa_.nnl("\nStar admin: ")
        getline(input)
        if input.val == "big-bang" or input.val == "bb": big_bang()
        elif input.val == "set-pswd" or input.val == "sp": set_password()
        elif input.val == "remove-pswd" or input.val == "rp": remove_password()
        elif input.val == "add-starcom" or input.val == "as": add_star_commander()
        elif input.val == "remove-starcom" or input.val == "rs": remove_star_commander()
        elif input.val == "generate-code" or input.val == "gc": generate_password()
        elif input.val == "quit" or input.val == "q": return
        elif input.val == ".": call.ioa_("\n{0} {1}", MAIN, version)
        elif input.val == "?":
            call.ioa_("\nStar Admin commands:")
            call.ioa_("   (bb) big-bang ---------- Destroy the universe")
            call.ioa_("   (sp) set-pswd ---------- Set a game password")
            call.ioa_("   (rp) remove-pswd ------- Remove the game password")
            call.ioa_("   (as) add-starcom ------- Add a Person_ID as a Star Commander")
            call.ioa_("   (rs) remove-starcom ---- Remove a Person_ID as a Star Commander")
            call.ioa_("   (gc) generate-code ----- Generate a codeword")
            call.ioa_("    (q) quit -------------- Quit the star admin system")
        elif input.val != "": call.ioa_("{0}: That is not a standard request:\n{1:12}Type a \"?\" for a list of proper requests.", MAIN, "")

def getline(input_var):
    MAIN = "starrunners"

    query_info.version = query_info_version_5
    query_info.suppress_spacing = True
    query_info.suppress_name_sw = True
    # query_info.cp_escape_control = "10"b;
    
    call.command_query_(query_info, input_var, MAIN)
    
include.query_info
        
star = starrunners
