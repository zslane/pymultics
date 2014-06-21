from pprint import pprint

from multics.globals import *

include.pit
include.query_info

class goto_end_of_game(Exception): pass

#== True global variables (that aren't parm types)
pdir      = ""
acl_entry = ""
shiptype  = ""
person    = ""
project   = ""
access    = "no"

def starrunners():

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
            robot            = Dim(2) (PL1.Structure(
                name         = char(5),
                energy       = fixed.bin,
                condition    = char(7),
                location     = char(8),
                controller   = char(21)
            )),
            notifications    = Dim(5) (PL1.Structure(
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
        for x in range(len(universe.notifications)): #range(50):
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
            for x in range(len(universe.notifications)): #range(50):
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
                             # if universe.notifications (x).person_id = person & universe.notifications (x).project_id = project:;
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
        call.set_acl(acl_entry, acl, whom)
        call.hcs_.set_ring_brackets(pdir, ename, ring_brackets, code)
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
            my.ship.energy_cur = my.ship.energy_old = my.ship.energy_max = my.ship.shields_cur = my.ship.shields_old = my.ship.shields_max = my.ship.torps_cur = my.ship.torps_old = my.ship.torps_max = my.ship.life_cur = my.ship.life_old = my.ship.psi_num = 0
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
                universe.black_hole = [""] * 5
                for i in range(len(universe.robot)): #range(20):
                    universe.robot[i].energy = 0
                    universe.robot[i].location = ""
                    universe.robot[i].condition = ""
                    universe.robot[i].controller = "none"
                # end for
            # end if
        # end with
        unlock(universe)
        
        # print univptr.ptr.dumps()
        
    # /* RECORED THE USER'S PERSON_ID */
        lock(my.ship)
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
                    call.ioa_("\nYou do not have proper clearance for Star Command.\n")
                    input.val = ""
                else:
                    password = parameter()
                    codeword = parameter()
                    call.ioa_()
                    call.read_password_("Password: ", password)
                    if len(password.val.strip()) < 3:
                        call.ioa_("{0}: Password must be at least 3 characters long.", MAIN)
                        return
                    # end if
                    call.read_password_("Codeword:", codeword)
                    if codeword.val != generate_codeword(password.val):
                        call.ioa_("Star Command clearance check failed.\n")
                        input.val = ""
                    else: call.ioa_("\nYou have been cleared for Star Command.")
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
        # black_hole_check()
        # check_monitor()
        # send_notifications()
        
    # /***** ENTER COMMAND LOOP ENVIRONMENT *****/
        
        while True:
            try:
                update_condition()
                input.val = ""
                call.ioa_.nnl("\nCOMMAND :> ")
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
                
                elif input.val == ".": call.ioa_("\n{0} {1}", MAIN, version)
                elif my.ship.type == "Star Commander":
                    if input.val == "cloaking-device" or input.val == "cd": cloaking_device()
                    elif input.val == "nova-blast" or input.val == "nb": nova_blast()
                    elif input.val == "star-gate" or input.val == "sg": create_stargate()
                    elif input.val == "tractor-beam" or input.val == "tb": tractor_beam()
                    elif input.val == "tractor-pull" or input.val == "tp": tractor_pull()
                    elif input.val == "trojan-horse" or input.val == "tj": trojan_horse()
                    elif input.val == "computer" or input.val == "cm": computer()
                    elif input.val[0] == ":": escape_to_multics()
                    elif input.val == "?":
                        command_list()
                        classified_com_list()
                    elif input.val != "":
                        call.ioa_("\n*** COMPUTER:")
                        call.ioa_("   That is not a standard ship command:")
                        call.ioa_("   Type a \"?\" for a list of proper commands")
                    # end if
                elif input.val == "?": command_list()
                elif input.val != "":
                    call.ioa_("\n*** COMPUTER:")
                    call.ioa_("   That is not a standard ship command:")
                    call.ioa_("   Type a \"?\" for a list of proper commands")
                    input.val = ""
                # end if
                
            # /* ENVIRONMENT CHECKING ROUTINES -- DAMAGE, MESSAGES, DEATHS, BLACK_HOLES, MONITOR, PSIONICS */
                damage_check()
                message_check()
                death_check()
                # black_hole_check()
                check_monitor()
                psionics_check()
                robot_functions()
            
            except goto_end_of_game: # goto end_of_game
                return
                
            except BreakCondition: # on quit call command_seq_terminator;
                command_seq_terminator()
                
            except DisconnectCondition: # on finish call universe_destroyed;
                try:
                    universe_destroyed()
                except goto_end_of_game:
                    pass
                finally:
                    raise DisconnectCondition()
                
            except SegmentFault: # on seg_fault_error call universe_destroyed;
                try:
                    universe_destroyed()
                    
                except goto_end_of_game:
                    return
                
            except:
                raise
            # end try
                
        # end while
        
    #-- end procedure

    # /***** COMMAND ROUTINES *****/

    def ship_status():
        call.ioa_("\nShip name: {0}", my.ship.name)
        call.ioa_("Ship type: {0}", my.ship.type)
        call.ioa_("---------------------")
        call.ioa_("Shield strength: {0}%", my.ship.shields_cur)
        call.ioa_("Missiles left: {0}", my.ship.torps_cur)
        call.ioa_("Energy left: {0}u", my.ship.energy_cur)
        call.ioa_("Life support level: {0}", my.ship.life_cur)
        call.ioa_("---------------------")
        call.ioa_("Condition: {0}", my.ship.condition)
        call.ioa_("Current location: {0}", my.ship.location)
    #-- end def ship_status
    
    def long_scan():
        stars = [""] * 5
        
        if my.ship.location == "Romula": stars[0] = "o"
        elif my.ship.location == "Vindicar": stars[1] = "o"
        elif my.ship.location == "Telgar": stars[2] = "o"
        elif my.ship.location == "Shadow": stars[3] = "o"
        else: stars[4] = "o"
        for x in range(universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if not enemy.ship.cloak_on:
                    if enemy.ship.type == "Star Commander":
                        if enemy.ship.location == "Romula": stars[0] += "@"
                        elif enemy.ship.location == "Vindicar": stars[1] += "@"
                        elif enemy.ship.location == "Telgar": stars[2] += "@"
                        elif enemy.ship.location == "Shadow": stars[3] += "@"
                        else: stars[4] += "@"
                    else:
                        if enemy.ship.location == "Romula": stars[0] += "*"
                        elif enemy.ship.location == "Vindicar": stars[1] += "*"
                        elif enemy.ship.location == "Telgar": stars[2] += "*"
                        elif enemy.ship.location == "Shadow": stars[3] += "*"
                        else: stars[4] += "*"
                    # end if
                # end if
            # end if
        # end if
        call.ioa_("\n   ROMULA    VINDICAR     TELGAR    SHADOW      ZORK")
        call.ioa_("--------------------------------------------------------")
        call.ioa_("|          |          |          |          |          |")
        call.ioa_("|{0:<10}|{1:<10}|{2:<10}|{3:<10}|{4:<10}|", stars[0], stars[1], stars[2], stars[3], stars[4])
        call.ioa_("|          |          |          |          |          |")
        call.ioa_("--------------------------------------------------------")
    #-- end def long_scan

    def short_scan():
        shipname   = [""] * 30
        shiptype   = [""] * 30
        docked     = [""] * 30
        present    = parm . init(0)
        black_hole = False
        
        print univptr.ptr.dumps()
        call.ioa_("\nSECTOR: {0}", my.ship.location)
        for x in range(5):
            if universe.black_hole[x] == my.ship.location: black_hole = True
        # end for
        for x in range(universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if not enemy.ship.cloak_on and enemy.ship.location == my.ship.location:
                    present.val = present.val + 1
                    shipname[present.val - 1] = enemy.ship.name
                    shiptype[present.val - 1] = enemy.ship.type
                    if enemy.ship.condition == "DOCKING": docked[present.val - 1] = "(Docking)"
                    elif enemy.ship.condition == "SHIELDS DOWN": docked[present.val - 1] = "(Shields Down)"
                # end if
            # end if
        # end for
        robot_sscan(present, shipname, shiptype, docked)
        if present.val == 0 and not black_hole:
            call.ioa_("*** SENSOR SCAN: Sector Void")
            return
        # end if
        call.ioa_("*** SENSOR SCAN:")
        if black_hole: call.ioa_("(((BLACK HOLE)))")
        for x in range(present.val):
            call.ioa_("   {0} {1} {2}", shiptype[x], shipname[x], docked[x])
        # end for
    #-- end def short_scan
    
    def move_ship():
        open_sectors = [""] * 2
        how_many     = 1
        input        = parm("")
        
        def hazard_check():
            x = (clock_() % 200) + 1
            course = "{0:06d}".format((clock_() % 99999) + 1)
            if x == 1: call.ioa_("\nION STORM encountered on course {0} to {1}", course, input.val)
            elif x == 2: call.ioa_("\nASTEROID BELT encountered on course {0} to {1}", course, input.val)
            if x < 3: hazard_damage()
        
        def hazard_damage():
            lock(my.ship)
            with my.ship:
                x = (clock_() % 10) + 1
                my.ship.shields_cur = max(0, my.ship.shields_cur - x)
                my.ship.shields_old = max(0, my.ship.shields_old - x)
                x = (clock_() % 100) + 1
                my.ship.energy_cur = max(0, my.ship.energy_cur - x)
                my.ship.energy_old = max(0, my.ship.energy_old - x)
            # end with
            unlock(my.ship)
        
        old_loc = my.ship.location;
        if my.ship.energy_cur < 10:
            call.ioa_("\nWE haven't got the energy to move, sir")
            return
        elif my.ship.tractor_on:
            call.ioa_("\nTRACTOR BEAM holding our ship, sir")
            return
        # end if
        if my.ship.location == "Romula": open_sectors[0] = "Vindicar"
        elif my.ship.location == "Vindicar":
            how_many = 2
            open_sectors[0] = "Romula"
            open_sectors[1] = "Telgar"
        elif my.ship.location == "Telgar":
            how_many = 2
            open_sectors[0] = "Vindicar"
            open_sectors[1] = "Shadow"
        elif my.ship.location == "Shadow":
            how_many = 2
            open_sectors[0] = "Telgar"
            open_sectors[1] = "Zork"
        else: open_sectors[0] = "Shadow"
        while input.val == "":
            if how_many == 1: call.ioa_("\nOPEN SECTOR is {0}, sir", open_sectors[0])
            else: call.ioa_("\nOPEN SECTORS are {0} and {1}, sir", open_sectors[0], open_sectors[1])
            call.ioa_.nnl("NAVIGATION :> ")
            timed_input(input)
            if input.val == "": return
            elif input.val == open_sectors[0] or input.val == open_sectors[1]:
                if input.val != "":
                    lock(my.ship)
                    with my.ship:
                        my.ship.location = input.val
                        my.ship.energy_cur = my.ship.energy_cur - 10
                        my.ship.energy_old = my.ship.energy_old - 10
                    # end with
                    unlock(my.ship)
                    call.ioa_("COURSE set for {0}, sir", input.val)
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
            call.ioa_("\nWE haven't got the energy to warpout, sir")
            return
        # end if
        if my.ship.tractor_on:
            call.ioa_("\nTRACTOR BEAM holding our ship, sir")
            return
        # end if
        old_loc = my.ship.location
        x = (clock_() % 1000) + 1
        if x > my.ship.energy_cur:
            call.ioa_("\n<<< BOOOOOOOOOOM >>>")
            call.ioa_("You have warped into a star")
            game_over()
        # end if
        lock(my.ship)
        with my.ship:
            my.ship.location = rand_location()
            my.ship.energy_cur = my.ship.energy_cur - 100
            my.ship.energy_old = my.ship.energy_old - 100
        # end with
        unlock(my.ship)
        call.ioa_("\nWARPOUT *****----------")
        call.ioa_("New location: {0}", my.ship.location)
        if old_loc != my.ship.location:
            inform_monitor(my.ship.location)
            inform_psionics(old_loc, my.ship.location)
        # end if
    #-- end def warpout
    
    def launch_missile():
        is_he_there = parm(False)
        hit         = parm(False)
        
        if my.ship.torps_cur == 0:
            call.ioa_("\nWE are out of missiles, sir")
            return
        # end if
        call.ioa_("\nMISSILE ready to launch, sir")
        call.ioa_.nnl("Target name: ")
        timed_input(input)
        if input.val == "": return;
        target.val = input.val
        verify_target(target, is_he_there)
        if not is_he_there.val:
            call.ioa_("*** SENSORS: Target ship {0} is not in this sector, sir", target)
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
                lock(my.ship)
                with my.ship:
                    my.ship.torps_cur = my.ship.torps_cur - 1
                    my.ship.torps_old = my.ship.torps_old - 1
                # end with
                unlock(my.ship)
                call.ioa_("\nMISSILE launched, sir")
                hit_that_sucker(hit, "missile")
                if target.val == "critical": return
                if not hit.val:
                    call.ioa_("MISSILE missed, sir")
                    return
                else: call.ioa_("<< BOOM >> MISSILE hit, sir")
                inflict_damage()
                if target_is_a_robot(target.val): return
                if enemy.ship.psionics:
                    lock(enemy.ship)
                    with enemy.ship:
                        enemy.ship.psi_mes[0] = "hit"
                        enemy.ship.psi_name[0] = my.ship.name
                        enemy.ship.psi_type[0] = my.ship.type
                    # end with
                    unlock(enemy.ship)
                # end if
            else: input.val = ""
        # end while
    #-- end def launch_missile
    
    def fire_lasers():
        is_he_there = parm(False)
        hit         = parm(False)
        
        if my.ship.energy_cur < 10:
            call.ioa_("\nWE haven't got the energy to fire lasers, sir")
            return
        # end if
        call.ioa_("\nLASER banks ready to fire, sir")
        call.ioa_.nnl("Target name: ")
        timed_input(input)
        if input.val == "": return;
        target.val = input.val
        verify_target(target, is_he_there)
        if not is_he_there.val:
            call.ioa_("*** SENSORS: Target ship {0} is not in this sector, sir", target)
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
                lock(my.ship)
                with my.ship:
                    my.ship.energy_cur = my.ship.energy_cur - 10
                    my.ship.energy_old = my.ship.energy_old - 10
                # end with
                unlock(my.ship)
                call.ioa_("\nLASERS fired, sir")
                hit_that_sucker(hit, "lasers")
                if target.val == "critical": return
                if not hit.val:
                    call.ioa_("LASERS missed, sir")
                    return
                else: call.ioa_("<< ZAP >> LASERS hit, sir")
                inflict_damage()
                if target_is_a_robot(target.val): return
                if enemy.ship.psionics:
                    lock(enemy.ship)
                    with enemy.ship:
                        enemy.ship.psi_mes[0] = "hit"
                        enemy.ship.psi_name[0] = my.ship.name
                        enemy.ship.psi_type[0] = my.ship.type
                    # end with
                    unlock(enemy.ship)
                # end if
            else: input.val = ""
        # end while
    #-- end def fire_lasers

    def contact_ship():
        x      = 0
        sendto = ""
          
        call.ioa_.nnl("\nWHO do you wish to contact, sir? ")
        timed_input(input)
        if input.val == "": return
        sendto = input.val
        if target_is_a_robot(sendto):
            call.ioa_("\nTRANSMISSIONS can not be sent to a RobotShip, sir")
            return
        # end if
        call.ioa_("WHAT is the message, sir?")
        call.ioa_.nnl("---: ")
        getline(input)
        if input.val == "":
            call.ioa_("MESSAGE not sent, sir")
            return
        # end if
        for x in range(universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null () and edir != pdir:
                if enemy.ship.name == sendto:
                    lock(enemy.ship)
                    with enemy.ship:
                        enemy.ship.fromname = my.ship.name
                        enemy.ship.fromtype = my.ship.type
                        enemy.ship.message = input.val
                    # end with
                    unlock(enemy.ship)
                    call.ioa_("MESSAGE sent, sir")
                    return
                # end if
            # end if
        # end for
        call.ioa_("TRANSMISSIONS are not being accepted by a ship named {0}, sir", sendto)
    #-- end def contact_ship
     
    def dock():
        x = 0
        
        if my.ship.tracname != "": call.ioa_("\n** STARBASE {0}: Please deactivate your Tractor Beam", my.ship.location)
        if my.ship.cloak_on: call.ioa_("\n** STARBASE {0}: Please deactivate your Cloaking Device", my.ship.location)
        if my.ship.tracname != "" or my.ship.cloak_on: return
        call.ioa_("\n** Welcome to STARBASE {0} **", my.ship.location)
        if my.ship.shields_cur > 0: call.ioa_("SHIELDS will be lowered for docking")
        # on quit call ignore_signal;
        inform_monitor("docking")
        inform_psionics("docking", my.ship.location)
        lock(my.ship)
        with my.ship:
            my.ship.condition = "DOCKING"
            my.ship.shields_cur = my.ship.shields_old = min(my.ship.shields_max, my.ship.shields_cur + 10)
            x = (clock_() % 3) + 1
            my.ship.torps_cur = my.ship.torps_old = min(my.ship.torps_max, my.ship.torps_cur + x)
            x = (clock_() % 41) + 10
            my.ship.energy_cur = my.ship.energy_old = min(my.ship.energy_max, my.ship.energy_cur + x)
            my.ship.life_cur = my.ship.life_old = min(10, my.ship.life_cur + 1)
        # end with
        unlock(my.ship)
        for x in range(16): # Make docking take 8 seconds
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
        
            for x in range(universe.number):
                edir = universe.pdir[0]
                call.hcs_.initiate(edir, ename, enemy, code)
                if enemy.ptr != null() and edir != pdir:
                    if enemy.ship.location == my.ship.location:
                        damage = (clock_() % 10) + 1
                        lock(enemy.ship)
                        enemy.ship.shields_cur = max(0, enemy.ship.shields_cur - damage)
                        unlock(enemy.ship)
                    # end if
                # end if
            # end for
            game_over()
        #-- end def share_the_misery
     
        call.ioa_.nnl("\nINITIATE self destruct sequence: ")
        timed_input(input)
        if input.val != "1a":
            call.ioa_("INCORRECT sequence password given :: sequence terminated")
            return
        # end if
        call.ioa_("SELF destruct sequence initiated ***")
        call.ioa_.nnl ("\nINITIATE sequence 2: ")
        timed_input(input)
        if input.val != "2b":
            call.ioa_("INCORRECT sequence password given :: sequence terminated")
            return
        # end if
        call.ioa_("SEQUENCE 2 initiated ***")
        call.ioa_.nnl("\nSELF destruct command: ")
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

    def escape_to_multics():
        command = input.val[1:]
        call.do(command)
    #-- end def escape_to_multics
    
    # /* TARGETTING -- HIT DETERMINATION AND CRITICAL HITS */

    def verify_target(target, is_he_there):
        for x in range(universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null () and edir != pdir:
                if enemy.ship.location == my.ship.location and enemy.ship.name == target.val:
                    is_he_there.val = True
                    return
                # end if
            # end if
        # end for
        robot_verify_target(target, is_he_there)
    #-- end def verify_target
    
    def hit_that_sucker(hit, weapon):
        robot_was_the_target = parm(False)
        x                    = 0

        def critical_hit():
            if weapon != "plasma":
                call.ioa_("\n<<< BOOOOOOOOOOM >>>")
                call.ioa_("<<< BOOOOOOOOOOM >>>")
                call.ioa_("\nCRITICAL centers have been hit on the {0} {1}!", enemy.ship.type, enemy.ship.name)
            # end if
            lock (enemy.ship)
            enemy.ship.deathmes = "bang"
            unlock(enemy.ship)
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
        call.ioa_("x = {0}", x)
        if x > enemy.ship.shields_cur: hit.val = True
        else: hit.val = False
    #-- end def hit_that_sucker
    
    def inflict_damage():
        d = parm(0)
        x = 0
        
        robot_damage(target, d)
        if d.val == 666: return
        lock(enemy.ship)
        if enemy.ship.condition == "DOCKING" or enemy.ship.condition == "D-RAY" or enemy.ship.condition == "SHIELDS DOWN" or enemy.ship.condition == "DROBOT":
            enemy.ship.deathmes = "down"
            unlock(enemy.ship)
            if my.ship.condition.find("ROBOT") == -1: call.ioa_("\nDEFLECTOR shields were down on the {0} {1}, sir", enemy.ship.type, enemy.ship.name)
            return
        # end if
        while x == 0:
            x = (clock_() % 4) + 1
            if x == 1:
                if enemy.ship.shields_cur == 0: x = 0
                else:
                    x = (clock_() % 10) + 1
                    enemy.ship.shields_cur = max(0, enemy.ship.shields_cur - x)
                    if my.ship.condition.find("ROBOT") == -1: call.ioa_("\nSHIELDS damaged on the {0} {1}, sir", enemy.ship.type, enemy.ship.name)
                # end if
            elif x == 2:
                if enemy.ship.energy_cur == 0: x = 0
                else:
                    x = (clock_() % 100) + 1
                    enemy.ship.energy_cur = max(0, enemy.ship.energy_cur - x)
                    if my.ship.condition.find("ROBOT") == -1: call.ioa_("\nENGINES damaged on the {0} {1}, sir", enemy.ship.type, enemy.ship.name)
                # end if
            elif x == 3:
                if enemy.ship.torps_cur == 0: x = 0
                else:
                    x = (clock_() % 3) + 1
                    enemy.ship.torps_cur = max(0, enemy.ship.torps_cur - x)
                    if my.ship.condition.find("ROBOT") == -1: call.ioa_("\nMISSILES damaged on the {0} {1}, sir", enemy.ship.type, enemy.ship.name)
                # end if
            elif x == 4:
                if enemy.ship.life_cur == 0: x = 0
                else:
                    enemy.ship.life_cur = enemy.ship.life_cur - 1
                    if my.ship.condition.find("ROBOT") == -1: call.ioa_("\nLIFE SUPPORT systems damaged on the {0} {1}, sir", enemy.ship.type, enemy.ship.name)
                # end if
            # end if
        # end while
        unlock(enemy.ship)
    #-- end def inflict_damage
    
    def inform_routines():
        ten_seconds = 10
        # on seg_fault_error call universe_destroyed;
        damage_check()
        message_check()
        death_check()
        # black_hole_check()
        check_monitor()
        psionics_check()
        robot_functions()
        call.timer_manager_.alarm_call(ten_seconds, inform_routines)
    #-- end def inform_routines
    
    # /***** ARMEGEDDON ROUTINES -- TRASH HIS SHIP, GOODBYE CRUEL UNIVERSE *****/
    
    def game_over():
    
        def update_universe():
            robot_release(my.ship.user)
            lock(universe)
            with universe:
                for x in range(universe.number):
                    if universe.pdir[x] == pdir:
                        for y in range(x, universe.number - 1):
                            universe.pdir[y] = universe.pdir[y + 1]
                            universe.user[y] = universe.user [y + 1]
                            universe.unique_id[y] = universe.unique_id[y + 1]
                        # end for
                        universe.pdir[universe.number - 1] = ""
                        universe.user[universe.number - 1] = ""
                        universe.unique_id[universe.number - 1] = 0
                        universe.number = universe.number - 1
                    # end if
                # end for
            # end with
            unlock(universe)
            call.hcs_.delentry_seg(my.ship, code)
            call.ioa_("\n<<< YOU HAVE BEEN VAPORIZED >>>")
            call.ioa_("\nThank you for playing STARRUNNERS.")
            raise goto_end_of_game
        #-- end def update_universe

        call.timer_manager_.reset_alarm_call(inform_routines)
        if input.val == "*": update_universe()
        for x in range(universe.number):
            edir = universe.pdir[0]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null() and edir != pdir and enemy.ship.name != "" and enemy.ship.type != "" and (my.ship.type == "Starship" or my.ship.type == "Cruiser" or my.ship.type == "Destroyer" or (my.ship.type == "Star Commander" and my.ship.life_cur == 0)):
                lock(enemy.ship)
                with enemy.ship:
                    enemy.ship.deathmes = "dead"
                    enemy.ship.deadname = my.ship.name
                    enemy.ship.deadtype = my.ship.type
                    if my.ship.tracname == enemy.ship.name: enemy.ship.tractor_on = False
                    if enemy.ship.tracname == my.ship.name: enemy.ship.tracname = ""
                    if my.ship.monname == enemy.ship.name: enemy.ship.monitored_by = ""
                # end with
                unlock(enemy.ship)
            # end if
        # end for
        update_universe()
    #-- end def game_over
    
    def universe_destroyed():
        univptr = null()
        call.hcs_.initiate(dname, xname, univptr, code)
        if code.val != 0 and univptr == null():
            call.ioa_("\n*** GALACTIC IMPLOSION IMMINENT ***\nAlas, the universe has been destroyed...")
            raise goto_end_of_game
        # end if
        call.ioa_("\n*** SENSORS: Enemy ship is gone, sir")
        enemy = null()
        # goto command_loop;
    #-- end def universe_destroyed
    
    # /***** INFORMING ROUTINES *****/
    
    def inform_monitor(info):
        if my.ship.monitored_by == "": return
        for x in range(universe.number):
            edir = universe.pdir[0]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null() and edir != pdir:
                if enemy.ship.name == my.ship.monitored_by:
                    lock(enemy.ship)
                    enemy.ship.monloc = info
                    unlock(enemy.ship)
                # end if
            # end if
        # end for
        if info == "vanished":
            lock(my.ship)
            my.ship.monitored_by = ""
            unlock(my.ship)
        # end if
    #-- end def inform_monitor
     
    def inform_psionics(old_loc, new_loc):
        for x in range(universe.number):
            edir = universe.pdir[0]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null() and edir != pdir and enemy.ship.psionics:
                if old_loc == enemy.ship.location or new_loc == enemy.ship.location or old_loc == "docking":
                    lock(enemy.ship)
                    with enemy.ship:
                        enemy.ship.psi_num = y = enemy.ship.psi_num + 1
                        enemy.ship.psi_name[y - 1] = my.ship.name
                        enemy.ship.psi_type[y - 1] = my.ship.type
                        if old_loc == enemy.ship.location: enemy.ship.psi_mes[y - 1] = "left"
                        elif old_loc == "docking": enemy.ship.psi_mes[y - 1] = new_loc
                        elif new_loc == enemy.ship.location: enemy.ship.psi_mes[y - 1] = "entered"
                    # end with
                    unlock(enemy.ship)
                # end if
            # end if
        # end for
    #-- end def inform_psionics

    def command_list():
        call.ioa_("\nCommands:")
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
        call.ioa_("\nClassified commands:")
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
        call.ioa_("\nComputer commands:")
        call.ioa_("   (srs) srunners -------- Player listing")
        call.ioa_("   (est) estatus --------- Enemy ship status")
        call.ioa_("   (prb) probe ----------- Probe for ship")
        call.ioa_("   (bhr) bhreport -------- Black hole report")
        call.ioa_("   (rsr) rsreport -------- RobotShip report")
    #-- end def computer_com_list
    
    # /***** ENVIRONMENT CHECKING ROUTINES *****/
    
    def damage_check():
        if my.ship.deathmes == "bang":
            call.ioa_("\n*** RED ALERT ***")
            call.ioa_("*** RED ALERT ***")
            call.ioa_("\nCRITICAL centers have been hit, sir!!!")
            game_over()
        elif my.ship.deathmes == "pull":
            call.ioa_("\nTRACTOR BEAM has pulled our ship into {0}, sir", my.ship.location)
            my.ship.deathmes = ""
        # end if
        if my.ship.life_cur == 0: game_over()
        elif my.ship.deathmes == "down": game_over()
        lock(my.ship)
        with my.ship:
            if my.ship.shields_cur != my.ship.shields_old:
                call.ioa_("\n<<< FOOOOOOOOOOM >>> SHIELDS have been hit, sir")
                call.ioa_("Shield strength has been reduced to {0}%", my.ship.shields_cur)
                # lock (my.ship)
                my.ship.shields_old = my.ship.shields_cur
                # unlock (my.ship)
            # end if
            if my.ship.energy_cur != my.ship.energy_old:
                call.ioa_("\n<<< FOOOOOOOOOOM >>> ENGINES have been hit, sir")
                call.ioa_("Energy remaining: {0}u", my.ship.energy_cur)
                # lock (my.ship)
                my.ship.energy_old = my.ship.energy_cur
                # unlock (my.ship)
            # end if
            if my.ship.torps_cur != my.ship.torps_old:
                call.ioa_("\n<<< FOOOOOOOOOOM >>> MISSILES have been hit, sir")
                call.ioa_("Missiles remaining: {0}", my.ship.torps_cur)
                # lock (my.ship)
                my.ship.torps_old = my.ship.torps_cur
                # unlock (my.ship)
            # end if
            if my.ship.life_cur != my.ship.life_old:
                call.ioa_("\n<<< FOOOOOOOOOOM >>> LIFE SUPPORT systems have been hit, sir")
                call.ioa_("Life support level: {0}", my.ship.life_cur)
                # lock (my.ship)
                my.ship.life_old = my.ship.life_cur
                # unlock (my.ship)
            # end if
            if my.ship.psi_mes[0] == "hit":
                call.ioa_("\nPSIONICS: We have just been attacked by the {0} {1}, sir", my.ship.psi_type[0], my.ship.psi_name[0])
                # lock (my.ship)
                my.ship.psi_mes[0] = my.ship.psi_name[0] = my.ship.psi_type[0] = ""
                # unlock (my.ship)
            # end if
        # end with
        unlock(my.ship)
    #-- end def damage_check
    
    def message_check():
        if my.ship.message == "": return
        if my.ship.message[:3] == "TH:" and my.ship.fromtype == "Trojan Horse":
            if my.ship.type == "Star Commander": call.ioa_("\nCOMMUNICATIONS: We've trapped a Trojan Horse from the Star Commander {0}\n{1:16s}({2})", my.ship.fromname, "", my.ship.message[3:])
            else: call.do(my.ship.message[3:])
            lock(my.ship)
            with my.ship:
                my.ship.fromname = my.ship.fromtype = my.ship.messge = ""
            # end with
            unlock(my.ship)
            return
        # end if
        call.ioa_("\nCOMMUNICATIONS: New transmission from the {0} {1}, sir", my.ship.fromtype, my.ship.fromname)
        call.ioa_("It says: {0}", my.ship.message)
        lock(my.ship)
        with my.ship:
            my.ship.message = my.ship.fromname = my.ship.fromtype = ""
        # end with
        unlock(my.ship)
    #-- end def message_check
    
    def death_check():
        if my.ship.deathmes != "dead": return
        call.ioa_("\n  <<< BOOOOOM >>>")
        call.ioa_("<<<<< BOOOOOM >>>>>")
        call.ioa_("  <<< BOOOOOM >>>")
        call.ioa_("\nSENSORS are picking up metallic debris from the {0} {1}, sir", my.ship.deadtype, my.ship.deadname)
        if my.ship.deadname == my.ship.monname:
            lock(my.ship)
            with my.ship:
                my.ship.monloc = ""
                my.ship.monname = my.ship.montype = "#"
            # end with
            unlock(my.ship)
            call.ioa_("\nMONITOR probe lost, sir")
        # end if
        lock(my.ship)
        with my.ship:
            my.ship.deathmes = my.ship.deadname = my.ship.deadtype = ""
        # end with
        unlock(my.ship)
    #-- end def death_check
    
    def check_monitor():
        if my.ship.monloc == "": return
        if my.ship.monloc == "docking": call.ioa_("\n*** MONITOR: {0} {1} has just docked", my.ship.montype, my.ship.monname)
        elif my.ship.monloc == "vanished":
            call.ioa_("\n*** MONITOR: Probe lost on {0} {1}", my.ship.montype, my.ship.monname)
            lock(my.ship)
            with my.ship:
                my.ship.monname = my.ship.montype = my.ship.monloc = ""
            # end with
            unlock(my.ship)
        else: call.ioa_("\n*** MONITOR: {0} {1} is now in {2}", my.ship.montype, my.ship.monname, my.ship.monloc)
        lock(my.ship)
        my.ship.monloc = ""
        unlock(my.ship)
    #-- end def check_monitor
     
    def psionics_check():
        if my.ship.psi_num > 0:
            if my.ship.psi_mes[0] != "left" and my.ship.psi_mes[0] != "entered": call.ioa_("\nPSIONICS: The {0} {1} has just docked at {2}, sir", my.ship.psi_type[0], my.ship.psi_name[0], my.ship.psi_mes[0])
            else: call.ioa_("\nPSIONICS: The {0} {1} has just ^a our sector, sir", my.ship.psi_type[0], my.ship.psi_name[0], my.ship.psi_mes[0])
            for x in range(1, my.ship.psi_num):
                if my.ship.psi_mes[x] != "left" and my.ship.psi_mes[x] != "entered": call.ioa_("{0:10s}The {1} {2} has just docked at {3}, sir", "", my.ship.psi_type[x], my.ship.psi_name[x], my.ship.psi_mes[x])
                else: call.ioa_("{0:10s}The {1} {2} has just {3} our sector, sir", "", my.ship.psi_type[x], my.ship.psi_name[x], my.ship.psi_mes[x])
            # end for
            lock(my.ship)
            with my.ship:
                my.ship.psi_name = [""] * 10
                my.ship.psi_type = [""] * 10
                my.ship.psi_mes = [""] * 10
                my.ship.psi_num = 0
            # end with
            unlock(my.ship)
        # end if
        
        if my.ship.psionics: return
        
        x = (clock_() % 2000) + 1
        if x > 1: return
        call.ioa_("\n=== STAR FLEET COMMAND ===")
        call.ioa_("\n=== Transmission to: {0} {1}", my.ship.type, my.ship.name)
        call.ioa_("=== You have been entrusted with our newest secret weapon: Psionics! ===")
        call.ioa_("=== Prepare to matter-transmit him aboard your ship. Congratulations ===")
        call.ioa_("\nMATTER-TRANSMITTER ready for boarding, sir")
        call.ioa_(">>>Energizeeeeeeeeeeeeeeeeeeeeeeeeeeeee...")
        call.ioa_("PSIONIC board ship, sir")
        lock(my.ship)
        my.ship.psionics = True
        unlock(my.ship)
    #-- end def psionics_check
    
    # /***** ROBOT INTERNALS *****/
    
    def robot_sscan(present, shipname, shiptype, docked):
        pass
    
    def target_is_a_robot(target):
        return False
        
    def robot_hit_him(target, robot_was_the_target, weapon, hit):
        robot_was_the_target.val = False
        
    def robot_verify_target(target, is_he_there):
        pass
        
    def robot_hit_him(target, robot_was_the_target, weapon, hit):
        robot_was_the_target.val = False
        
    def robot_damage(target, d):
        pass
        
    def robot_release(user):
        pass
        
    def robot_functions():
        pass

    # /***** GAME INTERNALS *****/
    
    def make_ship(shiptype):
        lock(my.ship)
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
        unlock(my.ship)
    #-- end def make_ship
    
    def update_condition():
        #on quit call command_seq_terminator;
        call.term_.single_refname(DO, code)
        call.hcs_.initiate(DO_dir, DO, null(), code)
        call.set_acl(acl_entry, acl, whom)
        call.set_acl(acl_entry, acl, person.rstrip() + "." + project)
        lock(my.ship)
        if my.ship.life_cur == 0: game_over()
        elif my.ship.deathmes == "down": game_over()
        elif my.ship.shields_cur == 0: my.ship.condition = "SHIELDS_DOWN"
        elif my.ship.condition == "DROBOT": my.ship.condition = "D-RAY"
        elif my.ship.life_cur > 6: my.ship.condition = "GREEN"
        elif my.ship.life_cur > 2: my.ship.condition = "YELLOW"
        else: my.ship.condition = "RED"
        unlock(my.ship)
        
    # /* ELIMINATE GHOST SHIPS */
        for x in range(universe.number):
            edir = universe.pdir[x]
            call.hcs_.initiate(edir, ename, enemy, code)
            if enemy.ptr != null():
                for y in range(universe.number):
                    if universe.user[x] == enemy.ship.user and universe.unique_id[x] != enemy.ship.unique_id:
                        lock(universe)
                        with (universe):
                            for z in range(y, universe.number - 1):
                                universe.pdir[z] = universe.pdir[z + 1]
                                universe.user[z] = universe.user[z + 1]
                                universe.unique_id[z] = universe.unique_id[z + 1]
                            # end for
                            universe.pdir[universe.number - 1] = ""
                            universe.user[universe.number - 1] = ""
                            universe.number = universe.number - 1
                        # end with
                        unlock(universe)
                   # end if
                # end for
            # end if
        # end for
    #-- end def update_condition
     
    def security_check():
        if my.ship.type == "Star Commander" and (access == "no" or shiptype != my.ship.type):
            call.ioa_("\nFROM STARFLEET COMMAND: You have unathorized control of a Star Commander.\nYou will be destroyed...")
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
        call.ioa_("\n:: COMMAND SEQUENCE TERMINATED ::")
    #-- end def command_seq_terminator
    
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
        for x in range(3):
            for y in range(len(password.rstrip())):
                if y == len(password.rstrip()) - 1: idx = -1
                else: idx = y
                shift = ALPHA_1.index(password[idx + 1])
                position = ALPHA_2.index(password[y])
                new_pos = shift + position
                if new_pos >= 26: new_pos = new_pos - 26
                new_pass = new_pass + ALPHA_2[new_pos]
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
        
    def verify(x, y):
        return len(set(x) - set(y))
    #-- end def verify
        
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
                call.ioa_("   (bb) big-bang ---------- Destroy the universe")
                call.ioa_("   (sp) set-pswd ---------- Set a game password")
                call.ioa_("   (rp) remove-pswd ------- Remove the game password")
                call.ioa_("   (as) add-starcom ------- Add a Person_ID as a Star Commander")
                call.ioa_("   (rs) remove-starcom ---- Remove a Person_ID as a Star Commander")
                call.ioa_("   (gc) generate-code ----- Generate a codeword")
                call.ioa_("    (q) quit -------------- Quit the star admin system")
            elif input.val != "": call.ioa_("{0}: That is not a standard request:\n{1:12}Type a \"?\" for a list of proper requests.", MAIN, "")

    # /* STAR ADMIN REQUEST ROUTINES */
    
    def big_bang():
        call.hcs_.initiate(dname, xname, univptr, code)
        if code.val != 0 and univptr.ptr == null():
            call.ioa_("{0} (big_bang): No database was found.", MAIN)
            call.ioa_("Creating {0}>{1}", dname, xname)
            call.hcs_.make_seg(dname, xname, univptr, code)
            universe.number     = 0
            universe.holes      = 0
            universe.unique_id  = [0] * 10
            universe.pdir       = [""] * 10
            universe.user       = [""] * 10
            universe.black_hole = [""] * 5
            universe.password   = ""
        else:
            call.ioa_("{0} (big_bang): Database destroyed and re-created.", MAIN)
            call.hcs_.delentry_seg(univptr.ptr, code)
            call.hcs_.make_seg(dname, xname, univptr, code)
            universe.number     = 0
            universe.holes      = 0
            universe.unique_id  = [0] * 10
            universe.pdir       = [""] * 10
            universe.user       = [""] * 10
            universe.black_hole = [""] * 5
            universe.password   = ""
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
        
        call.hcs_.make_seg(dname, aname, adminptr, code)
        call.set_acl(dname.rstrip() + ">" + aname, acl, whom)
        with admin_info:
            call.ioa_.nnl("{0} (admin_info): Game Admin: ", MAIN)
            getline(input)
            admin_info.game_admin = input.val
            call.ioa_.nnl("{0} (admin_info): User_info_line: ", MAIN)
            getline(input)
            admin_info.user_info_line = input.val
            call.ioa_.nnl("{0} (admin_info): Command_query_line: ", MAIN)
            getline(input)
            admin_info.com_query_line = input.val
            admin_info.star_comn.reset(1)
            call.ioa_.nnl("{0} (admin_info): Star Commander: ", MAIN)
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
    #-- end def getline
    
    procedure()
    
#-- end def starrunners

star = starrunners
