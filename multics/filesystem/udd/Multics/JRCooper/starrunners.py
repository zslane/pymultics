from pprint import pprint

from multics.globals import *

include.pit
include.query_info

class goto_end_of_game(Exception): pass

pdir = ""

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
    
    # pdir                     = ""
    
    adminptr                 = ptr . init(null())
    univptr                  = ptr . init(null())
    my                       = ptr . parm . init(null())
    enemy                    = ptr . parm . init(null())
    
    dcl (
        
        argn                 = fixed.bin . parm . init(0),
        argp                 = ptr . parm . init(null()),
        input                = char(256) . varying . parm . init(""),
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
        # target               = ""
        # x                    = 0
        # y                    = 0
        # z                    = 0
        
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
        global pdir
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
                # damage_check()
                # message_check()
                # death_check()
                # black_hole_check()
                # check_monitor()
                # psionics_check()
                # robot_functions()
            
            except goto_end_of_game: # goto end_of_game
                return
                
            except BreakCondition: # on quit call command_seq_terminator;
                command_seq_terminator()
                
            except DisconnectCondition: # on finish call universe_destroyed;
                try:
                    # universe_destroyed()
                    game_over()
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
                    shipname[present.val] = enemy.ship.name
                    shiptype[present.val] = enemy.ship.type
                    if enemy.ship.condition == "DOCKING": docked[present.val] = "(Docking)"
                    elif enemy.ship.condition == "SHIELDS DOWN": docked[present.val] = "(Shields Down)"
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
            if x == 1: call.ioa_("\nION STORM encountered on course {0} to {1}", course, input)
            elif x == 2: call.ioa_("\nASTEROID BELT encountered on course {0} to {1}", course, input)
            if x < 3: hazard_damage()
        
        def hazard_damage():
            lock(my.ship)
            with my.ship:
                x = (clock () % 10) + 1
                my.ship.shields_cur = max(0, my.ship.shields_cur - x)
                my.ship.shields_old = max(0, my.ship.shields_old - x)
                x = (clock () % 100) + 1
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
    
    def game_over():
        call.ioa_("GAME OVER")
        universe.number = 0
        # print univptr.ptr.dumps()
        raise goto_end_of_game
    
    def inform_monitor(location):
        pass
        
    def inform_psionics(old_loc, location):
        pass

    # /***** ROBOT INTERNALS *****/
    
    def robot_sscan(present, shipname, shiptype, docked):
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
        print my.ship.dumps()
    #-- end update_condition
        
    def security_check():
        pass
    #-- end def security_check
        
    def timed_input(input):
        ten_seconds = 10
    
        def inform_routines():
            # on seg_fault_error call universe_destroyed;
            # damage_check()
            # message_check()
            # death_check()
            # black_hole_check()
            # check_monitor()
            # psionics_check()
            # robot_functions()
            call.timer_manager_.alarm_call(ten_seconds, inform_routines)
        
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
        whom = "*.*.*"
        
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
