from pprint import pprint

from multics.globals import *

include.pit
include.query_info

class goto_command_loop(NonLocalGoto): pass
class goto_end_of_game(NonLocalGoto): pass

dcl (get_pdir_               = entry . returns (char(168)))
dcl (clock_                  = entry . returns (fixed.bin(36)))

#== True global variables (that aren't parm types)
pdir                         = ""
acl_entry                    = ""
shiptype                     = ""
person                       = ""
project                      = ""
access                       = "no"
ROBOT                        = ""

def starrunners():

    MAIN                     = "starrunners"

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
    
    adminptr                 = ptr . init(null())
    univptr                  = ptr . init(null())
    my                       = ptr . init(null())
    enemy                    = ptr . init(null())
    
    dcl (
        
        argn                 = fixed.bin . parm . init(0),
        argp                 = ptr . init(null()),
        input                = char(256) . varying . parm . init(""),
        target               = char(10) . parm . init(""),
        code                 = fixed.bin(35) . parm . init(0),
        
        admin_info           = PL1.Structure . based(adminptr = "admin_info") (
            game_admin       = char(21),
            user_info_line   = char(30),
            com_query_line   = char(30),
            star_comn        = fixed.bin,
            star_coms        = Dim(Dynamic.star_comn) (char(21))
        ),
        
        universe             = PL1.Structure . based(univptr = "universe") (
            number           = fixed.bin,
            pdir             = Dim(10+1) (char(32)),
            user             = Dim(10+1) (char(21)),
            unique_id        = Dim(10+1) (fixed.bin),
            holes            = fixed.bin,
            black_hole       = Dim(5+1) (char(8)),
            password         = char(10),
            robot            = Dim(20+1) (PL1.Structure(
                name         = char(5),
                energy       = fixed.bin,
                condition    = char(7),
                location     = char(8),
                controller   = char(21)
            )),
            notifications    = Dim(50+1) (PL1.Structure(
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
            psi_name         = Dim(10+1) (char(10)),
            psi_type         = Dim(10+1) (char(14)),
            psi_mes          = Dim(10+1) (char(8)),
            lock             = bit(36)
        ),
    )
    
    def procedure():
    
        MAIN                 = "starrunners"
        version              = "4.4"
        
        edir                 = ""
        enter_admin_loop     = False
        video_mode           = False
        accept_notifications = False
        on_the_list          = False
        list_players         = False
        
        global pdir
        global acl_entry
        global shiptype
        global person
        global project
        global access
        
    # /***** LET'S GET THE SHOW ON THE ROAD -- PRELIMINARY STUFF *****/
        
    # /* SET GAME MODES: -admin, -video, -list_players CONTROL_ARGS */
        call.cu_.arg_count(argn, code)
        if code.val != 0:
            call.com_err_(code.val, MAIN)
            return
        # end if
        for x in range(argn.val):
            call.cu_.arg_ptr(x, argp, code) ; arg = argp.val
            if arg == "-admin": enter_admin_loop = True
            elif arg == "-video": video_mode = True
            elif arg == "-list_players" or arg == "-lp": list_players = True
            elif arg == "-accept_notifications" or arg == "-ant": accept_notifications = True
            elif arg == "-refuse_notifications" or arg == "-rnt": accept_notifications = False
            elif substr(arg, 1, 1) == "-":
                call.ioa_("^a: Specified control argument is not accepted. ^a", MAIN, arg)
                return
            # end if
        # end for
        
    # /* ENTER ADMIN LOOP IF -admin CONTROL_ARG WAS SUPPLIED, AND USER HAS ACCESS */
        call.term_.single_refname(DO, code)
        call.hcs_.initiate(DO_dir, DO, DO, 0, 0, null(), code)
        call.hcs_.initiate(dname, aname, "", 0, 0, adminptr, code)
        if code.val != 0 and adminptr.ptr == null():
            call.ioa_("^/Administrative matrix not found.  Game locked.")
            
            #== The following bit of code was not in the original source, but I have
            #== no idea how the admin database originally got bootstrapped. Access to
            #== the star_admin() function, which provides the 'big-bang' command for
            #== creating a new admin database, is dependent on the current value of the
            #== admin_info.game_admin field. So how does the very first admin database
            #== get created? No clue. Hence this code. Note that I have no recollection
            #== of what the user_info_line or com_query_line contained, or what their
            #== purpose was in the code later on.
            
            call.hcs_.make_seg(dname, aname, "", 0, adminptr, code)
            if code.val == 0:
                #== This at least gives me access to 'admin mode' which in turn
                #== provides command (i.e., 'big-bang') for creating the universe
                #== database that the rest of the game depends on.
                admin_info.game_admin = "JRCooper"
                call.ioa_("Administrative matrix created.")
            # end if
            
            return
            
        # end if
        
        print "admin_info =", admin_info
        print adminptr.ptr.dumps()
        
        call.do(admin_info.user_info_line)
        call.do(admin_info.com_query_line)
        call.hcs_.initiate(get_pdir_(), "pit", "", 0, 0, pit_ptr, code)
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
        call.ioa_("^/Starrunners ^a", version)
        for x in do_range(1, admin_info.star_comn):
            if person == admin_info.star_coms[x-1]: access = "yes"
        # end for
        call.hcs_.initiate(dname, xname, "", 0, 0, univptr, code)
        # print univptr.ptr.dumps()
        if code.val != 0 and univptr.ptr == null():
            call.ioa_("^/I'm sorry, but the STARRUNNERS universe is closed.^/Please feel free to try later.  Thank you...")
            return
        # end if
        if universe.number == 10:
            call.ioa_("^/I'm sorry, but the STARRUNNERS universe is filled to maximum capacity.^/Please feel free to try later.  Thank you...")
            return
        # end if
        
    # /* ACCEPT/REFUSE NOTIFICATIONS.  PUT/TAKE ON/FROM LIST */
        for x in do_range(1, 50):
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
            for x in do_range(1, 50):
                if universe.notifications[x].person_id == "" and universe.notifications[x].project_id == "":
                    with universe:
                        universe.notifications[x].person_id = person
                        universe.notifications[x].project_id = project
                        return
                    # end with
                # end if
            # end for
        # end if
        if not on_the_list and accept_notifications: call.ioa_("^/Sorry, but the notifications list is full to maximum capacity...")
        if on_the_list: return
        
    # /* IF -list_players CONTROL_ARG WAS SUPPLIED, LIST PLAYERS, NO GAME */
        if list_players:
            call.ioa_("^/List of players: ^[none^]^[^d^]", (universe.number == 0), (universe.number > 0), universe.number)
            for x in do_range(1, universe.number):
                call.ioa_("^3x^a", universe.user[x])
            # end for
            return
        # end if
        
    # /* ASK HIM IF HE WANTS INSTRUCTIONS */
        while input.val == "":
            call.ioa_.nnl("^/Would you like instructions? ")
            getline(input)
            if input.val == "yes" or input.val == "y": call.print_(helpfile, "1")
            elif input.val != "no" and input.val != "n":
                call.ioa_("^/Please answer \"yes\" or \"no\".")
                input.val = ""
            # end if
        # end while
        
    # /* GET GAME PASSWORD (IF THERE IS ONE) */
        if universe.password != "":
            call.ioa_.nnl("^/Password: ")
            getline(input)
            if input.val != universe.password:
                call.ioa_("Incorrect password supplied.")
                call.ioa_("Please contact Starrunners Administrator for correct password.")
                return
            # end if
        # end if
        
    # /* SET finish TO TURN OFF NOTIFICATIONS */
        def begin_block():
            with univptr.ptr:
                for x in do_range(1, 50):
                    if universe.notifications[x].person_id == person and universe.notifications[x].project_id == project:
                        universe.notifications[x].person_id = ""
                        universe.notifications[x].project_id = ""
                    # end if
                # end for
            # end with
            continue_to_signal_(0)
        #-- end def begin_block
        
        with on_finish(begin_block):
        
    # /* SET quit AND seg_fault_error TO DESTROY SHIP/END GAME */
            with on_quit(game_over):
                with on_seg_fault_error(universe_destroyed):
                    try:
            
    # /* MAKE HIS SHIP */
                        pdir = get_pdir_()
                        call.hcs_.initiate(pdir, ename, "", 0, 0, my, code)
                        if my.ship != null(): call.hcs_.delentry_seg(my.ship, code)
                        call.hcs_.make_seg(pdir, ename, "", 0, my(ship), code)
                        my.ship.lock = my.ship.lock_word()
                        acl_entry = pdir + ">" + ename
                        call.set_acl(acl_entry, acl, whom)
                        call.hcs_.set_ring_brackets(pdir, ename, ring_brackets, code)
                        if code.val != 0:
                            call.com_err_(code.val, MAIN)
                            return
                        # end if
        
    # /* CLEAN OUT SHIP DATA FOR A FRESH START */
                        lock(my.ship.lock)
                        with my.ship:
                            my.ship.user = my.ship.name = my.ship.type = my.ship.condition = my.ship.message = my.ship.fromname = my.ship.fromtype = my.ship.deathmes = my.ship.deadname = my.ship.deadtype = my.ship.tracname = my.ship.monitored_by = my.ship.monloc = ""
                            my.ship.psi_name = [""] * (10+1)
                            my.ship.psi_type = [""] * (10+1)
                            my.ship.psi_mes = [""] * (10+1)
                            my.ship.monname = my.ship.montype = "#"
                            my.ship.location = "PHASING"
                            my.ship.black_hole = "start"
                            my.ship.energy_cur = my.ship.energy_old = my.ship.energy_max = my.ship.shields_cur = my.ship.shields_old = my.ship.shields_max = my.ship.torps_cur = my.ship.torps_old = my.ship.torps_max = my.ship.life_cur = my.ship.life_old = my.ship.psi_num = 0
                            my.ship.cloak_on = my.ship.tractor_on = my.ship.psionics = False
                            my.ship.unique_id = clock_()
                        # end with
                        unlock(my.ship.lock)
                        
    # /* ADD HIM TO LIST OF PLAYERS IN THE STARRUNNERS UNIVERSE */
                        if universe.number == 10:
                            call.ioa_("I'm sorry, but the STARRUNNERS universe if filled to maximum capacity.^/Please feel free to try later.  Thank you...")
                            return
                        # end if
                        lock(universe.lock)
                        with universe:
                            universe.number = universe.number + 1
                            universe.pdir[universe.number] = pdir
                            universe.unique_id[universe.number] = my.ship.unique_id
                            universe.user[universe.number] = person
                            if universe.number == 1:
                                universe.holes = 0
                                universe.black_hole = [""] * (5+1)
                                for i in do_range(1, 20):
                                    universe.robot[i].name = ""
                                    universe.robot[i].energy = 0
                                    universe.robot[i].location = ""
                                    universe.robot[i].condition = ""
                                    universe.robot[i].controller = "none"
                                # end for
                            # end if
                        # end with
                        unlock(universe.lock)
                        
                        # print univptr.ptr.dumps()
                        
    # /* RECORED THE USER'S PERSON_ID */
                        lock(my.ship.lock)
                        my.ship.user = person
                        unlock(my.ship.lock)
        
    # /* GET SHIP NAME */
                        input.val = ""
                        while input.val == "":
                            call.ioa_.nnl("^/Ship name: ")
                            getline(input)
                            if verify(input.val, allowed_chars) != 0:
                                call.ioa_("Invalid ship name: ^a", input.val)
                                input.val = ""
                            # end if
                            for x in range(universe.number):
                                edir = universe.pdir[x]
                                call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
                                if enemy.ptr != null() and edir != pdir and input.val == enemy.ship.name:
                                    call.ioa_("^/The name you have chosen is presently in use.^/Please choose a different name.")
                                    input.val = ""
                                # end if
                            # end for
                            if input.val != "": my.ship.name = input.val
                        # end while
                        
    # /* GET SHIP TYPE */
                        input.val = ""
                        while input.val == "":
                            call.ioa_.nnl("Ship type: ")
                            getline(input)
                            if input.val == "Destroyer" or input.val == "D": shiptype = "Destroyer"
                            elif input.val == "Cruiser" or input.val == "C": shiptype = "Cruiser"
                            elif input.val == "Starship" or input.val == "S": shiptype = "Starship"
                            elif input.val == "Star Commander" or input.val == "SC":
                                if access != "yes":
                                    call.ioa_("^/You do not have proper clearance for Star Command.^/")
                                    input.val = ""
                                else:
                                    password = parameter()
                                    codeword = parameter()
                                    call.ioa_()
                                    call.read_password_("Password: ", password)
                                    if len(password.val.strip()) < 3:
                                        call.ioa_("^a: Password must be at least 3 characters long.", MAIN)
                                        return
                                    # end if
                                    call.read_password_("Codeword:", codeword)
                                    if codeword.val != generate_codeword(password.val):
                                        call.ioa_("Star Command clearance check failed.^/")
                                        input.val = ""
                                    else: call.ioa_("^/You have been cleared for Star Command.")
                                    shiptype = "Star Commander"
                                # end if
                            else:
                                call.ioa_("That is not a standard ship type ---> use: Destroyer, Cruiser, or Starship.")
                                input.val = ""
                            # end if
                        # end while
                          
    # /* FINAL SET-UP PREPARATIONS */
                        make_ship(shiptype)
                        ship_status()
                        black_hole_check()
                        check_monitor()
                        send_notifications()
                        
                    except goto_end_of_game:
                        return
                    # end try
                # end with (on_seg_fault_error)
            # end with (on_quit)
        
    # /***** ENTER COMMAND LOOP ENVIRONMENT *****/
            with on_quit(command_seq_terminator):
                with on_seg_fault_error(universe_destroyed):
                    while (b'1'):
                        try:
                            update_condition()
                            input.val = ""
                            call.ioa_.nnl("^/COMMAND :> ")
                            timed_input(input)
                            security_check()
                            if input.val == "status" or input.val == "st": ship_status()
                            elif input.val == "lscan" or input.val == "ls": long_scan()
                            elif input.val == "sscan" or input.val == "ss": short_scan()
                            elif input.val == "thrust" or input.val == "th": move_ship()
                            elif input.val == "warpout" or input.val == "wp": warpout()
                            elif input.val == "missile" or input.val == "ms": launch_missile()
                            elif input.val == "lasers" or input.val == "lr": fire_lasers()
                            elif input.val == "contact" or input.val == "ct": contact_ship()
                            elif input.val == "dock" or input.val == "dk": dock()
                            elif input.val == "sdestruct" or input.val == "sd": self_destruct()
                            elif input.val == "deathray" or input.val == "dr": death_ray()
                            elif input.val == "*": game_over()
                            
                            elif input.val == ".": call.ioa_("^/^a ^a", MAIN, version)
                            elif my.ship.type == "Star Commander":
                                if input.val == "cloaking-device" or input.val == "cd": cloaking_device()
                                elif input.val == "nova-blast" or input.val == "nb": nova_blast()
                                elif input.val == "star-gate" or input.val == "sg": create_stargate()
                                elif input.val == "tractor-beam" or input.val == "tb": tractor_beam()
                                elif input.val == "tractor-pull" or input.val == "tp": tractor_pull()
                                elif input.val == "trojan-horse" or input.val == "tj": trojan_horse()
                                elif input.val == "computer" or input.val == "cm": computer()
                                elif input.val == "monitor" or input.val == "mn": monitor_ship()
                                elif input.val.startswith(":"): escape_to_multics()
                                elif input.val == "?":
                                    command_list()
                                    classified_com_list()
                                elif input.val != "":
                                    call.ioa_("^/*** COMPUTER:")
                                    call.ioa_("   That is not a standard ship command:")
                                    call.ioa_("   Type a \"?\" for a list of proper commands")
                                # end if
                            elif input.val == "?": command_list()
                            elif input.val != "":
                                call.ioa_("^/*** COMPUTER:")
                                call.ioa_("   That is not a standard ship command:")
                                call.ioa_("   Type a \"?\" for a list of proper commands")
                                input.val = ""
                            # end if
                            
                        # /* ENVIRONMENT CHECKING ROUTINES -- DAMAGE, MESSAGES, DEATHS, BLACK_HOLES, MONITOR, PSIONICS */
                            damage_check()
                            message_check()
                            death_check()
                            black_hole_check()
                            check_monitor()
                            psionics_check()
                            robot_functions()
                        
                        except goto_command_loop: # goto command_loop
                            continue
                            
                        except goto_end_of_game: # goto end_of_game
                            return
                            
                        # except DisconnectCondition: # on finish call universe_destroyed;
                            # try:
                                # universe_destroyed()
                            # finally:
                                # raise DisconnectCondition()
                            
                        except:
                            raise
                        # end try
                            
                    # end while
            
    #-- end procedure
    
    # /***** COMMAND ROUTINES *****/
    
    def ship_status():
        call.ioa_("^/Ship name: ^a", my.ship.name)
        call.ioa_("Ship type: ^a", my.ship.type)
        call.ioa_("---------------------")
        call.ioa_("Shield strength: ^d%", my.ship.shields_cur)
        call.ioa_("Missiles left: ^d", my.ship.torps_cur)
        call.ioa_("Energy left: ^du", my.ship.energy_cur)
        call.ioa_("Life support level: ^d", my.ship.life_cur)
        call.ioa_("---------------------")
        call.ioa_("Condition: ^a", my.ship.condition)
        call.ioa_("Current location: ^a", my.ship.location)
    #-- end def ship_status
    
    def long_scan():
        stars = [""] * (5+1)
        
        # print univptr.ptr.dumps()
        
        if my.ship.location == "Romula": stars[1] = "o"
        elif my.ship.location == "Vindicar": stars[2] = "o"
        elif my.ship.location == "Telgar": stars[3] = "o"
        elif my.ship.location == "Shadow": stars[4] = "o"
        else: stars[5] = "o"
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if not enemy.ship.cloak_on:
                    if enemy.ship.type == "Star Commander":
                        if enemy.ship.location == "Romula": stars[1] += "@"
                        elif enemy.ship.location == "Vindicar": stars[2] += "@"
                        elif enemy.ship.location == "Telgar": stars[3] += "@"
                        elif enemy.ship.location == "Shadow": stars[4] += "@"
                        else: stars[5] += "@"
                    else:
                        if enemy.ship.location == "Romula": stars[1] += "*"
                        elif enemy.ship.location == "Vindicar": stars[2] += "*"
                        elif enemy.ship.location == "Telgar": stars[3] += "*"
                        elif enemy.ship.location == "Shadow": stars[4] += "*"
                        else: stars[5] += "*"
                    # end if
                # end if
            # end if
        # end if
        call.ioa_("^/   ROMULA    VINDICAR     TELGAR    SHADOW      ZORK")
        call.ioa_("--------------------------------------------------------")
        call.ioa_("|          |          |          |          |          |")
        call.ioa_("|^a^12t|^a^23t|^a^34t|^a^45t|^a^56t|", stars[1], stars[2], stars[3], stars[4], stars[5])
        call.ioa_("|          |          |          |          |          |")
        call.ioa_("--------------------------------------------------------")
    #-- end def long_scan

    def short_scan():
        shipname   = [""] * (30+1)
        shiptype   = [""] * (30+1)
        docked     = [""] * (30+1)
        present    = fixed.bin . parm . init(0)
        # black_hole = False
        black_hole = bit(1) . init(b'0') ()
        
        call.ioa_("^/SECTOR: ^a", my.ship.location)
        for x in do_range(1, 5):
            if universe.black_hole[x] == my.ship.location: black_hole = b'1'
        # end for
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if not enemy.ship.cloak_on and enemy.ship.location == my.ship.location:
                    present.val = present.val + 1
                    shipname[present.val] = enemy.ship.name
                    shiptype[present.val] = enemy.ship.type
                    if enemy.ship.condition == "DOCKING": docked[present.val] = "(Docking)"
                    elif enemy.ship.condition == "SHIELDS DOWN": docked[present.val] = "(Shields Down)"
                # end if
            # end if
        # end for
        robot_sscan(present, shipname, shiptype, docked)
        if present.val == 0 and black_hole == b'0':
            call.ioa_("*** SENSOR SCAN: Sector Void")
            return
        # end if
        call.ioa_("*** SENSOR SCAN:")
        if black_hole == b'1': call.ioa_("(((BLACK HOLE)))")
        for x in do_range(1, present.val):
            call.ioa_("   ^a ^a ^a", shiptype[x], shipname[x], docked[x])
        # end for
    #-- end def short_scan
    
    def move_ship():
        open_sectors = [""] * (2+1)
        how_many     = 1
        input        = parm("")
        
        def hazard_check():
            x = (clock_() % 200) + 1
            course = "{0:06d}".format((clock_() % 99999) + 1)
            if x == 1: call.ioa_("^/ION STORM encountered on course ^a to ^a", course, input.val)
            elif x == 2: call.ioa_("^/ASTEROID BELT encountered on course ^a to ^a", course, input.val)
            if x < 3: hazard_damage()
        
        def hazard_damage():
            lock(my.ship.lock)
            with my.ship:
                x = (clock_() % 10) + 1
                my.ship.shields_cur = max(0, my.ship.shields_cur - x)
                my.ship.shields_old = max(0, my.ship.shields_old - x)
                x = (clock_() % 100) + 1
                my.ship.energy_cur = max(0, my.ship.energy_cur - x)
                my.ship.energy_old = max(0, my.ship.energy_old - x)
            # end with
            unlock(my.ship.lock)
        
        old_loc = my.ship.location;
        if my.ship.energy_cur < 10:
            call.ioa_("^/WE haven't got the energy to move, sir")
            return
        elif my.ship.tractor_on:
            call.ioa_("^/TRACTOR BEAM holding our ship, sir")
            return
        # end if
        if my.ship.location == "Romula": open_sectors[0] = "Vindicar"
        elif my.ship.location == "Vindicar":
            how_many = 2
            open_sectors[1] = "Romula"
            open_sectors[2] = "Telgar"
        elif my.ship.location == "Telgar":
            how_many = 2
            open_sectors[1] = "Vindicar"
            open_sectors[2] = "Shadow"
        elif my.ship.location == "Shadow":
            how_many = 2
            open_sectors[1] = "Telgar"
            open_sectors[2] = "Zork"
        else: open_sectors[1] = "Shadow"
        while input.val == "":
            if how_many == 1: call.ioa_("^/OPEN SECTOR is ^a, sir", open_sectors[1])
            else: call.ioa_("^/OPEN SECTORS are ^a and ^a, sir", open_sectors[1], open_sectors[2])
            call.ioa_.nnl("NAVIGATION :> ")
            timed_input(input)
            if input.val == "": return
            elif input.val == open_sectors[1] or input.val == open_sectors[2]:
                if input.val != "":
                    lock(my.ship.lock)
                    with my.ship:
                        my.ship.location = input.val
                        my.ship.energy_cur = my.ship.energy_cur - 10
                        my.ship.energy_old = my.ship.energy_old - 10
                    # end with
                    unlock(my.ship.lock)
                    call.ioa_("COURSE set for ^a, sir", input.val)
                    hazard_check()
                    inform_monitor(my.ship.location)
                    inform_psionics(old_loc, my.ship.location)
                # end if
            # end if
            else: input.val = ""
        # end while
    #-- end def move_ship
    
    def warpout():
        x       = 0
        old_loc = ""
        
        if my.ship.energy_cur < 100:
            call.ioa_("^/WE haven't got the energy to warpout, sir")
            return
        # end if
        if my.ship.tractor_on:
            call.ioa_("^/TRACTOR BEAM holding our ship, sir")
            return
        # end if
        old_loc = my.ship.location
        x = (clock_() % 1000) + 1
        if x > my.ship.energy_cur:
            call.ioa_("^/<<< BOOOOOOOOOOM >>>")
            call.ioa_("You have warped into a star")
            game_over()
        # end if
        lock(my.ship.lock)
        with my.ship:
            my.ship.location = rand_location()
            my.ship.energy_cur = my.ship.energy_cur - 100
            my.ship.energy_old = my.ship.energy_old - 100
        # end with
        unlock(my.ship.lock)
        call.ioa_("^/WARPOUT *****----------")
        call.ioa_("New location: ^a", my.ship.location)
        if old_loc != my.ship.location:
            inform_monitor(my.ship.location)
            inform_psionics(old_loc, my.ship.location)
        # end if
    #-- end def warpout
    
    def launch_missile():
        is_he_there = parm(False)
        hit         = parm(False)
        
        if my.ship.torps_cur == 0:
            call.ioa_("^/WE are out of missiles, sir")
            return
        # end if
        call.ioa_("^/MISSILE ready to launch, sir")
        call.ioa_.nnl("Target name: ")
        timed_input(input)
        if input.val == "": return;
        target.val = input.val
        verify_target(target.val, is_he_there)
        if not is_he_there.val:
            call.ioa_("*** SENSORS: Target ship ^a is not in this sector, sir", target.val)
            return
        # end if
        input.val = ""
        while input.val == "":
            call.ioa_.nnl("MISSILE locked on target, sir: ")
            timed_input(input)
            if input.val == "abort" or input.val == "ab":
                call.ioa_("LAUNCH aborted, sir")
                return
            elif input.val == "launch" or input.val == "l":
                lock(my.ship.lock)
                with my.ship:
                    my.ship.torps_cur = my.ship.torps_cur - 1
                    my.ship.torps_old = my.ship.torps_old - 1
                # end with
                unlock(my.ship.lock)
                call.ioa_("^/MISSILE launched, sir")
                hit_that_sucker(hit, "missile")
                if target.val == "critical": return
                if not hit.val:
                    call.ioa_("MISSILE missed, sir")
                    return
                else: call.ioa_("<< BOOM >> MISSILE hit, sir")
                inflict_damage()
                if target_is_a_robot(target.val): return
                if enemy.ship.psionics:
                    lock(enemy.ship.lock)
                    with enemy.ship:
                        enemy.ship.psi_mes[0] = "hit"
                        enemy.ship.psi_name[0] = my.ship.name
                        enemy.ship.psi_type[0] = my.ship.type
                    # end with
                    unlock(enemy.ship.lock)
                # end if
            else: input.val = ""
        # end while
    #-- end def launch_missile
    
    def fire_lasers():
        is_he_there = parm(False)
        hit         = parm(False)
        
        if my.ship.energy_cur < 10:
            call.ioa_("^/WE haven't got the energy to fire lasers, sir")
            return
        # end if
        call.ioa_("^/LASER banks ready to fire, sir")
        call.ioa_.nnl("Target name: ")
        timed_input(input)
        if input.val == "": return;
        target.val = input.val
        verify_target(target.val, is_he_there)
        if not is_he_there.val:
            call.ioa_("*** SENSORS: Target ship ^a is not in this sector, sir", target.val)
            return
        # end if
        input.val = ""
        while input.val == "":
            call.ioa_.nnl("LASER banks locked on target, sir: ")
            timed_input(input)
            if input.val == "deenergize" or input.val == "de":
                call.ioa_("LASER banks deenergizing, sir")
                return
            elif input.val == "fire" or input.val == "f":
                lock(my.ship.lock)
                with my.ship:
                    my.ship.energy_cur = my.ship.energy_cur - 10
                    my.ship.energy_old = my.ship.energy_old - 10
                # end with
                unlock(my.ship.lock)
                call.ioa_("^/LASERS fired, sir")
                hit_that_sucker(hit, "lasers")
                if target.val == "critical": return
                if not hit.val:
                    call.ioa_("LASERS missed, sir")
                    return
                else: call.ioa_("<< ZAP >> LASERS hit, sir")
                inflict_damage()
                if target_is_a_robot(target.val): return
                if enemy.ship.psionics:
                    lock(enemy.ship.lock)
                    with enemy.ship:
                        enemy.ship.psi_mes[0] = "hit"
                        enemy.ship.psi_name[0] = my.ship.name
                        enemy.ship.psi_type[0] = my.ship.type
                    # end with
                    unlock(enemy.ship.lock)
                # end if
            else: input.val = ""
        # end while
    #-- end def fire_lasers
    
    # /* TARGETTING -- HIT DETERMINATION AND CRITICAL HITS */
    
    def verify_target(verify_who, is_he_there):
        for x in range(universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null () and edir != pdir:
                if enemy.ship.location == my.ship.location and enemy.ship.name == verify_who:
                    is_he_there.val = True
                    return
                # end if
            # end if
        # end for
        robot_verify_target(verify_who, is_he_there)
    #-- end def verify_target
    
    def hit_that_sucker(hit, weapon):
        robot_was_the_target = parm(False)
        x                    = 0
        
        def critical_hit():
            if weapon != "plasma":
                call.ioa_("^/<<< BOOOOOOOOOOM >>>")
                call.ioa_("<<< BOOOOOOOOOOM >>>")
                call.ioa_("^/CRITICAL centers have been hit on the ^a ^a!", enemy.ship.type, enemy.ship.name)
            # end if
            lock (enemy.ship.lock)
            enemy.ship.deathmes = "bang"
            unlock(enemy.ship.lock)
        # /* SET THE TARGET TO "CRITICAL" SO THAT UPON RETURNING, CONTROL GOES CENTRAL */
            target.val = "critical"
        #-- end def critical_hit
        
        robot_hit_him(target, robot_was_the_target, weapon, hit)
        if robot_was_the_target.val: return
        if enemy.ship.type == "Star Commander":
            hit.val = False
            return
        # end if
        if weapon == "missile":
            x = (clock_() % 101) + 30
            if x > 125: critical_hit()
        else:
            x = (clock_() % 100) + 1
            if x == 100: critical_hit()
        # end if
        if x > enemy.ship.shields_cur: hit.val = True
        else: hit.val = False
    #-- end def hit_that_sucker
    
    def inflict_damage():
        d = parm(0)
        x = 0
        
        robot_damage(target.val, d)
        if d.val == 666: return
        lock(enemy.ship.lock)
        if enemy.ship.condition == "DOCKING" or enemy.ship.condition == "D-RAY" or enemy.ship.condition == "SHIELDS DOWN" or enemy.ship.condition == "DROBOT":
            enemy.ship.deathmes = "down"
            unlock(enemy.ship.lock)
            if my.ship.condition.find("ROBOT") == -1: call.ioa_("^/DEFLECTOR shields were down on the ^a ^a, sir", enemy.ship.type, enemy.ship.name)
            return
        # end if
        while x == 0:
            x = (clock_() % 4) + 1
            if x == 1:
                if enemy.ship.shields_cur == 0: x = 0
                else:
                    x = (clock_() % 10) + 1
                    enemy.ship.shields_cur = max(0, enemy.ship.shields_cur - x)
                    if my.ship.condition.find("ROBOT") == -1: call.ioa_("^/SHIELDS damaged on the ^a ^a, sir", enemy.ship.type, enemy.ship.name)
                # end if
            elif x == 2:
                if enemy.ship.energy_cur == 0: x = 0
                else:
                    x = (clock_() % 100) + 1
                    enemy.ship.energy_cur = max(0, enemy.ship.energy_cur - x)
                    if my.ship.condition.find("ROBOT") == -1: call.ioa_("^/ENGINES damaged on the ^a ^a, sir", enemy.ship.type, enemy.ship.name)
                # end if
            elif x == 3:
                if enemy.ship.torps_cur == 0: x = 0
                else:
                    x = (clock_() % 3) + 1
                    enemy.ship.torps_cur = max(0, enemy.ship.torps_cur - x)
                    if my.ship.condition.find("ROBOT") == -1: call.ioa_("^/MISSILES damaged on the ^a ^a, sir", enemy.ship.type, enemy.ship.name)
                # end if
            elif x == 4:
                if enemy.ship.life_cur == 0: x = 0
                else:
                    enemy.ship.life_cur = enemy.ship.life_cur - 1
                    if my.ship.condition.find("ROBOT") == -1: call.ioa_("^/LIFE SUPPORT systems damaged on the ^a ^a, sir", enemy.ship.type, enemy.ship.name)
                # end if
            # end if
        # end while
        unlock(enemy.ship.lock)
    #-- end def inflict_damage
    
    def contact_ship():
        x      = 0
        sendto = ""
          
        call.ioa_.nnl("^/WHO do you wish to contact, sir? ")
        timed_input(input)
        if input.val == "": return
        sendto = input.val
        if target_is_a_robot(sendto):
            call.ioa_("^/TRANSMISSIONS can not be sent to a RobotShip, sir")
            return
        # end if
        call.ioa_("WHAT is the message, sir?")
        call.ioa_.nnl("---: ")
        getline(input)
        if input.val == "":
            call.ioa_("MESSAGE not sent, sir")
            return
        # end if
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null () and edir != pdir:
                if enemy.ship.name == sendto:
                    lock(enemy.ship.lock)
                    with enemy.ship:
                        enemy.ship.fromname = my.ship.name
                        enemy.ship.fromtype = my.ship.type
                        enemy.ship.message = input.val
                    # end with
                    unlock(enemy.ship.lock)
                    call.ioa_("MESSAGE sent, sir")
                    return
                # end if
            # end if
        # end for
        call.ioa_("TRANSMISSIONS are not being accepted by a ship named ^a, sir", sendto)
    #-- end def contact_ship
    
    def dock():
        if my.ship.tracname != "": call.ioa_("^/** STARBASE ^a: Please deactivate your Tractor Beam", my.ship.location)
        if my.ship.cloak_on: call.ioa_("^/** STARBASE ^a: Please deactivate your Cloaking Device", my.ship.location)
        if my.ship.tracname != "" or my.ship.cloak_on: return
        call.ioa_("^/** Welcome to STARBASE ^a **", my.ship.location)
        if my.ship.shields_cur > 0: call.ioa_("SHIELDS will be lowered for docking")
        # on quit call ignore_signal;
        inform_monitor("docking")
        inform_psionics("docking", my.ship.location)
        lock(my.ship.lock)
        with my.ship:
            my.ship.condition = "DOCKING"
            my.ship.shields_cur = my.ship.shields_old = min(my.ship.shields_max, my.ship.shields_cur + 10)
            x = (clock_() % 3) + 1
            my.ship.torps_cur = my.ship.torps_old = min(my.ship.torps_max, my.ship.torps_cur + x)
            x = (clock_() % 41) + 10
            my.ship.energy_cur = my.ship.energy_old = min(my.ship.energy_max, my.ship.energy_cur + x)
            my.ship.life_cur = my.ship.life_old = min(10, my.ship.life_cur + 1)
        # end with
        unlock(my.ship.lock)
        for x in range(12): # Make docking take 6 seconds
            robot_functions()
            if my.ship.deathmes == "down": game_over()
            elif my.ship.deathmes == "bang": damage_check()
            call.timer_manager_.sleep(0.5, 0)
        # end for
        update_condition()
        call.ioa_("** DOCKING procedure completed.  Shields UP **")
    #-- end def dock
    
    def self_destruct():
    
        def share_the_misery():
            x      = 0
            damage = 0
        
            for x in do_range(1, universe.number):
                edir = universe.pdir[x]
                call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
                if enemy.ptr != null() and edir != pdir:
                    if enemy.ship.location == my.ship.location:
                        damage = (clock_() % 10) + 1
                        lock(enemy.ship.lock)
                        enemy.ship.shields_cur = max(0, enemy.ship.shields_cur - damage)
                        unlock(enemy.ship.lock)
                    # end if
                # end if
            # end for
            game_over()
        #-- end def share_the_misery
        
        call.ioa_.nnl("^/INITIATE self destruct sequence: ")
        timed_input(input)
        if input.val != "1a":
            call.ioa_("INCORRECT sequence password given :: sequence terminated")
            return
        # end if
        call.ioa_("SELF destruct sequence initiated ***")
        call.ioa_.nnl ("^/INITIATE sequence 2: ")
        timed_input(input)
        if input.val != "2b":
            call.ioa_("INCORRECT sequence password given :: sequence terminated")
            return
        # end if
        call.ioa_("SEQUENCE 2 initiated ***")
        call.ioa_.nnl ("^/INITIATE sequence 3: ")
        timed_input(input)
        if input.val != "3c":
            call.ioa_("INCORRECT sequence password given :: sequence terminated")
            return
        # end if
        call.ioa_("SEQUENCE 3 initiated ***")
        call.ioa_.nnl("^/SELF destruct command: ")
        timed_input(input)
        if input.val == "self-destruct" or input.val == "sd": share_the_misery()
        elif input.val == "abort" or input.val == "ab":
            call.ioa_("SELF destruct abort override command given :: sequence terminated")
            return
        else:
            call.ioa_("INCORRECT sequence password given :: sequence terminated")
            return
        # end if
    #-- end def self_destruct
    
    def death_ray():
        #== The Death Ray activation sequence is:
        #== > on: red switch
        #== > set dial to 55
        #== > on: grey switch
        #== > hit 1
        #== > hit 2
        #== > hit 3
        #== > off: grey switch
        #== > set dial to 0
        #== > off: red switch
        
        is_he_there              = parm(False)
        sequence_is_not_complete = True
        red_switch               = False
        grey_switch              = False
        one = two = three        = False
        activated                = False
        dial                     = 0
               
        def deduct_energy():
            lock(my.ship.lock)
            with my.ship:
                my.ship.energy_cur = my.ship.energy_cur - 500
                my.ship.energy_old = my.ship.energy_old - 500
            # end with
            unlock(my.ship.lock)
        #-- end def deduct_energy
            
        def DR_ERROR():
            call.ioa_("(DR) ERROR: Out-of-sequence on command -- sequence aborted")
            call.ioa_("^/SHIELDS raised")
            update_condition()
        #-- end def DR_ERROR
        
        if my.ship.energy_cur < 500:
            call.ioa_("^/WE haven't got the energy to fire the Death Ray, sir")
            return
        # end if
        call.ioa_("^/DEATH RAY sequence ready, sir")
        if my.ship.shields_cur > 0: call.ioa_("^/SHIELDS lowered")
        lock(my.ship.lock)
        my.ship.condition = "D-RAY"
        unlock(my.ship.lock)
        while sequence_is_not_complete:
            if my.ship.deathmes == "down": game_over()
            call.ioa_.nnl("> ")
            timed_input(input)
            if input.val == "on: red switch":
                if red_switch: call.ioa_("Red switch is already on.")
                else: red_switch = True
            elif input.val == "off: red switch":
                if not red_switch: call.ioa_("Red switch is not on.")
                elif activated:
                    if grey_switch or dial > 0: call.ioa_("Red switch is locked.")
                    else: sequence_is_not_complete = False
                elif dial > 0:
                    DR_ERROR()
                    return
                else: return
            elif input.val[:12] == "set dial to ":
                if verify(after(input.val, "to "), "1234567890") != 0: call.ioa_("(DR) ERROR: No such dial setting -- ^a", after(input.val, "to "))
                else:
                    x = int(after(input.val, "to "))
                    if x > 100: call.ioa_("(DR) ERROR: No such dial setting -- ^d", x)
                    elif x == 55 and not red_switch: call.ioa_("Dial is locked.")
                    elif x == 0 and grey_switch and activated:
                        DR_ERROR()
                        return
                    else: dial = x
                # end if
            elif input.val == "on: grey switch":
                if grey_switch: call.ioa_("Grey switch is already on.")
                elif dial != 55: call.ioa_("Grey switch is locked.")
                else: grey_switch = True
            elif input.val == "off: grey switch":
                if not grey_switch: call.ioa_("Grey switch is not on.")
                elif not activated and (one or two):
                    DR_ERROR()
                    return
                else: grey_switch = False
            elif input.val == "hit 1":
                if not grey_switch: call.ioa_("Control board is locked.")
                elif one: call.ioa_("[1] has already been hit.")
                else: one = True
            elif input.val == "hit 2":
                if not grey_switch: call.ioa_("Control board is locked.")
                elif not one:
                    DR_ERROR()
                    return
                elif two: call.ioa_("[2] has already been hit.")
                else: two = True
            elif input.val == "hit 3":
                if not grey_switch: call.ioa_("Control board is locked.")
                elif one and two:
                    call.ioa_("Security Override activated, sir")
                    activated = True
                else:
                    DR_ERROR()
                    return
                # end if
            elif input.val == "abort": return
            elif input.val != "": call.ioa_("(DR) ERROR: Unknown-drs-command -- \"^a\"", input.val)
        # end while
        call.ioa_("^/DEATH RAY energized, sir")
        call.ioa_.nnl("Target name: ")
        timed_input(input)
        if input.val == "":
            update_condition()
            return
        # end if
        target.val = input.val
        verify_target(target.val, is_he_there)
        if not is_he_there.val:
            call.ioa_("*** SENSORS: Target ship {0} is not in this sector, sir", target.val)
            call.ioa_("^/SHIELDS raised")
            update_condition()
            return
        # end if
        call.ioa_("DEATH RAY fired, sir")
        call.ioa_("^/SHIELDS raised")
        update_condition()
        if target_is_a_robot(target.val):
            x = (clock_() % 10) + 1
            if x > 1:
                deduct_energy()
                return
            else: robot_death(target.val)
        else:
            if enemy.ship.type == "Star Commander": return
            x = (clock_() % 10) + 1
            if x > 1:
                deduct_energy()
                return
            lock(enemy.ship.lock)
            with enemy.ship:
                enemy.ship.life_cur = 0
                if enemy.ship.condition == "DOCKING" or enemy.ship.condition == "D-RAY" or enemy.ship.condition == "SHIELDS DOWN" or enemy.ship.condition == "DROBOT": enemy.ship.deathmes = "down"
            # end with
            unlock(enemy.ship.lock)
        # end if
    #-- end def death_ray
    
    # /***** STAR COMMANDER COMMAND ROUTINES *****/

    def cloaking_device():
        if my.ship.energy_cur < 500:
            call.ioa_("^/WE haven't got the energy to activate the Cloaking Device, sir")
            return
        # end if
        if not my.ship.cloak_on:
            call.ioa_("^/CLOAKING DEVICE activated, sir")
            lock(my.ship.lock)
            with my.ship:
                my.ship.cloak_on = True
                my.ship.energy_cur = my.ship.energy_cur - 500
                my.ship.energy_old = my.ship.energy_old - 500
            # end with
            unlock(my.ship.lock)
            inform_monitor("vanished")
        else:
            input.val = ""
            call.ioa_("^/CLOAKING DEVICE is already activated, sir")
            while input.val == "":
                call.ioa_.nnl("Deactivate? ")
                timed_input(input)
                if input.val == "yes" or input.val == "y":
                    call.ioa_("CLOAKING DEVICE deactivated, sir")
                    lock(my.ship.lock)
                    my.ship.cloak_on = False
                    unlock(my.ship.lock)
                    return
                # end if
                if input.val != "no" and input.val != "n":
                    call.ioa_("^/Please type \"yes\" or \"no\".")
                    input.val = ""
                # end if
            # end while
        # end if
    #-- end def cloaking_device
     
    def nova_blast():
        is_he_there = parm(False)

        if my.ship.energy_cur < 100:
            call.ioa_("^/WE haven't got the energy to launch a Nova Blast, sir")
            return
        # end if
        call.ioa_("^/NOVA BLAST ready, sir")
        call.ioa_.nnl("Target name: ")
        timed_input(input)
        if input.val == "": return
        target.val = input.val
        verify_target(target.val, is_he_there)
        if not is_he_there.val:
            call.ioa_("*** SENSORS: Target ship ^a is not in this sector, sir", target.val)
            return
        # end if
        call.ioa_("NOVA BLAST launched, sir")
        if target_is_a_robot(target.val): robot_death(target.val)
        else:
            lock(enemy.ship.lock)
            with enemy.ship:
                enemy.ship.life_cur = 0
                if enemy.ship.condition == "DOCKING" or enemy.ship.condition == "D-RAY": enemy.ship.deathmes = "down"
            # end with
            unlock(enemy.ship.lock)
        # end if
        lock(my.ship.lock)
        with my.ship:
            my.ship.energy_cur = my.ship.energy_cur - 100
            my.ship.energy_old = my.ship.energy_old - 100
        # end with
        unlock(my.ship.lock)
    #-- end def nova_blast
    
    def create_stargate():
        old_loc = ""

        if my.ship.energy_cur < 1000:
            call.ioa_("^/WE haven't got the energy to create a Star Gate, sir ")
            return
        # end if
        old_loc = my.ship.location
        call.ioa_("^/STAR GATE opened, sir")
        input.val = ""
        while input.val == "":
            call.ioa_.nnl("Target sector: ")
            timed_input(input)
            if input.val == "": return
            elif input.val != "Romula" and input.val != "Vindicar" and input.val != "Telgar" and input.val != "Shadow" and input.val != "Zork": input.val = ""
        # end while
        lock(my.ship.lock)
        with my.ship:
            my.ship.location = input.val
            my.ship.energy_cur = my.ship.energy_cur - 1000
            my.ship.energy_old = my.ship.energy_old - 1000
        # end with
        unlock(my.ship.lock)
        call.ioa_("^/<< VOOM >>>>>>>>>>>>>>>>>>>>")
        call.ioa_("New location: ^a", my.ship.location)
        call.ioa_("^/STAR GATE closed, sir")
        if old_loc != my.ship.location:
            inform_monitor(my.ship.location)
            inform_psionics(old_loc, my.ship.location)
        # end if
    #-- end def create_stargate
     
    def tractor_beam():
        is_he_there = parm(False)
        
        if my.ship.energy_cur < 50:
            call.ioa_("^/WE haven't go the energy to activate the Tractor Beam, sir")
            return
        # end if
        if my.ship.tracname == "":
            call.ioa_("^/TRACTOR BEAM ready, sir")
            call.ioa_.nnl("Target name: ")
            timed_input(input)
            if input.val == "": return
            target.val = input.val
            verify_target(target.val, is_he_there)
            if not is_he_there.val:
                call.ioa_("*** SENSORS: Target ship ^a is not in this sector, sir", target.val)
                return
            # end if
            call.ioa_("TRACTOR BEAM activated, sir")
            lock(enemy.ship.lock)
            enemy.ship.tractor_on = True
            unlock(enemy.ship.lock)
            lock(my.ship.lock)
            with my.ship:
                my.ship.tracname = enemy.ship.name
                my.ship.energy_cur = my.ship.energy_cur - 50
                my.ship.energy_old = my.ship.energy_old - 50
            # end with
            unlock(my.ship.lock)
        # end if
        else:
            call.ioa_("^/TRACTOR BEAM is already activated, sir")
            input.val = ""
            while input.val == "":
                call.ioa_.nnl("Deactivate? ")
                timed_input(input)
                if input.val == "yes" or input.val == "y":
                    for x in do_range(1, universe.number):
                        edir = universe.pdir[x]
                        call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
                        if enemy.ptr != null() and edir != pdir and enemy.ship.name == my.ship.tracname:
                            lock(enemy.ship.lock)
                            enemy.ship.tractor_on = False
                            unlock(enemy.ship.lock)
                        # end if
                    # end for
                    lock(my.ship.lock)
                    my.ship.tracname = ""
                    unlock(my.ship.lock)
                    call.ioa_("TRACTOR BEAM deactivated, sir")
                elif input.val != "no" and input.val != "n":
                    call.ioa_("^/Please type \"yes\" or \"no\".")
                    input.val = ""
                # end if
            # end while
        # end if
    #-- end def tractor_beam
    
    def monitor_ship():
        is_he_there = parm(False)
        monitor_who = ""
        
        if my.ship.monname == "#":
            call.ioa_("^/MONITOR probe ready, sir")
            call.ioa_.nnl("Target name: ")
            timed_input(input)
            if input.val == "": return
            monitor_who = input.val
            verify_target(monitor_who, is_he_there)
            if not is_he_there.val:
                call.ioa_("*** SENSORS: Target ship ^a is not in this sector, sir", monitor_who)
                return
            # end if
            lock(enemy.ship.lock)
            enemy.ship.monitored_by = my.ship.name
            unlock(enemy.ship.lock)
            lock(my.ship.lock)
            with my.ship:
                my.ship.monname = enemy.ship.name
                my.ship.montype = enemy.ship.type
            # end with
            unlock(my.ship.lock)
            call.ioa_("MONITOR probe activated, sir")
            return
        # end if
        call.ioa_("^/MONITOR probe is already activated, sir")
        input.val = ""
        while input.val == "":
            call.ioa_.nnl("Deactivate? ")
            timed_input(input)
            if input.val == "yes" or input.val == "y":
                for x in do_range(1, universe.number):
                    edir = universe.pdir[x]
                    call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
                    if enemy.ptr != null() and edir != pdir:
                        if enemy.ship.name == my.ship.monname:
                            lock(enemy.ship.lock)
                            enemy.ship.monitored_by = ""
                            unlock(enemy.ship.lock)
                            lock(my.ship.lock)
                            with my.ship:
                                my.ship.monname = "#"
                                my.ship.montype = "#"
                                my.ship.monloc = ""
                            # end with
                            unlock(my.ship.lock)
                            call.ioa_("MONITOR probe deactivated, sir")
                        # end if
                    # end if
                # end for
            elif input.val != "no" and input.val != "n":
                call.ioa_("^/Please type \"yes\" or \"no\".")
                input.val = ""
            # end if
        # end while
    #-- end def monitor_ship
    
    def tractor_pull():
        if my.ship.tracname == "":
            call.ioa_("^/TRACTOR BEAM is not in operation, sir")
            return
        elif my.ship.energy_cur < 100:
            call.ioa_("^/WE haven't got the energy to pull the ship, sir")
            return
        # end if
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if my.ship.tracname == enemy.ship.name:
                    if my.ship.location == enemy.ship.location:
                        call.ioa_("^/The \"^a\" is already in ^a, sir", my.ship.tracname, enemy.ship.location)
                        return
                    # end if
                    lock(enemy.ship.lock)
                    enemy.ship.location = my.ship.location
                    if enemy.ship.deathmes == "": enemy.ship.deathmes = "pull"
                    unlock(enemy.ship.lock)
                    call.ioa_("^/TRACTOR BEAM pulling the \"^a\" into ^a, sir", my.ship.tracname, enemy.ship.location)
                    lock(my.ship.lock)
                    with my.ship:
                        my.ship.energy_cur = my.ship.energy_cur - 100
                        my.ship.energy_old = my.ship.energy_old - 100
                    # end with
                    unlock(my.ship.lock)
                    return
                # end if
            # end if
        # end of
    #-- end def tractor_pull

    def trojan_horse():
        victim = ""
        
        call.ioa_.nnl("^/WHO is to receive the Trojan Horse, sir? ")
        timed_input(input)
        if input.val == "": return
        victim = input.val
        call.ioa_("WHAT is the command, sir?")
        call.ioa_.nnl("---: ")
        timed_input(input)
        if input.val == "":
            call.ioa_("TROJAN HORSE not sent, sir")
            return
        # end if
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if enemy.ship.name == victim:
                    lock(enemy.ship.lock)
                    with enemy.ship:
                        enemy.ship.fromname = my.ship.name
                        enemy.ship.fromtype = "Trojan Horse"
                        enemy.ship.message = "TH:" + input.val
                    # end with
                    unlock(enemy.ship.lock)
                    call.ioa_("TROJAN HORSE sent, sir")
                    return
                # end if
            # end if
        # end for
        call.ioa_("TRANSMISSIONS are not being accepted by a ship named ^a, sir", victim)
    #-- end def trojan_horse
     
    # /* COMPUTER COMMAND ROUTINES */

    def computer():
        call.ioa_.nnl("^/*** COMPUTER ON ::: ")
        timed_input(input)
        if input.val == "": return
        elif input.val == "srunners" or input.val == "srs": list_all_players()
        elif input.val == "estatus" or input.val == "est": enemy_status()
        elif input.val == "probe" or input.val == "prb": probe()
        elif input.val == "bhreport" or input.val == "bhr": black_hole_report()
        elif input.val == "rsreport" or input.val == "rsr": robotship_report()
        elif input.val == "?": computer_com_list()
        else:
            call.ioa_("^/*** COMPUTER:")
            call.ioa_("   That is not a standard computer command:")
            call.ioa_("   Type \"?\" for a list of proper computer commands")
        # end if
    #-- end def computer
    
    def list_all_players():
        call.ioa_("^/Starrunners: ^d^/", universe.number)
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null():
                if enemy.ptr == my.ptr: call.ioa_(" * ^a: ^a ^a (^a)", my.ship.user, my.ship.type, my.ship.name, my.ship.location)
                elif enemy.ship.name == "" or enemy.ship.type == "": call.ioa_("   ^a: CREATING SHIP", enemy.ship.user)
                else: call.ioa_("   ^a: ^a ^a (^a)", enemy.ship.user, enemy.ship.type, enemy.ship.name, enemy.ship.location)
            # end if
        # end for
    #-- end def list_all_players
    
    def enemy_status():
        call.ioa_.nnl("^/STARFILE name: ")
        timed_input(input)
        if input.val == "": return
        shipfile = input.val
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if enemy.ship.name == shipfile and enemy.ship.location != "PHASING":
                    call.ioa_("^/::: STARFILE ^d :::", x + 1)
                    call.ioa_("^a ^a status:", enemy.ship.type, enemy.ship.name)
                    call.ioa_("^/Shield strength: ^d%^[   DOWN^]", enemy.ship.shields_cur, (enemy.ship.shields.cur == 0))
                    call.ioa_("Missiles left: ^d", enemy.ship.torps_cur)
                    call.ioa_("Energy left: ^du", enemy.ship.energy_cur)
                    call.ioa_("Life support level: ^d", enemy.ship.life_cur)
                    call.ioa_("Current location: ^a", enemy.ship.location)
                    return
                # end if
            # end if
        # end for
        call.ioa_("^/*** COMPUTER:")
        call.ioa_("   Unable to identify specified ship: ^a", shipfile)
    #-- end def enemy_status
    
    def probe():
        call.ioa_.nnl("^/*** PROBE ship: ")
        timed_input(input)
        if input.val == "": return
        probe_who = input.val
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if enemy.ship.name == probe_who and enemy.ship.location != "PHASING":
                    call.ioa_("*** PROBE sector: ^a", enemy.ship.location)
                    if enemy.ship.condition == "DOCKING": call.ioa_("^19tDOCKING")
                    elif enemy.ship.condition == "SHIELDS DOWN": call.ioa_("^19tSHIELDS DOWN")
                    if enemy.ship.tractor_on: call.ioa_("^19tTRACTOR BEAM HELD")
                    if enemy.ship.cloak_on: call.ioa_("^19tCLOAKING DEVICE ON")
                    return
                # end if
            # end if
        # end for
        call.ioa_("*** PROBE: Starfile on ^a could not be located", probe_who)
    #-- end def probe
    
    def black_hole_report():
        chart_mark = ["  "] * (5+1)
        
        for x in do_range(1, universe.holes):
            if universe.black_hole[x] == "Romula": chart_mark[1] = "()"
            elif universe.black_hole[x] == "Vindicar": chart_mark[2] = "()"
            elif universe.black_hole[x] == "Telgar": chart_mark[3] = "()"
            elif universe.black_hole[x] == "Shadow": chart_mark[4] = "()"
            elif universe.black_hole[x] == "Zork": chart_mark[5] = "()"
        # end for
        call.ioa_("^/ROMULA  VINDICAR  TELGAR  SHADOW  ZORK")
        call.ioa_("------  --------  ------  ------  ----")
        call.ioa_("  ^2a^7x^2a^7x^2a^6x^2a^5x^2a", chart_mark[1], chart_mark[2], chart_mark[3], chart_mark[4], chart_mark[5])
    #-- end def black_hole_report

    def robotship_report():
        call.ioa_("^/RobotShip Report:")
        for x in do_range(1, 20):
            if universe.robot[x].location != "": call.ioa_("^3xRobotShip ^a (^a) ^a", universe.robot[x].name, universe.robot[x].location, universe.robot[x].condition)
        # end for
    #-- end def robotship_report
    
    def escape_to_multics():
        command = after(input.val, ":")
        call.do(command)
    #-- end def escape_to_multics
    
    def inform_routines():
        ten_seconds = 10
        # on seg_fault_error call universe_destroyed;
        damage_check()
        message_check()
        death_check()
        black_hole_check()
        check_monitor()
        psionics_check()
        robot_functions()
        call.timer_manager_.alarm_call(ten_seconds, inform_routines)
    #-- end def inform_routines
    
    # /***** ARMEGEDDON ROUTINES -- TRASH HIS SHIP, GOODBYE CRUEL UNIVERSE *****/
    
    def game_over():
    
        def update_universe():
            robot_release(my.ship.user)
            lock(universe.lock)
            with universe:
                for x in do_range(1, universe.number):
                    if universe.pdir[x] == pdir:
                        for y in do_range(x, universe.number):
                            universe.pdir[y] = universe.pdir[y + 1]
                            universe.user[y] = universe.user [y + 1]
                            universe.unique_id[y] = universe.unique_id[y + 1]
                        # end for
                        universe.pdir[universe.number] = ""
                        universe.user[universe.number] = ""
                        universe.unique_id[universe.number] = 0
                        universe.number = universe.number - 1
                    # end if
                # end for
            # end with
            unlock(universe.lock)
            call.hcs_.delentry_seg(my.ship, code)
            call.ioa_("^/<<< YOU HAVE BEEN VAPORIZED >>>")
            call.ioa_("^/Thank you for playing STARRUNNERS.")
            raise goto_end_of_game
        #-- end def update_universe

        call.timer_manager_.reset_alarm_call(inform_routines)
        if input.val == "*": update_universe()
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir and enemy.ship.name != "" and enemy.ship.type != "" and (my.ship.type == "Starship" or my.ship.type == "Cruiser" or my.ship.type == "Destroyer" or (my.ship.type == "Star Commander" and my.ship.life_cur == 0)):
                lock(enemy.ship.lock)
                with enemy.ship:
                    enemy.ship.deathmes = "dead"
                    enemy.ship.deadname = my.ship.name
                    enemy.ship.deadtype = my.ship.type
                    if my.ship.tracname == enemy.ship.name: enemy.ship.tractor_on = False
                    if enemy.ship.tracname == my.ship.name: enemy.ship.tracname = ""
                    if my.ship.monname == enemy.ship.name: enemy.ship.monitored_by = ""
                # end with
                unlock(enemy.ship.lock)
            # end if
        # end for
        update_universe()
    #-- end def game_over
    
    def universe_destroyed():
        univptr = null()
        call.hcs_.initiate(dname, xname, "", 0, 0, univptr, code)
        if code.val != 0 and univptr == null():
            call.ioa_("^/*** GALACTIC IMPLOSION IMMINENT ***^/Alas, the universe has been destroyed...")
            raise goto_end_of_game
        # end if
        call.ioa_("^/*** SENSORS: Enemy ship is gone, sir")
        enemy = null()
        # goto command_loop;
    #-- end def universe_destroyed
    
    # /***** INFORMING ROUTINES *****/
    
    def inform_monitor(info):
        if my.ship.monitored_by == "": return
        for x in do_range(universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if enemy.ship.name == my.ship.monitored_by:
                    lock(enemy.ship.lock)
                    enemy.ship.monloc = info
                    unlock(enemy.ship.lock)
                # end if
            # end if
        # end for
        if info == "vanished":
            lock(my.ship.lock)
            my.ship.monitored_by = ""
            unlock(my.ship.lock)
        # end if
    #-- end def inform_monitor
     
    def inform_psionics(old_loc, new_loc):
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and edir != pdir and enemy.ship.psionics:
                if old_loc == enemy.ship.location or new_loc == enemy.ship.location or old_loc == "docking":
                    lock(enemy.ship.lock)
                    with enemy.ship:
                        enemy.ship.psi_num = y = enemy.ship.psi_num + 1
                        enemy.ship.psi_name[y] = my.ship.name
                        enemy.ship.psi_type[y] = my.ship.type
                        if old_loc == enemy.ship.location: enemy.ship.psi_mes[y] = "left"
                        elif old_loc == "docking": enemy.ship.psi_mes[y] = new_loc
                        elif new_loc == enemy.ship.location: enemy.ship.psi_mes[y] = "entered"
                    # end with
                    unlock(enemy.ship.lock)
                # end if
            # end if
        # end for
    #-- end def inform_psionics

    def command_list():
        call.ioa_("^/Commands:")
        call.ioa_("   (ss) sscan ------------ Short range scan")
        call.ioa_("   (ls) lscan ------------ Long range scan")
        call.ioa_("   (st) status ----------- Ship status")
        call.ioa_("   (th) thrust ----------- Move ship to an adjacent sector")
        call.ioa_("   (wp) warpout ---------- Hyperspace jump to a random sector")
        call.ioa_("   (ms) missile ---------- Missile attck")
        call.ioa_("   (lr) lasers ----------- Laser attack")
        call.ioa_("   (ct) contact ---------- Communication with another ship")
        call.ioa_("   (sd) sdestruct -------- Self destruct")
        call.ioa_("   (dr) deathray --------- Fire Death Ray")
        call.ioa_("   (dk) dock ------------- Dock at sector-starbase")
        call.ioa_("        * ---------------- Quit from game (Ship explodes)")
    #-- end def command_list
     
    def classified_com_list():
        call.ioa_("^/Classified commands:")
        call.ioa_("   (nb) nova-blast ------- Instantly destroys any ship")
        call.ioa_("   (cm) computer --------- Accesses classified computer files")
        call.ioa_("   (tb) tractor-beam ----- Tractor beam")
        call.ioa_("   (tp) tractor-pull ----- Pull ship into sector")
        call.ioa_("   (sg) star-gate -------- Star gate creation")
        call.ioa_("   (cd) cloaking-device -- Cloaking device")
        call.ioa_("   (mn) monitor ---------- Monitor ship")
        call.ioa_("   (tj) trojan-horse ----- Send trojan horse command")
    #-- end def classified_com_list
     
    def computer_com_list():
        call.ioa_("^/Computer commands:")
        call.ioa_("   (srs) srunners -------- Player listing")
        call.ioa_("   (est) estatus --------- Enemy ship status")
        call.ioa_("   (prb) probe ----------- Probe for ship")
        call.ioa_("   (bhr) bhreport -------- Black hole report")
        call.ioa_("   (rsr) rsreport -------- RobotShip report")
    #-- end def computer_com_list
    
    # /***** ENVIRONMENT CHECKING ROUTINES *****/
    
    def damage_check():
        if my.ship.deathmes == "bang":
            call.ioa_("^/*** RED ALERT ***")
            call.ioa_("*** RED ALERT ***")
            call.ioa_("^/CRITICAL centers have been hit, sir!!!")
            game_over()
        elif my.ship.deathmes == "pull":
            call.ioa_("^/TRACTOR BEAM has pulled our ship into ^a, sir", my.ship.location)
            my.ship.deathmes = ""
        # end if
        if my.ship.life_cur == 0: game_over()
        elif my.ship.deathmes == "down": game_over()
        lock(my.ship.lock)
        with my.ship:
            if my.ship.shields_cur != my.ship.shields_old:
                call.ioa_("^/<<< FOOOOOOOOOOM >>> SHIELDS have been hit, sir")
                call.ioa_("Shield strength has been reduced to ^d%", my.ship.shields_cur)
                # lock (my.ship.lock)
                my.ship.shields_old = my.ship.shields_cur
                # unlock (my.ship.lock)
            # end if
            if my.ship.energy_cur != my.ship.energy_old:
                call.ioa_("^/<<< FOOOOOOOOOOM >>> ENGINES have been hit, sir")
                call.ioa_("Energy remaining: ^du", my.ship.energy_cur)
                # lock (my.ship.lock)
                my.ship.energy_old = my.ship.energy_cur
                # unlock (my.ship.lock)
            # end if
            if my.ship.torps_cur != my.ship.torps_old:
                call.ioa_("^/<<< FOOOOOOOOOOM >>> MISSILES have been hit, sir")
                call.ioa_("Missiles remaining: ^d", my.ship.torps_cur)
                # lock (my.ship.lock)
                my.ship.torps_old = my.ship.torps_cur
                # unlock (my.ship.lock)
            # end if
            if my.ship.life_cur != my.ship.life_old:
                call.ioa_("^/<<< FOOOOOOOOOOM >>> LIFE SUPPORT systems have been hit, sir")
                call.ioa_("Life support level: ^d", my.ship.life_cur)
                # lock (my.ship.lock)
                my.ship.life_old = my.ship.life_cur
                # unlock (my.ship.lock)
            # end if
            if my.ship.psi_mes[0] == "hit":
                call.ioa_("^/PSIONICS: We have just been attacked by the ^a ^a, sir", my.ship.psi_type[0], my.ship.psi_name[0])
                # lock (my.ship.lock)
                my.ship.psi_mes[0] = my.ship.psi_name[0] = my.ship.psi_type[0] = ""
                # unlock (my.ship.lock)
            # end if
        # end with
        unlock(my.ship.lock)
    #-- end def damage_check
    
    def message_check():
        if my.ship.message == "": return
        if my.ship.message[:3] == "TH:" and my.ship.fromtype == "Trojan Horse":
            if my.ship.type == "Star Commander": call.ioa_("^/COMMUNICATIONS: We've trapped a Trojan Horse from the Star Commander ^a^/^16x(^a)", my.ship.fromname, my.ship.message[3:])
            else: call.do(my.ship.message[3:])
            lock(my.ship.lock)
            with my.ship:
                my.ship.fromname = my.ship.fromtype = my.ship.messge = ""
            # end with
            unlock(my.ship.lock)
            return
        # end if
        call.ioa_("^/COMMUNICATIONS: New transmission from the ^a ^a, sir", my.ship.fromtype, my.ship.fromname)
        call.ioa_("It says: ^a", my.ship.message)
        lock(my.ship.lock)
        with my.ship:
            my.ship.message = my.ship.fromname = my.ship.fromtype = ""
        # end with
        unlock(my.ship.lock)
    #-- end def message_check
    
    def death_check():
        if my.ship.deathmes != "dead": return
        call.ioa_("^/  <<< BOOOOOM >>>")
        call.ioa_("<<<<< BOOOOOM >>>>>")
        call.ioa_("  <<< BOOOOOM >>>")
        call.ioa_("^/SENSORS are picking up metallic debris from the ^a ^a, sir", my.ship.deadtype, my.ship.deadname)
        if my.ship.deadname == my.ship.monname:
            lock(my.ship.lock)
            with my.ship:
                my.ship.monloc = ""
                my.ship.monname = my.ship.montype = "#"
            # end with
            unlock(my.ship.lock)
            call.ioa_("^/MONITOR probe lost, sir")
        # end if
        lock(my.ship.lock)
        with my.ship:
            my.ship.deathmes = my.ship.deadname = my.ship.deadtype = ""
        # end with
        unlock(my.ship.lock)
    #-- end def death_check
    
    def check_monitor():
        if my.ship.monloc == "": return
        if my.ship.monloc == "docking": call.ioa_("^/*** MONITOR: ^a ^a has just docked", my.ship.montype, my.ship.monname)
        elif my.ship.monloc == "vanished":
            call.ioa_("^/*** MONITOR: Probe lost on ^a ^a", my.ship.montype, my.ship.monname)
            lock(my.ship.lock)
            with my.ship:
                my.ship.monname = my.ship.montype = my.ship.monloc = ""
            # end with
            unlock(my.ship.lock)
        else: call.ioa_("^/*** MONITOR: ^a ^a is now in ^a", my.ship.montype, my.ship.monname, my.ship.monloc)
        lock(my.ship.lock)
        my.ship.monloc = ""
        unlock(my.ship.lock)
    #-- end def check_monitor
    
    def psionics_check():
        if my.ship.psi_num > 0:
            if my.ship.psi_mes[1] != "left" and my.ship.psi_mes[1] != "entered": call.ioa_("^/PSIONICS: The ^a ^a has just docked at ^a, sir", my.ship.psi_type[1], my.ship.psi_name[1], my.ship.psi_mes[1])
            else: call.ioa_("^/PSIONICS: The ^a ^a has just ^a our sector, sir", my.ship.psi_type[1], my.ship.psi_name[1], my.ship.psi_mes[1])
            for x in do_range(2, my.ship.psi_num):
                if my.ship.psi_mes[x] != "left" and my.ship.psi_mes[x] != "entered": call.ioa_("^10xThe ^a ^a has just docked at ^a, sir", my.ship.psi_type[x], my.ship.psi_name[x], my.ship.psi_mes[x])
                else: call.ioa_("^10xThe ^a ^a has just ^a our sector, sir", my.ship.psi_type[x], my.ship.psi_name[x], my.ship.psi_mes[x])
            # end for
            lock(my.ship.lock)
            with my.ship:
                my.ship.psi_name = [""] * (10+1)
                my.ship.psi_type = [""] * (10+1)
                my.ship.psi_mes = [""] * (10+1)
                my.ship.psi_num = 0
            # end with
            unlock(my.ship.lock)
        # end if
        
        if my.ship.psionics: return
        
        x = (clock_() % 2000) + 1
        if x > 1: return
        call.ioa_("^/=== STAR FLEET COMMAND ===")
        call.ioa_("^/=== Transmission to: ^a ^a", my.ship.type, my.ship.name)
        call.ioa_("=== You have been entrusted with our newest secret weapon: Psionics! ===")
        call.ioa_("=== Prepare to matter-transmit him aboard your ship. Congratulations ===")
        call.ioa_("^/MATTER-TRANSMITTER ready for boarding, sir")
        call.ioa_(">>>Energizeeeeeeeeeeeeeeeeeeeeeeeeeeeee...")
        call.ioa_("PSIONIC board ship, sir")
        lock(my.ship.lock)
        my.ship.psionics = True
        unlock(my.ship.lock)
    #-- end def psionics_check

    # /***** BLACK HOLE ROUTINES *****/
    
    def black_hole_check():
        black_hole_init()
        new_black_hole()
        rand_new_hole()
        suck_him_in()
    #-- end def black_hole_check
    
    def black_hole_init():
        hole_here = False

        if my.ship.black_hole != "start": return
        lock(my.ship.lock)
        my.ship.black_hole = ""
        unlock(my.ship.lock)
        for x in do_range(1, universe.holes):
            if universe.black_hole[x] == my.ship.location: hole_here = True
        # end for
        if hole_here:
            call.ioa_("^/*** RED ALERT ***")
            call.ioa_("^/SENSORS indicate that we have just phased into a black hole sector, sir!")
            if my.ship.type != "Star Commander": pulling_damage()
        # end if
        if universe.holes == 1 and hole_here: return
        elif universe.holes > 0:
            call.ioa_("^/*** YELLOW ALERT ***")
            call.ioa_("^/SENSORS indicate black holes are present in the following sectors:")
        # end if
        for x in do_range(1, universe.holes):
            call.ioa_("   ^a", universe.black_hole[x])
        # end for
    #-- end def black_hole_init
    
    def new_black_hole():
        if my.ship.black_hole == "": return
        if my.ship.black_hole == my.ship.location:
            call.ioa_("^/*** RED ALERT ***")
            call.ioa_("^/SENSORS indicate that a black hole has just developed in our sector, sir!")
            if my.ship.type != "Star Commander": pulling_damage()
            lock(my.ship.lock)
            my.ship.black_hole = ""
            unlock(my.ship.lock)
        # end if
    #-- end def new_black_hole
    
    def rand_new_hole():
        new_hole = ""

        x = (clock_() % 1000) + 1
        if x > 1: return
        new_hole = rand_location()
        for x in do_range(1, universe.holes):
            if universe.black_hole[x] == new_hole: return
        # end for
        lock(universe.lock)
        universe.holes = universe.holes + 1
        universe.black_hole[universe.holes] = new_hole
        unlock(universe.lock)
        for x in do_range(1, universe.holes):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null ():
                lock(enemy.ship.lock)
                enemy.ship.black_hole = new_hole
                unlock(enemy.ship.lock)
            # end if
        # end for
    #-- end def rand_new_hole
    
    def pulling_damage():
        lock(my.ship.lock)
        with my.ship:
            my.ship.energy_cur = max(0, my.ship.energy_cur - 100)
            my.ship.energy_old = max(0, my.ship.energy_old - 100)
            my.ship.life_cur = max(0, my.ship.life_cur - 3)
            my.ship.life_old = max(0, my.ship.life_old - 3)
            my.ship.shields_cur = max(0, my.ship.shields_cur - 10)
            my.ship.shields_old = max(0, my.ship.shields_old - 10)
        # end with
        unlock(my.ship.lock)
        call.ioa_("^/*** ENGINEERING: Sir, our engines have taken heavy damages!")
        call.ioa_("*** MEDICAL: Sir, heavy casualties reported in all stations!")
        call.ioa_("*** CONTROL: Sir, our shields have taken heavy damages!")
    #-- end def pulling_damage

    def suck_him_in():
        hole_here = False
        
        for x in do_range(1, universe.holes):
            if universe.black_hole[x] == my.ship.location: hole_here = True
        # end if
        if not hole_here: return
        x = (clock_() % 500) + 1
        if x > my.ship.energy_cur:
            call.ioa_("^/BLACK HOLE is pulling our ship in, sir!")
            call.ioa_("^/IMPULSE engines activated, sir")
            call.timer_manager_.sleep(2.5, 0)
            x = (clock_() % 4) + 1
            if x > 1: game_over()
            call.ioa_("ESCAPE successful, sir")
        # endif
    #-- end def suck_him_in
    
    # /***** ROBOT INTERNALS *****/
    
    def robot_sscan(present, shipname, shiptype, docked):
        for x in do_range(1, 20):
            if my.ship.location == universe.robot[x].location:
                present.val = present.val + 1
                shipname[present.val] = universe.robot[x].name
                shiptype[present.val] = "RobotShip"
                if universe.robot[x].condition == "DOCKING": docked[present.val] = "(Docking)"
            # end if
        # end for
    #-- end def robot_scan
    
    def robot_verify_target(verify_who, is_he_there):
        for x in do_range(1, 20):
            if (my.ship.location == universe.robot[x].location) and (verify_who == universe.robot[x].name): is_he_there.val = True
        # end for
    #-- end def robot_verify_target
    
    def robot_hit_him(target_parm, robot_was_the_target, weapon, hit):
        if target_is_a_robot(target_parm.val): robot_was_the_target.val = True
        if weapon == "missile": x = (clock_() % 1601) + 400
        else: x = (clock_() % 1600) + 1
        if (x > 1538 and weapon == "lasers") or (x > 1923 and weapon == "missile"):
            call.ioa_("^/<<< BOOOOOOOOOOM >>>")
            call.ioa_("<<< BOOOOOOOOOOM >>>")
            call.ioa_("^/CRITICAL centers have been hit on the RobotShip ^a!", target_parm.val)
            robot_death(target_parm.val)
            target_parm.val = "critical"
            return
        elif x > universe.robot[robot_index(target_parm.val)].energy: hit.val = True
        else: hit.val = False
    #-- end def robot_hit_him
    
    def robot_damage(which_robot, x):
        if not target_is_a_robot(which_robot): return
        if universe.robot[robot_index(which_robot)].condition == "DOCKING":
            robot_death(which_robot)
            call.ioa_("^/FORCE FIELDS were down on the RobotShip ^a, sir", which_robot)
            x.val = 666
            return
        # end if
        x.val = (clock_() % 100) + 1
        lock(universe.lock)
        with universe:
            universe.robot[robot_index(which_robot)].energy = max(universe.robot[robot_index(which_robot)].energy - x.val, 0)
        # end with
        unlock(universe.lock)
        call.ioa_("^/ENERGY reduced on the RobotShip ^a", which_robot)
        if universe.robot[robot_index(which_robot)].energy == 0: robot_death(which_robot)
        x.val = 666
    #-- end def robot_damage
    
    def robot_death(which_robot):
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null() and enemy.ship.name != "" and enemy.ship.type != "":
                lock(enemy.ship.lock)
                with enemy.ship:
                    enemy.ship.deathmes = "dead"
                    enemy.ship.deadname = universe.robot[robot_index(which_robot)].name
                    enemy.ship.deadtype = "RobotShip"
                # end with
                unlock(enemy.ship.lock)
            # end if
        # end for
        lock(universe.lock)
        with universe:
            universe.robot[robot_index(which_robot)].location = ""
            universe.robot[robot_index(which_robot)].controller = "dead"
        # end with
        unlock(universe.lock)
    #-- end def robot_death
    
    def robot_release(control):
        for x in do_range(1, 20):
            if universe.robot[x].controller == control:
                lock(universe.lock)
                with universe:
                    universe.robot[x].controller = "free"
                # end with
                unlock(universe.lock)
            # end if
        # end for
    #-- end def robot_release
    
    def target_is_a_robot(target_string):
        if target_string[:2] == "R\\": return True
        return False
    #-- end def target_is_a_robot
    
    def robot_index(which_robot):
        for x in do_range(1, 20):
            if universe.robot[x].name == which_robot: return x
        # end for
        return 0
    #-- end def robot_index
    
    def robot_num():
        count = 0
        for x in do_range(1, 20):
            if universe.robot[x].controller != "none" and universe.robot[x].controller != "dead": count = count + 1
        # end for
        return count
    #-- end def robot_num
    
    # /***** ROBOT CONTROL FUNCTIONS *****/
    
    def robot_functions():
        
        def rand_new_robot():
            dead_count = 0
            
            x = (clock_() % max(robot_num() * 200, 1)) + 1
            if x > 1: return
            for x in do_range(1, 20):
                if universe.robot[x].controller == "none":
                    lock(universe.lock)
                    with universe:
                        universe.robot[x].name = "R\\{0:03d}".format(x)
                        universe.robot[x].energy = 1000
                        universe.robot[x].location = rand_location()
                        universe.robot[x].controller = my.ship.user
                    # end with
                    unlock(universe.lock)
                    return
                # end if
                if universe.robot[x].controller == "dead": dead_count = dead_count + 1
            # end for
            if dead_count < 20: return
            lock(universe.lock)
            with universe:
                for i in do_range(1, 20):
                    universe.robot[i].controller = "none"
                # end for
            # end with
            unlock(universe.lock)
        #-- end def rand_new_robot
        
        def take_free_robot():
            for x in do_range(1, 20):
                if universe.robot[x].controller == "free":
                    lock(universe.lock)
                    with universe:
                        universe.robot[x].controller = my.ship.user
                    # end with
                    unlock(universe.lock)
                # end if
            # end for
        #-- end def take_free_robot
        
        def hack_robot_actions():
            global ROBOT
            
            action = parm("")
            
            def look_for_targets(action):
                if universe.robot[robot_index(ROBOT)].condition == "DOCKING": return
                for x in do_range(1, universe.number):
                    edir = universe.pdir[x]
                    call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
                    if enemy.ptr != null() and enemy.ship.location == universe.robot[robot_index(ROBOT)].location:
                        action.val = "fire"
                        return
                    # end if
                # end for
            #-- end def look_for_targets
            
            def health_check(action):
                if universe.robot[robot_index(ROBOT)].energy < 200: action.val = "dock"
                elif universe.robot[robot_index(ROBOT)].condition == "DOCKING": action.val = "dock"
            #-- end def health_check
            
            def move_or_contact(action):
                x = (clock_() % 10) + 1
                if x < 3: return
                elif x == 3: action.val = "cont"
                else: action.val = "move"
            #-- end def move_or_contact
            
            def robot_fire():
                count = 0
                tptr  = [null()] * (10+1)
                hit   = parm(False)
                  
                while True:
                    for x in do_range(1, universe.number):
                        edir = universe.pdir[x]
                        call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
                        if enemy.ptr != null() and enemy.ship.location == universe.robot[robot_index(ROBOT)].location:
                            count = count + 1
                            tptr[count] = enemy.ptr
                        # end if
                    # end for
                    if count == 0: return
                    who = (clock_() % count) + 1
                    enemy.ptr = tptr[who]
                    if enemy.ptr != null(): break
                # end while
                target.val = ""
                lock(my.ship.lock)
                if my.ship.condition == "D-RAY" or my.ship.condition == "DOCKING": my.ship.condition = "DROBOT"
                else: my.ship.condition = "ROBOT"
                unlock(my.ship.lock)
                try:
                    # on seg_fault_error call ignore_signal_2;
                    hit_that_sucker(hit, "plasma")
                    if hit.val: inflict_damage()
                    lock(universe.lock)
                    with universe:
                        universe.robot[robot_index(ROBOT)].energy = max (0, universe.robot[robot_index(ROBOT)].energy - 10)
                    # end with
                    unlock(universe.lock)
                except SegmentFault:
                    raise goto_command_loop
                # end try
                # on seg_fault_error call universe_destroyed;
                update_condition()
                  
                # ignore_signal_2: procedure;

            # /* PROCEDURE FOR IGNORIG SEG_FAULT_ERRORS DURING ROBOT ATTACKS */

                      # goto command_loop;
                      
                # end ignore_signal_2;
            
            #-- end def robot_fire
         
            def robot_dock():
                if universe.robot[robot_index(ROBOT)].condition == "DOCKING":
                    x = (clock_() % 3) + 1
                    if x == 1:
                        lock(universe.lock)
                        with universe:
                            universe.robot[robot_index(ROBOT)].condition = ""
                        # end with
                        unlock(universe.lock)
                    # end if
                    return
                # end if
                x = (clock_() % 100) + 1
                lock(universe.lock)
                with universe:
                    universe.robot[robot_index(ROBOT)].energy = min(0, universe.robot[robot_index(ROBOT)].energy + x)
                    universe.robot[robot_index(ROBOT)].condition = "DOCKING"
                # end with
                unlock(universe.lock)
            #-- end def robot_dock
         
            def robot_move():
                open_sectors = [""] * (2+1)
                x            = 0
                
                if universe.robot[robot_index(ROBOT)].location == "Romula":
                    open_sectors[1] = "Vindicar"
                    x = 1
                elif universe.robot[robot_index(ROBOT)].location == "Vindicar":
                    open_sectors[1] = "Romula"
                    open_sectors[2] = "Telgar"
                elif universe.robot[robot_index(ROBOT)].location == "Telgar":
                    open_sectors[1] = "Vindicar"
                    open_sectors[2] = "Shadow"
                elif universe.robot[robot_index(ROBOT)].location == "Shadow":
                    open_sectors[1] = "Telgar"
                    open_sectors[2] = "Zork"
                else:
                    open_sectors[1] = "Shadow"
                    x = 1
                # end if
                if x != 1: x = (clock_() % 2) + 1
                lock(universe.lock)
                with universe:
                    universe.robot[robot_index(ROBOT)].location = open_sectors[x]
                # end with
                unlock(universe.lock)
            #-- end def robot_move
            
            def robot_send_msg():
                dcl (msg_file = PL1.File,
                     msg      = parm)
                
                PL1.open.file(msg_file).title(vfile_(dname + ">" + "sv4.4.text")).stream.input
                PL1.read.file(msg_file).into(msg)
                count = int(msg.val)
                which = (clock_() % count) + 1
                for x in do_range(1, which):
                    PL1.read.file(msg_file).into(msg)
                # end if
                PL1.close.file(msg_file)
                which = (clock_() % universe.number) + 1
                for x in do_range(1, which):
                    edir = universe.pdir[x]
                    call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
                    if enemy.ptr != null() and x == which - 1:
                        lock(enemy.ship.lock)
                        with enemy.ship:
                            enemy.ship.fromtype = "RobotShip"
                            enemy.ship.fromname = ROBOT
                            enemy.ship.message = msg.val
                        # end with
                        unlock(enemy.ship.lock)
                    # end if
                # end for
            #-- end def robot_snd_msg
            
            if my.ship.condition == "DOCKING":
                x = (clock_() % 100000) + 1
                if x > 1: return
            # end if
            for x in do_range(1, 20):
                if universe.robot[x].controller == my.ship.user:
                    ROBOT = universe.robot[x].name
                    look_for_targets(action)
                    if action.val == "": health_check(action)
                    if action.val == "": move_or_contact(action)
                    if action.val == "fire": robot_fire()
                    if action.val == "move": robot_move()
                    if action.val == "cont": robot_send_msg()
                # end if
            # end for
            
        #-- end def hack_robot_actions
        
        if my.ship.condition != "DOCKING":
            rand_new_robot()
            take_free_robot()
        # end if
        hack_robot_actions()
        
    #-- end def robot_functions
    
    # /***** GAME INTERNALS *****/
    
    def make_ship(shiptype):
        lock(my.ship.lock)
        with my.ship:
            my.ship.type = shiptype
            my.ship.life_cur = my.ship.life_old = 10
            my.ship.condition = "GREEN"
            if shiptype == "Destroyer":
                my.ship.energy_cur = my.ship.energy_old = my.ship.energy_max = 700
                my.ship.shields_cur = my.ship.shields_old = my.ship.shields_max = 50
                my.ship.torps_cur = my.ship.torps_old = my.ship.torps_max = 10
            elif shiptype == "Cruiser":
                my.ship.energy_cur = my.ship.energy_old = my.ship.energy_max = 800
                my.ship.shields_cur = my.ship.shields_old = my.ship.shields_max = 70
                my.ship.torps_cur = my.ship.torps_old = my.ship.torps_max = 5
            elif shiptype == "Starship":
                my.ship.energy_cur = my.ship.energy_old = my.ship.energy_max = 1000
                my.ship.shields_cur = my.ship.shields_old = my.ship.shields_max = 60
                my.ship.torps_cur = my.ship.torps_old = my.ship.torps_max = 5
            elif shiptype == "Star Commander":
                my.ship.energy_cur = my.ship.energy_old = my.ship.energy_max = 100000
                my.ship.shields_cur = my.ship.shields_old = my.ship.shields_max = 1000
                my.ship.torps_cur = my.ship.torps_old = my.ship.torps_max = 100
            # end if
            my.ship.location = rand_location()
        unlock(my.ship.lock)
    #-- end def make_ship
    
    def update_condition():
        #on quit call command_seq_terminator;
        call.term_.single_refname(DO, code)
        call.hcs_.initiate(DO_dir, DO, DO, 0, 0, null(), code)
        call.set_acl(acl_entry, acl, whom)
        call.set_acl(acl_entry, acl, person.rstrip() + "." + project)
        lock(my.ship.lock)
        if my.ship.life_cur == 0: game_over()
        elif my.ship.deathmes == "down": game_over()
        elif my.ship.shields_cur == 0: my.ship.condition = "SHIELDS_DOWN"
        elif my.ship.condition == "DROBOT": my.ship.condition = "D-RAY"
        elif my.ship.life_cur > 6: my.ship.condition = "GREEN"
        elif my.ship.life_cur > 2: my.ship.condition = "YELLOW"
        else: my.ship.condition = "RED"
        unlock(my.ship.lock)
        
    # /* ELIMINATE GHOST SHIPS */
        for x in do_range(1, universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, "", 0, 0, enemy, code)
            if enemy.ptr != null():
                for y in range(universe.number):
                    if universe.user[x] == enemy.ship.user and universe.unique_id[x] != enemy.ship.unique_id:
                        lock(universe.lock)
                        with (universe):
                            for z in do_range(y, universe.number):
                                universe.pdir[z] = universe.pdir[z + 1]
                                universe.user[z] = universe.user[z + 1]
                                universe.unique_id[z] = universe.unique_id[z + 1]
                            # end for
                            universe.pdir[universe.number] = ""
                            universe.user[universe.number] = ""
                            universe.number = universe.number - 1
                        # end with
                        unlock(universe.lock)
                   # end if
                # end for
            # end if
        # end for
    #-- end def update_condition
    
    def security_check():
        if my.ship.type == "Star Commander" and (access == "no" or shiptype != my.ship.type):
            call.ioa_("^/FROM STARFLEET COMMAND: You have unathorized control of a Star Commander.^/You will be destroyed...")
            game_over()
        # end if
    #-- end def security_check
        
    def timed_input(input):
        ten_seconds = 10
        
        call.timer_manager_.alarm_call(ten_seconds, inform_routines)
        security_check()
        getline(input)
        call.timer_manager_.reset_alarm_call(inform_routines)
    #-- end def timed_input
    
    def command_seq_terminator():
        call.ioa_("^/:: COMMAND SEQUENCE TERMINATED ::")
        raise goto_command_loop
    #-- end def command_seq_terminator
     
    def send_notifications():
        # send_mail_info.sent_from = "STARRUNNERS"
        # send_mail_info.version = send_mail_info_version_2
        # send_mail_info.wakeup = True
        # send_mail_info.acknowledge = False
        # send_mail_info.notify = False
        # send_mail_info.always_add = False
        # send_mail_info.never_add = False
        for x in do_range(1, 50):
            if universe.notifications[x].person_id != "" and universe.notifications[x].project_id != "":
                # call.send_mail_(universe.notifications[x].person_id.rstrip() + "." + universe.notifications[x].project_id.rstrip(), "I have just entered the Starrunners universe...", send_mail_info, 0)
                call.do("send_message {0} {1}".format(universe.notifications[x].person_id.rstrip() + "." + universe.notifications[x].project_id.rstrip(), "I have just entered the Starrunners universe..."))
            # end if
        # end for
    #-- end def send_notifications
    
    def rand_location():
        x = (clock_() % 5) + 1
        if x == 1: location = "Romula"
        elif x == 2: location = "Vindicar"
        elif x == 3: location = "Telgar"
        elif x == 4: location = "Shadow"
        else: location = "Zork"
        return location
    #-- end def rand_location
    
    def generate_codeword(key_word):
        password = ""
        new_pass = ""
        idx = shift = position = new_pos = 0
        ALPHA_1  = "abcdefghijklmnopqrstuvwxyz"
        ALPHA_2  = "zafkpubglqvchmrwdinsxejoty"
        
        password = key_word
        for x in do_range(1, 3):
            for y in do_range(1, length(rtrim(password))):
                if y == length(rtrim(password)): idx = 0
                else: idx = y
                shift = index(ALPHA_1, substr(password, idx + 1, 1))
                position = index(ALPHA_2, substr(password, y, 1))
                new_pos = shift + position
                if new_pos > 26: new_pos = new_pos - 26
                new_pass = new_pass + substr(ALPHA_2, new_pos, 1)
            # end for
            password = new_pass
            new_pass = ""
        # end for
        return password
    #-- end def generate_codeword
    
    def lock(lock_bit):
        call.set_lock_.lock(lock_bit, 5, code)
    #-- end def lock
    
    def unlock(lock_bit):
        call.set_lock_.unlock(lock_bit, code)
    #-- end def unlock
    
    # /***** STAR ADMIN SYSTEM *****/

    def star_admin():
        password      = parameter()
        MAIN          = "star_admin"
        version       = "1.2"
        from datetime import datetime as date
        
        def big_bang():
            call.hcs_.initiate(dname, xname, "", 0, 0, univptr, code)
            if code.val != 0 and univptr.ptr == null():
                call.ioa_("^a (big_bang): No database was found.", MAIN)
                call.ioa_("Creating ^a>^a", dname, xname)
                call.hcs_.make_seg(dname, xname, "", 0, univptr, code)
                universe.number     = 0
                universe.holes      = 0
                universe.unique_id  = [0] * (10+1)
                universe.pdir       = [""] * (10+1)
                universe.user       = [""] * (10+1)
                universe.black_hole = [""] * (5+1)
                universe.password   = ""
                universe.lock       = univptr.ptr.lock_word()
            else:
                call.ioa_("^a (big_bang): Database destroyed and re-created.", MAIN)
                call.hcs_.delentry_seg(univptr.ptr, code)
                call.hcs_.make_seg(dname, xname, "", 0, univptr, code)
                universe.number     = 0
                universe.holes      = 0
                universe.unique_id  = [0] * (10+1)
                universe.pdir       = [""] * (10+1)
                universe.user       = [""] * (10+1)
                universe.black_hole = [""] * (5+1)
                universe.password   = ""
                universe.lock       = univptr.ptr.lock_word()
            # end if
            
            # print univptr.ptr.dumps()
            
            call.hcs_.initiate(dname, aname, "", 0, 0, adminptr, code)
            if code.val != 0 and adminptr.ptr == null():
                create_database()
                call.ioa_("^/Created: ^a>^a", dname, aname)
            else:
                call.hcs_.delentry_seg(adminptr.ptr, code)
                create_database()
            # end if
        #-- end def big_bang
            
        def create_database():
            acl = "r"
            
            call.hcs_.make_seg(dname, aname, "", 0, adminptr, code)
            call.set_acl(dname.rstrip() + ">" + aname, acl, whom)
            with admin_info:
                call.ioa_.nnl("^a (admin_info): Game Admin: ", MAIN)
                getline(input)
                admin_info.game_admin = input.val
                call.ioa_.nnl("^a (admin_info): User_info_line: ", MAIN)
                getline(input)
                admin_info.user_info_line = input.val
                call.ioa_.nnl("^a (admin_info): Command_query_line: ", MAIN)
                getline(input)
                admin_info.com_query_line = input.val
                admin_info.star_comn.reset(1)
                call.ioa_.nnl("^a (admin_info): Star Commander: ", MAIN)
                getline(input)
                admin_info.star_coms[0] = input.val
            # end with
        #-- end def create_database

        def set_password():
            call.hcs_.initiate(dname, xname, "", 0, 0, univptr, code)
            if code.val != 0 and univptr.ptr == null():
                call.ioa_("^a (set_pswd): Database not found. ^a>^a", MAIN, dname, xname)
                return
            # end if
            input.val = "#"
            while input .val == "#":
                call.ioa_.nnl("^/New password: ")
                getline(input)
                if input.val == "":
                    call.ioa_("^a (set_pswd): Current password \"^a\" not changed.", MAIN, universe.password)
                    return
                # end if
                if verify(input.val, allowed_chars) == 0: password = input.val
                else:
                    call.ioa_("^a (set_pswd): Invalid character(s) found in pssword.  Please retype.", MAIN)
                    input = "#"
                # end if
                universe.password = password
            # end while
        #-- end def set_password
        
        def remove_password():
            call.hcs_.initiate(dname, xname, "", 0, 0, univptr, code)
            if code.val != 0 and univptr.ptr == null():
                call.ioa_("^a (set_pswd): Database not found. ^a>^a", MAIN, dname, xname)
                return
            # end if
            universe.password = ""
            call.ioa_("^a (remove_pswd): Password removed.", MAIN)
        #-- end def remove_password
        
        def generate_password():
            codeword = ""
            input    = parm("")
            
            call.ioa_.nnl("^/Keyword: ")
            getline(input)
            if input.val == "": return
            codeword = input.val
            call.ioa_("^/Codeword is \"^a\".", generate_codeword(codeword))
        #-- end def generate_password
        
        def add_star_commander():
            call.hcs_.initiate(dname, aname, "", 0, 0, adminptr, code)
            if code.val != 0 and adminptr.ptr == null():
                call.ioa_("^a (add_starcom): Database not found. ^a>^a", MAIN, dname, aname)
                return
            # end if
            call.ioa_.nnl("^a (add_starcom): Person ID: ", MAIN)
            getline(input)
            if input.val == "": return
            for x in do_range(1, admin_info.star_comn):
                if admin_info.star_coms[x-1] == "":
                    with admin_info:
                        admin_info.star_coms[x-1] = input.val
                    # end with
                    return
                # end if
            # end for
            with admin_info:
                admin_info.star_comn += 1
                admin_info.star_coms[admin_info.star_comn-1] = input.val
            # end with
        #-- end def add_star_commander
        
        def remove_star_commander():
            call.hcs_.initiate(dname, aname, "", 0, 0, adminptr, code)
            if code.val != 0 and adminptr.ptr == null():
                call.ioa_("^a (remove_starcom): Database not found. ^a>^a", MAIN, dname, aname)
                return
            # end if
            call.ioa_("^/Current Star Commanders:")
            for x in do_range(1, admin_info.star_comn):
                if admin_info.star_coms[x-1] != "": call.ioa_("   ^a", admin_info.star_coms[x])
            # end for
            call.ioa_.nnl("^a (remove_starcom): Person ID: ", MAIN)
            getline(input)
            if input.val == "": return
            with admin_info:
                for x in do_range(1, admin_info.star_comn):
                    if admin_info.star_coms[x-1] == input.val: admin_info.star_coms[x] = ""
                # end for
            # end with
        #-- end def remove_star_commander
        
        input.val = ""
        call.ioa_("^/Star Admin ^a^/", version)
        call.read_password_("Password:", password)
        if password.val != date.now().strftime("%m%d%Y"):
            call.ioa_("^a: Incorrect password supplied.", MAIN)
            # return
        # end if
        password.val = ""
        while (b'1'):
            call.ioa_.nnl("^/Star admin: ")
            getline(input)
            if input.val == "big-bang" or input.val == "bb": big_bang()
            elif input.val == "set-pswd" or input.val == "sp": set_password()
            elif input.val == "remove-pswd" or input.val == "rp": remove_password()
            elif input.val == "add-starcom" or input.val == "as": add_star_commander()
            elif input.val == "remove-starcom" or input.val == "rs": remove_star_commander()
            elif input.val == "generate-code" or input.val == "gc": generate_password()
            elif input.val == "quit" or input.val == "q": return
            elif input.val == ".": call.ioa_("^/^a ^a", MAIN, version)
            elif input.val == "?":
                call.ioa_("^/Star Admin commands:")
                call.ioa_("   (bb) big-bang ---------- Destroy the universe")
                call.ioa_("   (sp) set-pswd ---------- Set a game password")
                call.ioa_("   (rp) remove-pswd ------- Remove the game password")
                call.ioa_("   (as) add-starcom ------- Add a Person_ID as a Star Commander")
                call.ioa_("   (rs) remove-starcom ---- Remove a Person_ID as a Star Commander")
                call.ioa_("   (gc) generate-code ----- Generate a codeword")
                call.ioa_("    (q) quit -------------- Quit the star admin system")
            elif input.val != "": call.ioa_("^a: That is not a standard request:^/^12xType a \"?\" for a list of proper requests.", MAIN)
        # end while
    #-- end def star_admin

    # /* STAR ADMIN REQUEST ROUTINES */
    
    def getline(input_var):
        MAIN = "starrunners"
        
        query_info.version = query_info_version_5
        query_info.suppress_spacing = True
        query_info.suppress_name_sw = True
        # query_info.cp_escape_control = "10"b;
        
        call.command_query_(query_info, input_var, MAIN)
    #-- end def getline
    
    procedure()
    
#-- end def starrunners

star = starrunners
