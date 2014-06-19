
from multics.globals import *

include.pit

MAIN                     = "starrunners"

dcl (get_pdir_           = entry . returns(char(168)))
dcl (clock_              = entry . returns(fixed.bin(36)))
dcl (acl                 = char(2) . init("rw"))
dcl (ring_brackets       = Dim(3) (fixed.bin(3)) . init([5, 5, 5]))
dcl (whom                = char(5) . init("*.*.*"))
dcl (DO_dir              = char(4) . init(">sss"))
dcl (DO                  = char(2) . init("do"))
dcl (dname               = char(14) . init(">udd>m>g>dbd"))
dcl (ename               = char(10) . init("sv4.4.ship"))
dcl (xname               = char(10) . init("sv4.4.univ"))
dcl (aname               = char(10) . init("sv1.2.info"))
dcl (helpfile            = char(25) . init(">udd>m>game>s>star.help"))
dcl (allowed_chars       = char(87) . init("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 !$%&'()*:=-[]{}<>.,/?_|^"))

adminptr                 = pointer
univptr                  = pointer

dcl (

    argn                 = parm,
    argp                 = parm,
    input                = parm . init(""),
    code                 = parm,
    my                   = parm,
    enemy                = parm,
    
    admin_info           = PL1.Structure . based(adminptr) (
        game_admin       = char(21),
        user_info_line   = char(30),
        com_query_line   = char(30),
        star_comn        = fixed.bin,
        star_coms        = Dim(Dynamic.star_comn) (char(21))
    ),
    
    universe             = PL1.Structure . based(univptr) (
        number           = fixed.bin,
        pdir             = Dim(10) (char(32)),
        user             = Dim(10) (char(21)),
        unique_id        = Dim(10) (fixed.bin),
        holes            = fixed.bin,
        black_hole       = Dim(5) (char(8)),
        password         = char(10),
        robot            = Dim(20) (PL1.Structure(
            name         = char(5),
            energy       = fixed.bin,
            condition    = char(7),
            location     = char(8),
            controller   = char(21)
        )),
        notifications    = Dim(50) (PL1.Structure(
            person_id    = char(21),
            project_id   = char(9)
        )),
        lock             = fixed.bin(36)
    ),
    
    ship                 = PL1.Structure(
        user             = char(32),
        unique_id        = fixed.bin,
        name             = char(10),
        type             = char(14),
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
        condition        = char(12),
        location         = char(8),
        message          = char(256),
        fromname         = char(10),
        fromtype         = char(14),
        deathmes         = char(4),
        deadname         = char(10),
        deadtype         = char(14),
        cloak_on         = bit(1),
        tractor_on       = bit(1),
        tracname         = char(10),
        monitored_by     = char(10),
        monname          = char(10),
        montype          = char(14),
        monloc           = char(8),
        black_hole       = char(8),
        psionics         = bit(1),
        psi_num          = fixed.bin,
        psi_name         = Dim(10) (char(10)),
        psi_type         = Dim(10) (char(14)),
        psi_mes          = Dim(10) (char(8)),
        lock             = bit(36)
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
    
# /* ENTER ADMIN LOOP IF -admin CONTROL_ARG WAS SUPPLIED, AND USER HAS ACCESS */
    call.term_.single_refname(DO, code)
    call.hcs_.initiate(DO_dir, DO, null(), code)
    call.hcs_.initiate(dname, aname, adminptr, code)
    if code.val != 0 and adminptr.ptr == null():
        call.ioa_("\nAdministrative matrix not found.  Game locked.")
        
        #== The following bit of code was not in the original source, but I have
        #== no idea how the admin database originally got bootstrapped. Access to
        #== the star_admin() function, which provides the 'big-bang' command for
        #== creating a new admin database, is dependent on the current value of the
        #== admin_info.game_admin field. So how does the very first admin database
        #== get created? No clue. Hence this code. Note that I have no recollection
        #== of what the user_info_line or com_query_line contained, or what their
        #== purpose was in the code later on.
        
        call.hcs_.make_seg(dname, aname, adminptr, code)
        if code.val == 0:
            with admin_info:
                #== This at least gives me access to 'admin mode' which in turn
                #== provides command (i.e., 'big-bang') for creating the universe
                #== database that the rest of the game depends on.
                admin_info.game_admin = "JRCooper"
            # end with
            call.ioa_("Administrative matrix created.")
        # end if
        
        return
        
    # end if
    print admin_info
    
    call.do(admin_info.user_info_line)
    call.do(admin_info.com_query_line)
    call.hcs_.initiate(get_pdir_(), "pit", pit_ptr, code)
    pit = pit_ptr.ptr
    person = pit.login_name
    project = pit.project
    if enter_admin_loop:
        if person == admin_info.game_admin:
            star_admin()
            return
        else:
            call.ioa_("This command is for Starrunners Administrators only.")
            return
        # end if
    # end if
    
# /* SET UP GAME ENVIRONMENT */
    call.ioa_("\nStarrunners {0}", version)
    for x in range(admin_info.star_comn):
        if person == admin_info.star_coms[x]: access = "yes"
    # end for
    call.hcs_.initiate(dname, xname, univptr, code)
    if code.val != 0 and univptr.ptr == null():
        call.ioa_("\nI'm sorry, but the STARRUNNERS universe is closed.\nPlease feel free to try later.  Thank you...")
        return
    # end if
    if universe.number == 9:
        call.ioa_("\nI'm sorry, but the STARRUNNERS universe is filled to maximum capacity.\nPlease feel free to try later.  Thank you...")
        return
    # end if
               
# /* ACCEPT/REFUSE NOTIFICATIONS.  PUT/TAKE ON/FROM LIST */
    for x in range(50):
        if universe.notifications[x].person_id == person and universe.notifications[x].project_id == project:
            if not accept_notifications:
                with universe:
                    universe.notifications[x].person_id = ""
                    universe.notifications[x].project_id = ""
                # end with
            # end if
            on_the_list = True
        # end if
    # end for
    if not on_the_list and accept_notifications:
        for x in range(50):
            if universe.notifications[x].person_id == "" and universe.notifications[x].project_id == "":
                with universe:
                    universe.notifications[x].person_id = person
                    universe.notifications[x].project_id = project
                    return
                # end with
            # end if
        # end for
    # end if
    if not on_the_list and accept_notifications: call.ioa_("\nSorry, but the notifications list is full to maximum capacity...")
    if on_the_list: return
        
# /* IF -list_players CONTROL_ARG WAS SUPPLIED, LIST PLAYERS, NO GAME */
    if list_players:
        call.ioa_("\nList of players: {0}", "none" if universe.number == 0 else universe.number)
        for x in range(universe.number):
            call.ioa_("   {0}", universe.user[x])
        # end for
        return
    # end if
    
# /* ASK HIM IF HE WANTS INSTRUCTIONS */
    while input.val == "":
        call.ioa_.nnl("\nWould you like instructions? ")
        getline(input)
        if input.val == "yes" or input.val == "y": call.print_(helpfile, "1")
        elif input.val != "no" and input.val != "n":
            call.ioa_("\nPlease answer \"yes\" or \"no\".")
            input.val = ""
        # end if
    # end while
          
# /* GET GAME PASSWORD (IF THERE IS ONE) */
    if universe.password != "":
        call.ioa_.nnl("\nPassword: ")
        getline(input)
        if input.val != universe.password:
            call.ioa_("Incorrect password supplied.")
            call.ioa_("Please contact Starrunners Administrator for correct password.")
            return
        # end if
    # end if
               
# /* SET quit AND seg_fault_error TO DESTROY SHIP/END GAME */
          # on quit call game_over;
          # on seg_fault_error call universe_destroyed;

# /* SET finish TO TURN OFF NOTIFICATIONS */
          # on finish begin;
                    # do x = 1 to 50;
                         # if universe.notifications (x).person_id = person & universe.notifications (x).project_id = project then do;
                                   # universe.notifications (x).person_id = "";
                                   # universe.notifications (x).project_id = "";
                              # end;
                    # end;
                    # call continue_to_signal_ ((0));
               # end;
               
# /* MAKE HIS SHIP */
    pdir = get_pdir_()
    call.hcs_.initiate(pdir, ename, my, code)
    if my.ship != null(): call.hcs_.delentry_seg(my.ship, code)
    call.hcs_.make_seg(pdir, ename, my(ship), code)
    acl_entry = pdir + ">" + ename
    # call set_acl (entry, acl, whom);
    # call hcs_$set_ring_brackets (pdir, ename, ring_brackets, code);
    if code.val != 0:
        call.com_err_(code.val, MAIN)
        return
    # end if
               
# /* CLEAN OUT SHIP DATA FOR A FRESH START */
    lock(my.ship)
    with my.ship:
        my.ship.user = my.ship.name = my.ship.type = my.ship.condition = my.ship.message = my.ship.fromname = my.ship.fromtype = my.ship.deathmes = my.ship.deadname = my.ship.deadtype = my.ship.tracname = my.ship.monitored_by = my.ship.monloc = ""
        my.ship.psi_name = [""] * 10
        my.ship.psi_type = [""] * 10
        my.ship.psi_mes = [""] * 10
        my.ship.monname = my.ship.montype = "#"
        my.ship.location = "PHASING"
        my.ship.black_hole = "start"
        my.ship.energy_cur = my.ship.energy_old = my.ship.energy_max = my.ship.shields_cur = my.ship.shields_old = my.ship.shields_max = my.ship.torps_cur = my.ship.torps_old = my.ship.torps_max = my.ship.life_cur = my.ship.life_old = my.ship.psi_num = 0;
        my.ship.cloak_on = my.ship.tractor_on = my.ship.psionics = False
        my.ship.unique_id = clock_()
    # end with
    unlock(my.ship)

# /* ADD HIM TO LIST OF PLAYERS IN THE STARRUNNERS UNIVERSE */
    if universe.number == 9:
        call.ioa_("I'm sorry, but the STARRUNNERS universe if filled to maximum capacity.\nPlease feel free to try later.  Thank you...")
        return
    # end if
    lock(universe)
    with universe:
        universe.number = universe.number + 1
        universe.pdir[universe.number - 1] = pdir
        universe.unique_id[universe.number - 1] = my.ship.unique_id
        universe.user[universe.number - 1] = person
        if universe.number == 1:
                universe.holes = 0
                universe.black_hole = ""
                for i in range(20):
                    universe.robot[i].energy = 0
                    universe.robot[i].location = ""
                    universe.robot[i].condition = ""
                    universe.robot[i].controller = "none"
                # end for
        # end if
    # end with
    unlock(universe)

# /* RECORED THE USER'S PERSON_ID */
    lock(my.ship)
    with my.ship:
        my.ship.user = person
    unlock(my.ship)

# /* GET SHIP NAME */
    input.val = ""
    while input.val == "":
        call.ioa_.nnl("\nShip name: ")
        getline(input)
        if verify(input.val, allowed_chars) != 0:
            call.ioa_("Invalid ship name: {0}", input.val)
            input.val = ""
        # end if
        for x in range(universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null() and edir != pdir and input.val == enemy.ship.name:
                call.ioa_("\nThe name you have chosen is presently in use.\nPlease choose a different name.")
                input.val = ""
            # end if
        # end for
        if input.val != "":
            with my.ship:
                my.ship.name = input.val
            # end with
        # end if
    # end while
          
def lock(lock_bit):
    call.set_lock_.lock(lock_bit, 5, code)
    
def unlock(lock_bit):
    call.set_lock_.unlock(lock_bit, code)

def verify(x, y):
    return len(set(x) - set(y))
    
# /***** STAR ADMIN SYSTEM *****/

def star_admin():
    password      = parameter()
    MAIN          = "star_admin"
    version       = "1.2"
    from datetime import datetime as date
    
    input.val = ""
    call.ioa_("\nStar Admin {0}\n", version)
    call.read_password_("Password:", password)
    if password.val != date.now().strftime("%m%d%Y"):
        call.ioa_("{0}: Incorrect password supplied.", MAIN)
        # return
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
            call.ioa_("  (bb) big-bang ---------- Destroy the universe")
            call.ioa_("  (sp) set-pswd ---------- Set a game password")
            call.ioa_("  (rp) remove-pswd ------- Remove the game password")
            call.ioa_("  (as) add-starcom ------- Add a Person_ID as a Star Commander")
            call.ioa_("  (rs) remove-starcom ---- Remove a Person_ID as a Star Commander")
            call.ioa_("  (gc) generate-code ----- Generate a codeword")
            call.ioa_("   (q) quit -------------- Quit the star admin system")
        elif input.val != "": call.ioa_("{0}: That is not a standard request:\n{1:12}Type a \"?\" for a list of proper requests.", MAIN, "")

# /* STAR ADMIN REQUEST ROUTINES */

def big_bang():
    call.hcs_.initiate(dname, xname, univptr, code)
    if code.val != 0 and univptr.ptr == null():
        call.ioa_("{0}(big_bang): No database was found.", MAIN)
        call.ioa_("Creating {0}>{1}", dname, xname)
        call.hcs_.make_seg(dname, xname, univptr, code)
        with universe:
            universe.number     = 0
            universe.holes      = 0
            universe.unique_id  = [0] * 10
            universe.pdir       = [""] * 10
            universe.user       = [""] * 10
            universe.black_hole = [""] * 5
            universe.password   = ""
        # end with
    else:
        call.ioa_("{0}(big_bang): Database destroyed and re-created.", MAIN)
        call.hcs_.delentry_seg(univptr.ptr, code)
        call.hcs_.make_seg(dname, xname, univptr, code)
        with universe:
            universe.number     = 0
            universe.holes      = 0
            universe.unique_id  = [0] * 10
            universe.pdir       = [""] * 10
            universe.user       = [""] * 10
            universe.black_hole = [""] * 5
            universe.password   = ""
        # end with
    # end if
    
    call.hcs_.initiate(dname, aname, adminptr, code)
    if code.val != 0 and adminptr.ptr == null():
        create_database()
        call.ioa_("\nCreated: {0}>{1}", dname, aname)
    else:
        call.hcs_.delentry_seg(adminptr.ptr, code)
        create_database()
    # end if
#-- end def big_bang
    
def create_database():
    acl = "r"
    whom = "*.*.*"
    
    call.hcs_.make_seg(dname, aname, adminptr, code)
    #call.set_acl(dname.rstrip() + ">" + aname, acl, whom)
    # admin_info = adminptr.ptr
    with admin_info:
        call.ioa_.nnl("{0}(admin_info): Game Admin: ", MAIN)
        getline(input)
        admin_info.game_admin = input.val
        call.ioa_.nnl("{0}(admin_info): User_info_line: ", MAIN)
        getline(input)
        admin_info.user_info_line = input.val
        call.ioa_.nnl("{0}(admin_info): Command_query_line: ", MAIN)
        getline(input)
        admin_info.com_query_line = input.val
        admin_info.star_comn += 1
        call.ioa_.nnl("{0}(admin_info): Star Commander: ", MAIN)
        getline(input)
        admin_info.star_coms[0] = input.val
    # end with
#-- end def create_database

def getline(input_var):
    MAIN = "starrunners"

    query_info.version = query_info_version_5
    query_info.suppress_spacing = True
    query_info.suppress_name_sw = True
    # query_info.cp_escape_control = "10"b;
    
    call.command_query_(query_info, input_var, MAIN)
    
include.query_info
        
star = starrunners
