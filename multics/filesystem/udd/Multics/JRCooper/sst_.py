
from multics.globals import *

include. sst_node
# include. sst_macros
include. sst_constants

dcl ( clock                  = entry . returns (fixed.bin (36)) )
dcl ( ssu_                   = entry )
dcl ( sst_data_              = external_static )

dcl ( argn                   = fixed.bin . parm )
dcl ( argp                   = ptr )
dcl ( code                   = fixed.bin (35) . parm . init (0) )

class goto_place_supply_ship(Exception): pass
class goto_get_bomb_targets(Exception): pass

class sst_(Subroutine):

    def __init__(self):
        super(sst_, self).__init__(self.__class__.__name__)

    def set_up_game(self, node, game_length, rank):
        # These are fields that don't retain their initial values defined in sst_node_.py
        # node.suit_pts = 50
        # node.body_pts = 20
        # node.jet_energy = 1000
        # node.flamer_energy = 1000
        # node.nuke_bombN = 4
        # node.nuke_bonus_score = 5000
        # node.score.success_ratio = -1
        
        node.arachnidT = mod (clock (), (game_length * 10)) + game_length * 10
        node.skinnyT = mod (clock (), (game_length * 5)) + game_length * 5
        # for sx in do_range(1, 5):
            # for sy in do_range(1, 5):
                # node.sector[sx][sy].arachnidN = 0
                # node.sector[sx][sy].skinnyN = 0
                # node.sector[sx][sy].radiation = "0"
                # node.sector[sx][sy].supply = "0"
                # for px in do_range(1, 10):
                    # for py in do_range(1, 10):
                        # node.sector[sx][sy].point[px][py] = "."
                    # # end for
                # # end for
                # node.chart[sx][sy].arachnidN = "."
                # node.chart[sx][sy].skinnyN = "."
                # node.chart[sx][sy].radiation = "."
                # node.chart[sx][sy].supply = "."
            # # end for
        # # end for
        node.rank = rank
        node.time_left = ((node.arachnidT + node.heavy_beamT) + ((4 - node.rank) * .25))
        node.SX = mod (clock (), 5) + 1
        node.SY = mod (clock (), 5) + 1
        node.PX = mod (clock (), 10) + 1
        node.PY = mod (clock (), 10) + 1
        node.sector[node.SX][node.SY].point[node.PX][node.PY] = TROOPER
        node.HE_bombN = mod (clock (), 6) + 10
        node.supplyN = mod (clock (), (5 - rank)) + 2
        for i in do_range(1, 6):
            node.supply[i].uses_left = 0
        # end for
        node.beacon.SX = mod (clock (), 5) + 1
        node.beacon.SY = mod (clock (), 5) + 1
        node.beacon.PX = mod (clock (), 10) + 1
        node.beacon.PY = mod (clock (), 10) + 1
        node.score.total = 0
        
        # /* Set up the ARACHNIDS */

        for x in do_range(1, node.arachnidT):
            it_was_not_placed = True
            while (it_was_not_placed):
                y = mod (clock (), 5) + 1
                z = mod (clock (), 5) + 1
                if ((y != node.SX) or (z != node.SY)) and (node.sector[y][z].arachnidN < 9):
                    node.Arachnid[x].SX = y
                    node.Arachnid[x].SY = z
                    y = mod (clock (), 10) + 1
                    z = mod (clock (), 10) + 1
                    if (node.sector[node.Arachnid[x].SX][node.Arachnid[x].SY].point[y][z] == "."):
                        node.Arachnid[x].PX = y
                        node.Arachnid[x].PY = z
                        node.Arachnid[x].life_pts = mod (clock (), rank * 100) + 100
                        node.sector[node.Arachnid[x].SX][node.Arachnid[x].SY].point[node.Arachnid[x].PX][node.Arachnid[x].PY] = ARACHNID
                        node.sector[node.Arachnid[x].SX][node.Arachnid[x].SY].arachnidN = node.sector[node.Arachnid[x].SX][node.Arachnid[x].SY].arachnidN + 1
                        it_was_not_placed = False
                    # end if
                # end if
            # end while
        # end for
        
        # /* Set up the SKINNIES */

        for x in do_range(1, node.skinnyT):
            it_was_not_placed = True
            while (it_was_not_placed):
                y = mod (clock (), 5) + 1
                z = mod (clock (), 5) + 1
                if ((y != node.SX) or (z != node.SY)) and (node.sector[y][z].skinnyN < 9):
                    node.Skinny[x].SX = y
                    node.Skinny[x].SY = z
                    y = mod (clock (), 10) + 1
                    z = mod (clock (), 10) + 1
                    if (node.sector[node.Skinny[x].SX][node.Skinny[x].SY].point[y][z] == "."):
                        node.Skinny[x].PX = y
                        node.Skinny[x].PY = z
                        node.Skinny[x].life_pts = mod (clock (), rank * 50) + 50
                        node.sector[node.Skinny[x].SX][node.Skinny[x].SY].skinnyN = node.sector[node.Skinny[x].SX][node.Skinny[x].SY].skinnyN + 1
                        node.sector[node.Skinny[x].SX][node.Skinny[x].SY].point[node.Skinny[x].PX][node.Skinny[x].PY] = SKINNY
                        it_was_not_placed = False
                    # end if
                # end if
            # end while
        # end for
        
        # /* Set up the HEAVY BEAMS */

        node.heavy_beamT = int (round ((node.arachnidT / 10.0), 0))
        for x in do_range(1, node.heavy_beamT):
            it_was_not_placed = True
            while (it_was_not_placed):
                y = mod (clock (), 5) + 1
                z = mod (clock (), 5) + 1
                if ((y != node.SX) or (z != node.SY)) and (node.sector[y][z].arachnidN < 9):
                    node.Heavy_beam[x].SX = y
                    node.Heavy_beam[x].SY = z
                    y = mod (clock (), 10) + 1
                    z = mod (clock (), 10) + 1
                    if (node.sector[node.Heavy_beam[x].SX][node.Heavy_beam[x].SY].point[y][z] == "."):
                        node.Heavy_beam[x].PX = y
                        node.Heavy_beam[x].PY = z
                        node.Heavy_beam[x].life_pts = mod (clock (), rank * 200) + 200
                        node.sector[node.Heavy_beam[x].SX][node.Heavy_beam[x].SY].point[node.Heavy_beam[x].PX][node.Heavy_beam[x].PY] = HEAVY_BEAM
                        node.sector[node.Heavy_beam[x].SX][node.Heavy_beam[x].SY].arachnidN = node.sector[node.Heavy_beam[x].SX][node.Heavy_beam[x].SY].arachnidN + 1
                        it_was_not_placed = False
                    # end if
                # end if
            # end while
        # end for
        
        # /* Set up the MISSILE_LAUNCHERS */

        node.missile_lT = int (round ((node.skinnyT / 5.0), 0))
        for x in do_range(1, node.missile_lT):
            it_was_not_placed = True
            while (it_was_not_placed):
                y = mod (clock (), 5) + 1
                z = mod (clock (), 5) + 1
                if ((y != node.SX) or (z != node.SY)) and (node.sector[y][z].skinnyN < 9):
                    node.Missile_l[x].SX = y
                    node.Missile_l[x].SY = z
                    y = mod (clock (), 10) + 1
                    z = mod (clock (), 10) + 1
                    if (node.sector[node.Missile_l[x].SX][node.Missile_l[x].SY].point[y][z] == "."):
                        node.Missile_l[x].PX = y
                        node.Missile_l[x].PY = z
                        node.Missile_l[x].life_pts = mod (clock (), rank * 150) + 150
                        node.sector[node.Missile_l[x].SX][node.Missile_l[x].SY].point[node.Missile_l[x].PX][node.Missile_l[x].PY] = MISSILE_L
                        node.sector[node.Missile_l[x].SX][node.Missile_l[x].SY].skinnyN = node.sector[node.Missile_l[x].SX][node.Missile_l[x].SY].skinnyN + 1
                        it_was_not_placed = False
                    # end if
                # end if
            # end while
        # end for

        # /* Set up the MOUNTAINS */

        for x in do_range(1, 5):
            for y in do_range(1, 5):
                z = mod (clock (), 10)
                for a in do_range(1, z):
                    it_was_not_placed = True
                    while (it_was_not_placed):
                        b = mod (clock (), 10) + 1
                        c = mod (clock (), 10) + 1
                        if (node.sector[x][y].point[b][c] == "."):
                            node.sector[x][y].point[b][c] = MOUNTAIN
                            it_was_not_placed = False
                        # end if
                    # end while
                # end for
            # end for
        # end for
          
        # /* Set up the SUPPLY_SHIPS *
        
        for x in do_range(1, node.supplyN):
            it_was_not_placed = True
            while (it_was_not_placed):
        # place_supply_ship:
                try:
                    y = mod (clock (), 5) + 1
                    z = mod (clock (), 5) + 1
                    if ((y != node.SX) or (z != node.SY)):
                        for a in do_range(1, x):
                        # do a = 1 to (x - 1);
                            if (y == node.supply[a].SX) and (z == node.supply[a].SY): raise goto_place_supply_ship
                        # end for
                        node.supply[x].SX = y
                        node.supply[x].SY = z
                        y = mod (clock (), 10) + 1
                        z = mod (clock (), 10) + 1
                        if (node.sector[node.supply[x].SX][node.supply[x].SY].point[y][z] == "."):
                            node.supply[x].PX = y
                            node.supply[x].PY = z
                            node.supply[x].uses_left = game_length
                            node.sector[node.supply[x].SX][node.supply[x].SY].point[node.supply[x].PX][node.supply[x].PY] = SUPPLY_SHIP
                            node.sector[node.supply[x].SX][node.supply[x].SY].supply = "S"
                            node.chart[node.supply[x].SX][node.supply[x].SY].supply = "S"
                            it_was_not_placed = False
                        # end if
                    # end if
                except goto_place_supply_ship:
                    pass
                # end try
            # end while
        # end for

        # /* Set up the BREACHES */

        while (node.breachN == 0):
            for x in do_range(1, 5):
                for y in do_range(1, 5):
                    z = 0
                    if (node.sector[x][y].arachnidN > 0): z = mod (clock (), 3) + 1
                    if (z == 1):
                        it_was_not_placed = True
                        while (it_was_not_placed):
                            b = mod (clock (), 10) + 1
                            c = mod (clock (), 10) + 1
                            if (node.sector[x][y].point[b][c] == "."):
                                node.breachN = node.breachN + 1
                                node.breach[node.breachN].SX = x
                                node.breach[node.breachN].SY = y
                                node.breach[node.breachN].PX = b
                                node.breach[node.breachN].PY = c
                                node.breach[node.breachN].engineer = mod (clock (), 250) + 250
                                node.breach[node.breachN].prisoners = max (0, mod (clock (), 5) - 3)
                                node.sector[x][y].point[b][c] = BREACH
                                it_was_not_placed = False
                            # end if
                        # end while
                    # end if
                # end for
            # end for
        # end while
        
        # /* Set up the FORTS */
        
        for x in do_range(1, 5):
            for y in do_range(1, 5):
                z = 0
                if (x != node.SX) or (y != node.SY): z = mod (clock (), 10) + 1
                if (z == 1):
                    it_was_not_placed = True
                    while (it_was_not_placed):
                        b = mod (clock (), 10) + 1
                        c = mod (clock (), 10) + 1
                        if (node.sector[x][y].point[b][c] == "."):
                            node.fortN = node.fortN + 1
                            node.fort[node.fortN].SX = x
                            node.fort[node.fortN].SY = y
                            node.fort[node.fortN].PX = b
                            node.fort[node.fortN].PY = c
                            node.fort[node.fortN].guard = mod (clock (), 250) + 250
                            a = mod (clock (), 10) + 1
                            # if (a == 1) and not node.secret_plans_found:
                                # node.secret_plans_found = True
                                # node.fort[node.fortN].secret_plans_here = True
                            # # end if
                            node.sector[x][y].point[b][c] = FORT
                            it_was_not_placed = False
                        # end if
                    # end while
                # end if
            # end for
        # end for
        
    def print_introduction(self, node, last_name):
        call. ioa_ ("^/*************************")
        call. ioa_ ("^/To: M.I. ^a ^a", RANK[node.rank], last_name)
        call. ioa_ ("Planetary Strike Mission")
        call. ioa_ ("Mission briefing:")
        call. ioa_ ("^10t^d Arachnids", node.arachnidT + node.heavy_beamT)
        call. ioa_ ("^10t?? Skinnies")
        call. ioa_.nnl ("^10t^d Supply ships:", node.supplyN)
        for x in do_range(1, node.supplyN):
            call. ioa_.nnl (" ^d - ^d^[,^]", node.supply[x].SX, node.supply[x].SY, (x != node.supplyN))
        # end for
        call. ioa_ ("^/Drop site: Sector ^d - ^d, Mark ^d - ^d", node.SX, node.SY, node.PX, node.PY)
        call. ioa_ ("You have ^.1f hours to complete your mission.  The retrieval beacn will", node.time_left)
        call. ioa_ ("land at Sector ^d - ^d, Mark ^d - ^d.  Good luck!", node.beacon.SX, node.beacon.SY, node.beacon.PX, node.beacon.PY)
        call. ioa_ ("^/*************************")
        
    def daemon(self, scip):
        Node = ssu_.get_info_ptr (scip)
        update_chart (Node)
        Node.score.total = calc_score (Node, "arachnids")
        Node.score.total = Node.score.total + calc_score (Node, "skinnies")
        Node.score.total = Node.score.total + calc_score (Node, "heavy_beams")
        Node.score.total = Node.score.total + calc_score (Node, "missile_ls")
        Node.score.total = Node.score.total + calc_score (Node, "mountains")
        Node.score.total = Node.score.total + calc_score (Node, "supplies")
        Node.score.total = Node.score.total + calc_score (Node, "prisoners")
        if (Node.score.total >= Node.nuke_bonus_score):
            call. ioa_ ("^/***BONUS NUKE BOMB awarded -- Score: ^d", Node.score.total)
            Node.nuke_bonus_score = Node.nuke_bonus_score + 5000
            Node.nuke_bombN = Node.nuke_bombN + 1
        # end if
        if (Node.time_left < 1.1) and (not Node.beacon.landed):
            call. ioa_ ("^/\"...To the everlasting glory of the infantry, shines the name, shines the name^/name of Rodger Young!\"  Retrieval Beacon has landed at Sector ^d - ^d.", Node.beacon.SX, Node.beacon.SY)
            Node.time_left = 2.5
            call. ioa_ ("^/Retrieval time: ^.1f hrs.", Node.time_left)
            Node.sector[Node.beacon.SX][Node.beacon.SY].point[Node.beacon.PX][Node.beacon.PY] = BEACON
            Node.beacon.landed = True
        # end if
        if (Node.SX == Node.beacon.SX) and (Node.SY == Node.beacon.SY) and (Node.PX == Node.beacon.PX) and (Node.PY == Node.beacon.PY) and Node.beacon.landed:
            call. ioa_ ("^/Retrieval successful!")
            Node.score.success_ratio = round (((Node.score.arachnids_Xed + Node.score.heavy_beams_Xed) / float(Node.arachnidT + Node.heavy_beamT)) * 100, 0)
            if (Node.score.success_ratio > 50): Node.score.rank_bonus = Node.rank * 100
            Node.score.skinny_prisoners = (Node.skinnyT + Node.missile_lT) - (Node.score.skinnies_Xed + Node.missile_ls_Xed)
            call. ioa_ ("^3x*************************")
            call. ioa_ ("^/Your mission yielded a success ratio of ^d%", Node.score.success_ratio)
            if (Node.score.skinny_prionsers > 0): call. ioa_ ("The remaining ^d Skinnies surrender.", Node.score.skinny_prisoners)
            if (Node.score.success_ratio == 100): call. ioa_ ("You will be recommended for promotion.")
            call. ioa_ ("Aecturnae gloriae peditum...")
            call. ssu_.execute_string (scip, "score -all", code)
            call. ioa_ ("^/*************************")
            call. ssu_.abort_subsystem (scip, (0))
        elif (Node.time_left < .1):
            call. ioa_ ("^/Retrieval complete.")
            Node.score.captured_penalty = -500
            you_lose ("no_time")
        # end if
        if (not H_or_M_present (Node.distress.SX, Node.distress.SY, Node)) and Node.distress.notified:
            Node.distress.SX = 0
            Node.distress.SY = 0
            Node.distress.which_supply = 0
            Node.distress.notified = False
        # end if
        attack_supply_ships (Node)
        
    def scanner(self, scip, node):
        if not node.equipment.scanner.working:
            call. ioa_ ("^/Scanner is damaged.")
            return
        # end if
        call. ioa_ ("^/SCANNER READOUT: Sector ^d - ^d^/", node.SX, node.SY)
        for x in do_range(node.SX - 1, node.SX + 1):
            for y in do_range(node.SY - 1, node.SY + 1):
                if (x < 1) or (x > 5) or (y < 1) or (y > 5): call. ioa_.nnl ("   ----")
                else:
                    call. ioa_.nnl ("^3x^d^d^a^a", node.sector[x][y].arachnidN, node.sector[x][y].skinnyN, node.sector[x][y].radiation, node.sector[x][y].supply)
                    node.chart[x][y].arachnidN = ltrim (char_(node.sector[x][y].arachnidN))
                    node.chart[x][y].skinnyN = ltrim (char_(node.sector[x][y].skinnyN))
                    node.chart[x][y].radiation = node.sector[x][y].radiation
                    node.chart[x][y].supply = node.sector[x][y].supply
                # end if
            # end for
            call. ioa_ ()
        # end for
        
    def chart(self, scip, node):
        call. ioa_ ("^/PLANETARY CHART:")
        call. ioa_ ("^/     1      2      3      4      5")
        call. ioa_ ("    --------------------------------")
        for x in do_range(1, 5):
            call. ioa_.nnl ("^d:  ", x)
            for y in do_range(1, 5):
                call. ioa_.nnl ("^a^a^a^a^3x", node.chart[x][y].arachnidN, node.chart[x][y].skinnyN, node.chart[x][y].radiation, node.chart[x][y].supply)
            # end for
            call. ioa_ ()
        # end for
        call. ioa_ ("^/LOCUS PROXIMITY: Sector ^d - ^d, Mark ^d - ^d", node.SX, node.SY, node.PX, node.PY)        
        
    def snooper(self, scip, node):
        
        def snooper_status(line_no):
            if (line_no == 2): call. ioa_.nnl ("^5xSuit condition:^25t^d pts.", node.suit_pts)
            elif (line_no == 3): call. ioa_.nnl ("^5xBody condition:^25t^d pts.", node.body_pts)
            elif (line_no == 4): call. ioa_.nnl ("^5xBooster energy:^25t^d units", node.jet_energy)
            elif (line_no == 5): call. ioa_.nnl ("^5xFlamer energy:^25t^d units", node.flamer_energy)
            elif (line_no == 6): call. ioa_.nnl ("^5xHE bombs left:^25t^d", node.HE_bombN)
            elif (line_no == 7): call. ioa_.nnl ("^5xNuke bombs left:^25t^d", node.nuke_bombN)
            elif (line_no == 8): call. ioa_.nnl ("^5xArachnids left:^25t^d", (node.arachnidT + node.heavy_beamT - node.score.arachnids_Xed - node.score.heavy_beams_Xed))
            elif (line_no == 9): call. ioa_.nnl ("^5xTime left:^25t^.1f hrs.", node.time_left)
            else: return
        #-- end def snooper_status
        
        print_status = False
        
        if not node.equipment.snooper.working:
            call. ioa_ ("^/Snooper is damaged.")
            return
        # end if
        call. ssu_.arg_count (scip, argn)
        for x in range(argn.val):
            call. ssu_.arg_ptr (scip, x, argp) ; arg = argp.val
            if (arg == "-status") or (arg == "-st"): print_status = True
            elif (substr (arg, 1, 1) == "-"): call. ssu_.abort_line (scip, error_table_.badopt, "^a", arg)
            else: call. ssu_.abort_line (scip, (0), "^/^5xUsage: snooper {-status}")
        # end for
        
        call. ioa_ ("^/SECTOR ^d - ^d, MARK ^d - ^d", node.SX, node.SY, node.PX, node.PY)
        call. ioa_ ("^/    1 2 3 4 5 6 7 8 9 10")
        for x in do_range(1, 10):
            if (x < 10): call. ioa_.nnl (" ^d ", x)
            else: call. ioa_.nnl ("10 ")
            for y in do_range(1, 10):
                call. ioa_.nnl (" ^a", node.sector[node.SX][node.SY].point[x][y])
            # end for
            if print_status and (x > 1): snooper_status(x)
            call. ioa_ ()
        # end for
        node.chart[node.SX][node.SY].arachnidN = str(node.sector[node.SX][node.SY].arachnidN)
        node.chart[node.SX][node.SY].skinnyN = str(node.sector[node.SX][node.SY].skinnyN)
        node.chart[node.SX][node.SY].radiation = node.sector[node.SX][node.SY].radiation
        node.chart[node.SX][node.SY].supply = node.sector[node.SX][node.SY].supply
        
    def status(self, scip, node):

        all_switch     = False
        damage_switch  = False
        general_status = False
        damage_report  = False
        I_want_to_see  = [False] * (23+1)

        call. ssu_.arg_count (scip, argn)
        if (argn.val == 0):
            general_status = True
            I_want_to_see = [True] * (23+1)
        # end if
        for x in range(argn.val):
            call. ssu_.arg_ptr (scip, x, argp) ; arg = argp.val
            if (arg == "-damage") or (arg == "-dmg"): damage_switch = True
            elif (arg == "-all") or (arg == "-a"): all_switch = True
            elif (substr (arg, 1, 1) == "-"): call. ssu_.abort_line (scip, (0), "^/^5xUsage: status {item} {-damage {item}} {-all}")
            elif (not damage_switch):
                if (arg == "locus") or (arg == "loc"): I_want_to_see[LOCUS] = True
                elif (arg == "suit"): I_want_to_see[SUIT] = True
                elif (arg == "body"): I_want_to_see[BODY] = True
                elif (arg == "boosters") or (arg == "jets") or (arg == "jet_boosters"): I_want_to_see[BOOSTER_ENERGY] = True
                elif (arg == "flamer_rifle") or (arg == "flamer") or (arg == "rifle"): I_want_to_see[FLAMER_ENERGY] = True
                elif (arg == "he_bombs") or (arg == "he"): I_want_to_see[HE_BOMBN] = True
                elif (arg == "nuke_bombs") or (arg == "nukes"): I_want_to_see[NUKE_BOMBN] = True
                elif (arg == "arachnids") or (arg == "bugs"): I_want_to_see[BUGS_LEFT] = True
                elif (arg == "time"): I_want_to_see[TIME_LEFT] = True
                else: call. ssu_.abort_line (scip, (0), "^/^xNo status for ""^a"".", arg)
                general_status = True
            else:
                if (arg == "scanner"): I_want_to_see[SCANNER] = True
                elif (arg == "snooper"): I_want_to_see[SNOOPER] = True
                elif (arg == "flamer_rifle") or (arg == "flamer") or (arg == "rifle"): I_want_to_see[FLAMER_RIFLE] = True
                elif (arg == "he_launcher") or (arg == "he"): I_want_to_see[HE_LAUNCHER] = True
                elif (arg == "nuke_launcher") or (arg == "nuker"): I_want_to_see[NUKE_LAUNCHER] = True
                elif (arg == "listening_device") or (arg == "ld"): I_want_to_see[LISTENING_DEV] = True
                elif (arg == "jet_boosters") or (arg == "boosters") or (arg == "jets"): I_want_to_see[JET_BOOSTERS] = True
                else: call. ssu_.abort_line (scip, (0), "^/^5xNo such device. ^a", arg)
                damage_report = True
            # end if
        # end for
        if all_switch:
            general_status = True
            damage_report = True
            I_want_to_see = [True] * (23+1)
        # end if
        if damage_switch and (not damage_report):
            damage_report = True
            for x in do_range(10, 16):
                I_want_to_see[x] = True
            # end for
        # end if
        if general_status:
            call. ioa_ ("^/Trooper status report:")
            if I_want_to_see[LOCUS]: call. ioa_ ("^3xLocus proximity:^25tSector ^d - ^d, Mark ^d - ^d", node.SX, node.SY, node.PX, node.PY)
            if I_want_to_see[SUIT]: call. ioa_ ("^3xSuit condition:^25t^d pts.", node.suit_pts)
            if I_want_to_see[BODY]: call. ioa_ ("^3xBody condition:^25t^d pts.", node.body_pts)
            if I_want_to_see[BOOSTER_ENERGY]: call. ioa_ ("^3xBooster energy:^25t^d units", node.jet_energy)
            if I_want_to_see[FLAMER_ENERGY]: call. ioa_ ("^3xFlamer energy:^25t^d units", node.flamer_energy)
            if I_want_to_see[HE_BOMBN]: call. ioa_ ("^3xHE bombs left:^25t^d", node.HE_bombN)
            if I_want_to_see[NUKE_BOMBN]: call. ioa_ ("^3xNuke bombs left:^25t^d", node.nuke_bombN)
            if I_want_to_see[BUGS_LEFT]: call. ioa_ ("^3xArachnids left:^25t^d", (node.arachnidT + node.heavy_beamT - node.score.arachnids_Xed - node.score.heavy_beams_Xed))
            if I_want_to_see[TIME_LEFT]: call. ioa_ ("^3xTime left:^25t^.1f hrs.", node.time_left)
        # end if
        if damage_report:
            call. ioa_ ("^/Trooper damage report:")
            if I_want_to_see[SCANNER]:
                call. ioa_ ("^3xScanner^25t^[WORKING^]^[DAMAGED^]", node.equipment.scanner.working, not node.equipment.scanner.working)
                if (not node.equipment.scanner.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.scanner.repair_time, max (0, node.equipment.scanner.repair_time - 1))
            # end if
            if I_want_to_see[SNOOPER]:
                call. ioa_ ("^3xSnooper^25t^[WORKING^]^[DAMAGED^]", node.equipment.snooper.working, not node.equipment.snooper.working)
                if (not node.equipment.snooper.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.snooper.repair_time, max (0, node.equipment.snooper.repair_time - 1))
            # end if
            if I_want_to_see[JET_BOOSTERS]:
                call. ioa_ ("^3xJet boosters^25t^[WORKING^]^[DAMAGED^]", node.equipment.jet_boosters.working, not node.equipment.jet_boosters.working)
                if (not node.equipment.jet_boosters.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.jet_boosters.repair_time, max (0, node.equipment.jet_boosters.repair_time - 1))
            # end if
            if I_want_to_see[FLAMER_RIFLE]:
                call. ioa_ ("^3xFlamer rifle^25t^[WORKING^]^[DAMAGED^]", node.equipment.flamer.working, not node.equipment.flamer.working)
                if (not node.equipment.flamer.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.flamer.repair_time, max (0, node.equipment.flamer.repair_time - 1))
            # end if
            if I_want_to_see[HE_LAUNCHER]:
                call. ioa_ ("^3xHE launcher^25t^[WORKING^]^[DAMAGED^]", node.equipment.HE_launcher.working, not node.equipment.HE_launcher.working)
                if (not node.equipment.HE_launcher.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.HE_launcher.repair_time, max (0, node.equipment.HE_launcher.repair_time - 1))
            # end if
            if I_want_to_see[NUKE_LAUNCHER]:
                call. ioa_ ("^3xNuke launcher^25t^[WORKING^]^[DAMAGED^]", node.equipment.nuke_launcher.working, not node.equipment.nuke_launcher.working)
                if (not node.equipment.nuke_launcher.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.nuke_launcher.repair_time, max (0, node.equipment.nuke_launcher.repair_time - 1))
            # end if
            if I_want_to_see[LISTENING_DEV]:
                call. ioa_ ("^3xListening dev^25t^[WORKING^]^[DAMAGED^]", node.equipment.listening_dev.working, not node.equipment.listening_dev.working)
                if (not node.equipment.listening_dev.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.listening_dev.repair_time, max (0, node.equipment.listening_dev.repair_time - 1))
                  
    def fly(self, scip, node):
    
        target_SX      = fixed.bin . init (0) . local
        target_SY      = fixed.bin . init (0) . local
        target_PX      = fixed.bin . parm . init (0)
        target_PY      = fixed.bin . parm . init (0)
        real_target_PX = fixed.bin . init (0) . local
        real_target_PY = fixed.bin . init (0) . local
        original_SX    = fixed.bin . init (0) . local
        original_SY    = fixed.bin . init (0) . local
        original_PX    = fixed.bin . init (0) . local
        original_PY    = fixed.bin . init (0) . local
        
        call. ssu_.arg_count (scip, argn)
        if (argn.val != 4): call. ssu_.abort_line (scip, (0), "^/^5xUsage: fly Sector_X Sector_Y Mark_X Mark_Y")
        for x in range(4):
            call. ssu_.arg_ptr (scip, x, argp) ; arg = argp.val
            if (verify (arg, "1234567890") != 0): call. ssu_.abort_line (scip, (0), "^/^5xInvalid coordinate. ^a", arg)
            if (x == 0): target_SX = decimal (arg)
            elif (x == 1): target_SY = decimal (arg)
            elif (x == 2): real_target_PX = decimal (arg)
            else: real_target_PY = decimal (arg)
        # end for
        if (target_SX > 5) or (target_SX == 0) or (target_SY > 5) or (target_SY == 0) or (real_target_PX > 10) or (real_target_PX == 0) or (real_target_PY > 10) or (real_target_PY == 0): call. ssu_.abort_line (scip, (0), "^/^5xFlight not possible with given vectors.")
        original_SX = node.SX
        original_SY = node.SY
        original_PX = node.PX
        original_PY = node.PY
        
        if (target_SX == original_SX) and (target_SY == original_SY): call. ssu_.abort_line (scip, (0), "^/^5xUse the \"jump\" request for movement within a sector.")
        if not node.equipment.jet_boosters.working:
            call. ioa_ ("^/Jet boosters are damaged.")
            return
        # end if
        if (node.jet_energy < calc_move_cost (node.SX, node.SY, node.PX, node.PY, target_SX, target_SY, real_target_PX, real_target_PY)):
            call. ioa_ ("^/Jet boosters do not have sufficient energy remaining for flight.")
            return
        # end if
        if (node.time_left < calc_move_time (node.SX, node.SY, node.PX, node.PY, target_SX, target_SY, real_target_PX, real_target_PY)):
            call. ioa_ ("^/Time left: ^.1f hrs., Flight time: ^.1f", node.time_left, calc_move_time (node.SX, node.SY, node.PX, node.PY, target_SX, target_SY, real_target_PX, real_target_PY))
            return
        # end if
        get_target_point (node.SX, node.SY, node.PX, node.PY, target_SX, target_SY, target_PX, target_PY)
        move ("Flight", node, target_PX.val, target_PY.val)
        node.SX = target_SX
        node.SY = target_SY
        node.PX = real_target_PX
        node.PY = real_target_PY
        got_there_ok (node)
        node.jet_energy = node.jet_energy - calc_move_cost (original_SX, original_SY, original_PX, original_PY, node.SX, node.SY, node.PX, node.PY)
        node.time_left = node.time_left - calc_move_time (original_SX, original_SY, original_PX, original_PY, node.SX, node.SY, node.PX, node.PY)
        node.sector[original_SX][original_SY].point[original_PX][original_PY] = "."
        if node.was_in_rad:
            node.sector[original_SX][original_SY].point[original_PX][original_PY] = RADIATION
            if not node.sitting_in_rad: node.was_in_rad = False
        # end if
        if node.sitting_in_rad: node.was_in_rad = True
        node.sector[node.SX][node.SY].point[node.PX][node.PY] = TROOPER
        call. ioa_ ("^/***LOCUS PROXIMITY: Sector ^d - ^d, Mark ^d - ^d", node.SX, node.SY, node.PX, node.PY)
        enemy_attack (node)
        
    def jump(self, scip, node):
        call. ssu_.arg_count (scip, argn)
        if (argn.val != 2): call. ssu_.abort_line (scip, (0), "^/^5xUsage: jump Mark_X, Mark_Y")
        for x in range(2):
            call. ssu_.arg_ptr (scip, x, argp) ; arg = argp.val
            if (verify (arg, "1234567890") != 0): call. ssu_.abort_line (scip, (0), "^/^5xInvalid coordinate. ^a", arg)
            if (x == 0): target_PX = decimal (arg)
            else: target_PY = decimal (arg)
        # end for
        if (target_PX == 0) or (target_PX > 10) or (target_PY == 0) or (target_PY > 10): call. ssu_.abort_line (scip, (0), "^/^5xJump not possible with given vectors.")

        if (node.PX == target_PX) and (node.PY == target_PY):
            call. ioa_ ("^/Mark ^d - ^d is already your current position.", target_PX, target_PY)
            return
        # end if
        if (node.suit_pts < 10):
            call. ioa_ ("^/Suit strength insufficient for jump to Mark ^d - ^d.", target_PX, target_PY)
            if (node.jet_energy < calc_move_cost (node.SX, node.SY, node.PX, node.PY, node.SX, node.SY, target_PX, target_PY)): return
            call. ioa_ ("Using Jet booster power...")
            node.jet_energy = node.jet_energy - calc_move_cost (node.SX, node.SY, node.PX, node.PY, node.SX, node.SY, target_PX, target_PY)
        # end if
        if (node.time_left < calc_move_time (node.SX, node.SY, node.PX, node.PY, node.SX, node.SY, target_PX, target_PY)):
            call. ioa_ ("^/Time left: ^.1f hrs., Jump time: ^.1f hrs.", node.time_left, calc_move_time (node.SX, node.SY, node.PX, node.PY, node.SX, node.SY, target_PX, target_PY))
            return
        # end if
        original_PX = node.PX
        original_PY = node.PY
        move ("Jump", node, target_PX, target_PY)
        node.PX = target_PX
        node.PY = target_PY
        node.time_left = node.time_left - calc_move_time (node.SX, node.SY, original_PX, original_PY, node.SX, node.SY, node.PX, node.PY)
        node.sector[node.SX][node.SY].point[original_PX][original_PY] = "."
        if node.was_in_rad:
            node.sector[node.SX][node.SY].point[original_PX][original_PY] = RADIATION
            if (not node.sitting_in_rad): node.was_in_rad = False
        # end if
        if node.sitting_in_rad: node.was_in_rad = True
        node.sector[node.SX][node.SY].point[node.PX][node.PY] = TROOPER
        enemy_attack (node)
    
    def flamer(self, scip, node):
        class goto_FLAME_THEM_BUGGERS(Exception): pass
        
        energy_tally    = fixed.bin . parm . init (0)
        enemyN          = fixed.bin . init (0) . local
        where_X         = Dim(50+1) (fixed.bin . init (0))
        where_Y         = Dim(50+1) (fixed.bin . init (0))
        allotted_energy = Dim(50+1) (fixed.bin . init (0))
        type            = Dim(50+1) (char (10) . init (""))

        if (not node.equipment.flamer.working):
            call. ioa_ ("^/Flamer rifle is damaged.")
            return
        # end if
        if (not enemies_present (node)):
            call. ioa_ ("^/There are no enemies present.")
            return
        # end if
        call. ioa_ ("^/Flamer energy remaining: ^d units^[^/^]", node.flamer_energy, (node.flamer_energy > 0))
        try:
            for x in do_range(1, 10):
                for y in do_range(1, 10):
                    if (node.flamer_energy == 0): raise goto_FLAME_THEM_BUGGERS
                    if (node.sector[node.SX][node.SY].point[x][y] == ARACHNID):
                        allot_flamer_energy ("Arachnid", x, y, energy_tally, node)
                        enemyN = enemyN + 1
                        where_X[enemyN] = x
                        where_Y[enemyN] = y
                        allotted_energy[enemyN] = energy_tally.val
                        type[enemyN] = "Arachnid"
                    elif (node.sector[node.SX][node.SY].point[x][y] == SKINNY):
                        allot_flamer_energy ("Skinny", x, y, energy_tally, node)
                        enemyN = enemyN + 1
                        where_X[enemyN] = x
                        where_Y[enemyN] = y
                        allotted_energy[enemyN] = energy_tally.val
                        type[enemyN] = "Skinny"
                    elif (node.sector[node.SX][node.SY].point[x][y] == HEAVY_BEAM):
                        allot_flamer_energy ("Heavy Beam", x, y, energy_tally, node)
                        enemyN = enemyN + 1
                        where_X[enemyN] = x
                        where_Y[enemyN] = y
                        allotted_energy[enemyN] = energy_tally.val
                        type[enemyN] = "Heavy Beam"
                    elif (node.sector[node.SX][node.SY].point[x][y] == MISSILE_L):
                        allot_flamer_energy ("Missile-L", x, y, energy_tally, node)
                        enemyN = enemyN + 1
                        where_X[enemyN] = x
                        where_Y[enemyN] = y
                        allotted_energy[enemyN] = energy_tally.val
                        type[enemyN] = "Missile-L"
                    # end if
                # end for
            # end for
            energy_tally.val = 0
            for x in do_range(1, enemyN):
                energy_tally.val = energy_tally.val + allotted_energy[x]
            # end for
            if (energy_tally.val == 0): return

        except goto_FLAME_THEM_BUGGERS:
            pass
        # end try
        
        for x in do_range(1, enemyN):
            if (x == 1): call. ioa_ ()
            flame_that_sucker (type[x], where_X[x], where_Y[x], allotted_energy[x], node)
        # end for
        node.time_left = max (0, node.time_left - .1)
        enemy_attack (node)
        
    def score(self, scip, node):
        all_switch = False
        I_want_to_see = [False] * (23+1)
        
        call. ssu_.arg_count (scip, argn)
        if (argn.val == 0):
            call. ioa_ ("^/Your score:^10x^d", node.score.total)
            return
        # end if
        for x in range(argn.val):
            call. ssu_.arg_ptr (scip, x, argp) ; arg = argp.val
            if (arg == "-all") or (arg == "-a"): all_switch = True
            elif (substr (arg, 1, 1) == "-"): call. ssu_.abort_line (scip, error_table_.badopt, "^a", arg)
            elif (arg == "arachnids") or (arg == "bugs"): I_want_to_see[ARACHNID_SCORE] = True
            elif (arg == "skinnies"): I_want_to_see[SKINNY_SCORE] = True
            elif (arg == "heavy_beams"): I_want_to_see[HEAVY_BEAM_SCORE] = True
            elif (arg == "missile_ls"): I_want_to_see[MISSILE_L_SCORE] = True
            elif (arg == "mountains") or (arg == "mts"): I_want_to_see[MOUNTAIN_SCORE] = True
            elif (arg == "supplies"): I_want_to_see[SUPPLY_SCORE] = True
            elif (arg == "prisoners"): I_want_to_see[PRISONER_SCORE] = True
            else: call. ssu_.abort_line (scip, (0), "^/^5xNo score of \"^a\".", arg)
        # end for
        if all_switch: I_want_to_see = [True] * (23+1)
        node.score.total = node.score.total + node.score.death_penalty + node.score.captured_penalty + node.score.skinny_prisoners
        node.score.total = node.score.total + max (0, round (node.score.success_ratio * 20, 0))
        if all_switch and (node.score.total == 0):
            call. ioa_ ("^/Your score:^10x0")
            return
        # end if
        call. ioa_ ("^[^/Your score:^]", all_switch)
        if I_want_to_see[ARACHNID_SCORE]:
            if (node.score.arachnids_Xed > 0): call. ioa_ ("^3x^d Arachnid warriors^40t^d", node.score.arachnids_Xed, calc_score (node, "arachnids"))
            elif (not all_switch): call. ioa_ ("No Arachnid warriors destroyed.")
        # end if
        if I_want_to_see[SKINNY_SCORE]:
            if (node.score.skinnies_Xed > 0): call. ioa_ ("^3x^d Skinny warriors^40t^d", node.score.skinnies_Xed, calc_score (node, "skinnies"))
            elif (not all_switch): call. ioa_ ("No Skinny warriors destroyed.")
        # end if
        if all_switch and (node.score.skinny_prisoners > 0): call. ioa_ ("^3x^d Skinny prisoners^40t^d", node.score.skinny_prisoners, node.score.skinny_prisoners)
        if I_want_to_see[HEAVY_BEAM_SCORE]:
            if (node.score.heavy_beams_Xed > 0): call. ioa_ ("^3x^d Heavy weapon beams^40t^d", node.score.heavy_beams_Xed, calc_score (node, "heavy_beams"))
            elif (not all_switch): call. ioa_ ("No Heavy weapon beams destroyed.")
        # end if
        if I_want_to_see[MISSILE_L_SCORE]:
            if (node.score.missile_ls_Xed > 0): call. ioa_ ("^3x^d Missile launchers^40t^d", node.score.missile_ls_Xed, calc_score (node, "missile_ls"))
            elif (not all_switch): call .ioa_ ("No Missile launchers destroyed.")
        # end if
        if I_want_to_see[PRISONER_SCORE]:
            if (node.score.prisoners_rescued > 0): call. ioa_ ("^3x^d Prisoners rescued^40t^d", node.score.prisoners_rescued, calc_score (node, "prisoners"))
            elif (not all_switch): call. ioa_ ("No Arachnid warriors destroyed.")
        # end if
        if I_want_to_see[MOUNTAIN_SCORE]:
            if (node.score.mountains_Xed > 0): call. ioa_ ("^3x^d Mountains destroyed^40t^d", node.score.mountains_Xed, calc_score (node, "mountains"))
            elif (not all_switch): call. ioa_ ("No Mountains destroyed.")
        # end if
        if I_want_to_see[SUPPLY_SCORE]:
            if (node.score.supplies_Xed > 0): call. ioa_ ("^3x^d supply ships destroyed^40t^d", node.score.supplies_Xed, calc_score (node, "supplies"))
            elif (not all_switch): call. ioa_ ("No supply ships destroyed.")
        # end if
        if all_switch and (node.score.success_ratio > 0): call. ioa_ ("^3xMission success bonus^40t^d", round (node.score.success_ratio * 20, 0))
        if all_switch and (node.score.rank_bonus > 0): call. ioa_ ("^3xRank bonus (^a level)^40t^d", RANK[node.rank], node.score.rank_bonus)
        if all_switch and (node.score.death_penalty < 0): call. ioa_ ("^3xPenalty for getting killed^39t-1000")
        if all_switch and (node.score.captured_penalty < 0): call. ioa_ ("^3xPenalty for getting captured^40t-500")
        if all_switch: call. ioa_ ("^30t------^/Total:^40t^d", node.score.total)
        
    def launch(self, scip, node):

        burst           = fixed.bin . init (0) . local
        BURST_MAX       = fixed.bin . init (0) . local
        weapon          = char (5) . init ("") . local
        input           = char ('*') . parm . init ("")
        where_X         = Dim(3+1) (fixed.bin . init (0))
        where_Y         = Dim(3+1) (fixed.bin . init (0))
        
        call. ssu_.arg_count (scip, argn)
        if (argn.val == 0): call. ssu_.abort_line (scip, (0), "^/^5xUsage: launch weapon")
        call. ssu_.arg_ptr (scip, 0, argp) ; arg = argp.val
        weapon = arg
        if (weapon == "he"):
            try:
                if (not node.equipment.HE_launcher.working):
                    call. ioa_ ("^/HE launcher is damaged.")
                    return
                # end if
                if (argn.val > 1):
                    call. ssu_.arg_ptr (scip, 1, argp) ; arg = argp.val
                    if (verify (arg, "1234567890") != 0): call. ssu_.abort_line (scip, (0), "^/^5x#_of_bombs must be a positive integer. ^a", arg)
                    BURST_MAX = decimal (arg)
                    if (BURST_MAX > 3): call. ssu_.abort_line (scip, (0), "^/^5xMaximum of 3 HE bombs per burst.")
                    elif (argn.val > (BURST_MAX * 2) + 2): call. ssu_.abort_line (scip, (0), "^/^5xToo many coordinates given.")
                    for x in do_range(2, BURST_MAX * 2, 2):
                        for y in do_range(1, 2):
                            if (x + y > argn.val) and (y == 2): call. ssu_.abort_line (scip, (0), "^/^5xHE Usage: launch he {#_of_bombs} {target_coordinates}")
                            elif (x + y > argn.val): raise goto_get_bomb_targets
                            call. ssu_.arg_ptr (scip, x + y - 1, argp) ; arg = argp.val
                            if (verify (arg, "1234567890") != 0): call. ssu_.abort_line (scip, (0), "^/^5xInvalid coordinate. ^a", arg)
                            elif (decimal (arg) == 0) or (decimal (arg) > 10): call. ssu_.abort_line (scip, (0), "^/^5xInvalid coordinate. ^a", arg)
                            elif (y == 1):
                                burst = burst + 1
                                where_X[burst] = decimal (arg)
                            else: where_Y[burst] = decimal (arg)
                        # end for
                    # end for
                else:
                    get_no_of_bombs = True
                    while get_no_of_bombs:
                        get_no_of_bombs = False
# get_no_of_bombs:
                        input.val = "NULL"
                        call. ioa_ ("^/HE bombs remaining: ^d", node.HE_bombN)
                        if (node.HE_bombN == 0): return
                        while (verify (input.val, "1234567890") != 0):
                            call. ioa_.nnl ("How many to launch? ")
                            getline (input)
                            if (input.val == ""): input.val = "NULL"
                        # end while
                        BURST_MAX = decimal (input.val)
                        if (BURST_MAX == 0): call. ssu_.abort_line (scip, (0))
                        elif (BURST_MAX > 3):
                            call. ioa_ ("Maximum of 3 HE bombs per burst.")
                            get_no_of_bombs = True # goto get_no_of_bombs
                        # end if
                    # end while
                # end if
            except goto_get_bomb_targets:
                pass
            # end try
# get_bomb_targets:
            if (BURST_MAX > node.HE_bombN):
                call. ioa_ ("^/HE bombs remaining: ^d", node.HE_bombN)
                return
            # end if
            for x in do_range(burst + 1, BURST_MAX):
                if (x == burst + 1): call. ioa_ ()
                if (BURST_MAX == 1): get_target_for_bomb (where_X[x], where_Y[x], 0)
                else: get_target_for_bomb (where_X[x], where_Y[x], x)
            # end for
        
        elif (weapon == "nuke"):
            if (argn.val != 1) and (argn.val != 3): call. ssu_.abort_line (scip, (0), "^/^5xNuke Usage: launch nuke {Target_X Target_Y}")
            if (not node.equipment.nuke_launcher.working):
                call. ioa_ ("^/Nuke launcher is damaged.")
                return
            # end if
            if (argn.val == 3):
                call. ssu_.arg_ptr (scip, 1, argp) ; arg = argp.val
                if (verify (arg, "1234567890") != 0): call. ssu_.abort_line (scip, (0), "^/^5xInvalid coordinate. ^a", arg)
                where_X[1] = decimal (arg)
                call. ssu_.arg_ptr (scip, 2, argp) ; arg = argp.val
                if (verify (arg, "1234567890") != 0): call. ssu_.abort_line (scip, (0), "^/^5xInvalid coordinate. ^a", arg)
                where_Y[1] = decimal (arg)
                BURST_MAX = 1
            # end if
            if (BURST_MAX == 0):
                call. ioa_ ("^/Nuke bombs remaining: ^d", node.nuke_bombN)
                if (node.nuke_bombN == 0): return
                else: call. ioa_ ()
                BURST_MAX = 1
                get_target_for_bomb (where_X[1], where_Y[1], 0)
            # end if
        
        else: call. ssu_.abort_line (scip, (0), "^/^5xNo such launcher. ^a", weapon)
        
        for x in do_range(1, BURST_MAX):
            launch_it (weapon, where_X[x], where_Y[x], x, node)
            if (weapon == "he"): node.HE_bombN = node.HE_bombN - 1
            else: node.nuke_bombN = node.nuke_bombN - 1
        # end for
        enemy_attack (node)
        
    def repair(self, scip, node):

        device_idx          = fixed.bin . init (0) . local
        device              = Dim(7+1) (char (30) . init (""))
        scanner_repair_sw   = bit (1) . init (b'0') . local
        flamer_repair_sw    = bit (1) . init (b'0') . local
        he_repair_sw        = bit (1) . init (b'0') . local
        nuker_repair_sw     = bit (1) . init (b'0') . local
        ld_repair_sw        = bit (1) . init (b'0') . local
        jets_repair_sw      = bit (1) . init (b'0') . local
        
        call. ssu_.arg_count (scip, argn)
        if (argn.val == 0): call. ssu_.abort_line (scip, (0), "^/^5xUsage: repair device")
        for x in do_range(1, argn.val):
            call. ssu_.arg_ptr (scip, x, argp) ; arg = argp.val
            if (arg == "scanner") and (not scanner_repair_sw):
                scanner_repair_sw = b'1'
                device_idx = device_idx + 1
                device[device_idx] = "scanner"
            elif (arg == "snooper") and (not snooper_repair_sw):
                snooper_repair_sw = b'1'
                device_idx = device_idx + 1
                device[device_idx] = "snooper"
            elif ((arg == "flamer_rifle") or (arg == "flamer")) and (not flamer_repair_sw):
                flamer_repair_sw = b'1'
                device_idx = device_idx + 1
                device[device_idx] = "flamer_rifle"
            elif ((arg == "he_launcher") or (arg == "he")) and (not he_repair_sw):
                he_repair_sw = b'1'
                device_idx = device_idx + 1
                device[device_idx] = "he_launcher"
            elif ((arg == "nuke_launcher") or (arg == "nuker")) and (not nuker_repair_sw):
                nuker_repair_sw = b'1'
                device_idx = device_idx + 1
                device[device_idx] = "nuke_launcher"
            elif ((arg == "listening_device") or (arg == "ld")) and (not ld_repair_sw):
                ld_repair_sw = b'1'
                device_idx = device_idx + 1
                device[device_idx] = "listening_device"
            elif ((arg == "jet_boosters") or (arg == "jets")) and (not jets_repair_sw):
                jets_repair_sw = b'1'
                device_idx = device_idx + 1
                device[device_idx] = "jet_boosters"
            else: call. ssu_.abort_line (scip, (0), "^/^5xNo such device. ^a", arg)
        # end for
        for x in do_range(1, device_idx):
            repair_damage (device[x], node)
        # end for
        
    def rest(self, scip, node):
        rest_time       = fixed.dec (5, 2) . init (0) . local
        number_suffix   = [ "st", "nd", "rd" ] + ["th"]*17 + \
                          [ "st", "nd", "rd" ] + ["th"]*7  + \
                          [ "st", "nd", "rd" ] + ["th"]*7  + \
                          [ "st", "nd", "rd" ] + ["th"]*7
        
        call. ssu_.arg_count (scip, argn)
        if (argn.val != 1): call. ssu_.abort_line (scip, (0), "^/^5xUsage: rest hours")
        call. ssu_.arg_ptr (scip, 0, argp) ; arg = argp.val
        if (verify (arg, ".1234567890") != 0): call. ssu_.abort_line (scip, (0), "^/^5xRest time must be numeric. ^a", arg)
        rest_time = convert_to_real (arg)
        if (rest_time > node.time_left):
            call. ioa_ ("^/Time left: ^.1f hrs., Rest time: ^.1f hrs.", node.time_left, rest_time)
            return
        # end if
        call. ioa_ ("^/Rested.")
        node.body_pts = min (20, node.body_pts + round (rest_time * 4, 0))
        node.time_left = node.time_left - rest_time
        for x in do_range(1, max(1, trunc(rest_time))):
            if (trunc (rest_time) > 1) and enemies_present (node): call. ioa_ ("^/^d^a hour:", x, number_suffix[x - 1])
            enemy_attack (node)
        # end for
        
    def transfer(self, scip, node):
    
        transfer_energy     = fixed.bin . init (0) . local
        to_device           = char (12) . init ("") . local
        true_xfer_energy    = fixed.bin . init (0) . local

        call. ssu_.arg_count (scip, argn)
        if (argn.val != 2): call. ssu_.abort_line (scip, (0), "^/^5xUsage: transfer device energy_amount")
        call. ssu_.arg_ptr (scip, 0, argp) ; arg = argp.val
        if (arg == "jet_boosters") or (arg == "jets"): to_device = "jet_boosters"
        elif (arg == "flamer_rifle") or (arg == "flamer"): to_device = "flamer_rifle"
        else: call. ssu_.abort_line (scip, (0), "^/^5xDevice must be either \"flamer\" or \"jets\".")
        call. ssu_.arg_ptr (scip, 1, argp) ; arg = argp.val
        if (verify (arg, "1234567890") != 0): call. ssu_.abort_line (scip, (0), "^/^5xEnergy_amount must be a positive integer. ^a", arg)
        transfer_energy = decimal (arg)
        if (to_device == "jet_boosters") and (transfer_energy > node.flamer_energy):
            call. ioa_ ("^/Flamer energy remaining: ^d units.  No transfer.", node.flamer_energy)
            return
        elif (to_device == "flamer_rifle") and (transfer_energy > node.jet_energy):
            call. ioa_ ("^/Jet booster energy remaining: ^d units.  No transfer.", node.jet_energy)
            return
        # end if
        if (node.time_left < .2):
            call. ioa_ ("^/Time left: ^.1f hrs., Transfer time: 0.2 hrs.", node.time_left)
            return
        # end if
        if (to_device == "jet_boosters"):
            true_xfer_energy = min (transfer_energy, 1000 - node.jet_energy)
            call. ioa_ ("^/^d units transferred to Jet boosters.", true_xfer_energy)
            if (true_xfer_energy < transfer_energy): call. ioa_ ("Flamer retains remaining ^d units.", transfer_energy - true_xfer_energy)
            node.jet_energy = node.jet_energy + true_xfer_energy
            node.flamer_energy = node.flamer_energy - true_xfer_energy
            call. ioa_ ("^/Jet booster energy:  ^d units", node.jet_energy)
            call. ioa_ ("Flamer rifle energy: ^d units", node.flamer_energy)
        elif (to_device == "flamer_rifle"):
            true_xfer_energy = min (transfer_energy, 1000 - node.flamer_energy)
            call. ioa_ ("^/^d units transferred to Flamer rifle.", true_xfer_energy)
            if (true_xfer_energy < transfer_energy): call. ioa_ ("Jets retains remaining ^d units.", transfer_energy - true_xfer_energy)
            node.flamer_energy = node.flamer_energy + true_xfer_energy
            node.jet_energy = node.jet_energy - true_xfer_energy
            call. ioa_ ("^/Flamer rifle energy: ^d units", node.flamer_energy)
            call. ioa_ ("Jet booster energy:  ^d units", node.jet_energy)
        # end if
        node.time_left = node.time_left - .2
        
    def encamp(self, scip, node):
        if node.encamped:
            call. ioa_ ("^/You are already encamped.")
            return
        # end if
        if (node.time_left < 1):
            call. ioa_ ("^/Time left: ^.1f hrs., Encampment time: 1.0 hrs.", node.time_left)
            return
        # end if
        for x in do_range(node.PX - 1, node.PX + 1):
            for y in do_range(node.PY - 1, node.PY + 1):
                if (x > 0) and (x < 11) and (y > 0) and (y < 11):
                    if node.sector[node.SX][node.SY].point[x][y] == SUPPLY_SHIP:
                        call. ioa_ ("^/Encamped.")
                        node.encamped = True
                        for z in do_range(1, node.supplyN):
                            if (node.supply[z].SX == node.SX) and (node.supply[z].SY == node.SY) and (node.supply[z].PX == x) and (node.supply[z].PY == y):
                                node.supply[z].uses_left = node.supply[z].uses_left - 1
                                if (node.supply[z].uses_left == 0):
                                    call. ioa_ ("Supply ship exhausted -> returning to base.")
                                    node.encamped = False
                                    node.sector[node.SX][node.SY].point[x][y] = "."
                                    if (node.SX == node.distress.SX) and (node.SY == node.distress.SY):
                                        node.distress.SX = 0
                                        node.distress.SY = 0
                                    # end if
                                    node.sector[node.SX][node.SY].supply = "0"
                                # end if
                            # end if
                        # end for
                        node.suit_pts = min (50, max (node.suit_pts * 2, node.suit_pts + 10))
                        node.jet_energy = min (1000, max (node.jet_energy * 2, node.jet_energy + 500))
                        node.flamer_energy = min (1000, max (node.flamer_energy * 2, node.flamer_energy + 500))
                        node.HE_bombN = min (10, max (node.HE_bombN * 2, node.HE_bombN + 5))
                        node.time_left = node.time_left - 1
                        return
                    # end if
                # end if
            # end for
        # end for
        call. ioa_ ("^/You are not adjacent to a supply ship.")
        
    def rescue(self, scip, node):
        bdex  = fixed.bin . init (0) . local
        input = parm("")
        
        for x in do_range(node.PX - 1, node.PX + 1):
            for y in do_range(node.PY - 1, node.PY + 1):
                if (node.sector[node.SX][node.SY].point[x][y] == BREACH):
                    for z in do_range(1, node.breachN):
                        if (node.breach[z].SX == node.SX) and (node.breach[z].SY == node.SY) and (node.breach[z].PX == x) and (node.breach[z].PY == y): bdex = z
                    # end for
                # end if
            # end for
        # end for
        if (bdex == 0):
            call. ioa_ ("^/You are not adjacent to a breach.")
            return
        # end if
        while (node.breach[bdex].engineer > 0):
            x = round (node.breach[bdex].engineer / 100, 0)
            if (x > 0):
                call. ioa_.nnl ("^/***ENGINEER in breach:^33t")
                damage_the_trooper (x, node)
            else: call. ioa_ ()
            x = mod (clock (), (1 + node.suit_pts + node.body_pts)) + 30
            call. ioa_ ("***TROOPER attack^33t^d pts. to Engineer", x)
            node.breach[bdex].engineer = max (0, node.breach[bdex].engineer - x)
            if (node.breach[bdex].engineer == 0): call. ioa_ ("***ENGINEER in breach destroyed.")
            else:
                call. ioa_.nnl ("^/Do you wish to continue the rescue? ")
                yes_no (input)
                if (input.val == "no") or (input.val == "n"):
                    enemy_attack (node)
                    return
                # end if
            # end if
            node.time_left = node.time_left - .1
            call. sst_.daemon (scip)
        # end while
        if (node.breach[bdex].prisoners == 1): call. ioa_ ("^/Prisoner rescued.")
        else: call. ioa_ ("^/No prisoner here.")
        node.score.prisoners_rescued = node.score.prisoners_rescued + node.breach[bdex].prisoners
        enemy_attack (node)
        
    def quit(self, scip, node):
        see_score = False
        input     = parm("")

        call. ssu_.arg_count (scip, argn)
        for x in range(argn.val):
            call. ssu_.arg_ptr (scip, x, argp) ; arg = argp.val
            if (arg == "-score") or (arg == "-sc"): see_score = True
            else: call. ssu_.abort_line (scip, (0), "^/^5xUsage: quit {-score}")
        # end for
        call. ioa_.nnl ("^/Do you wish to quit? ")
        yes_no (input)
        if (input.val == "y") or (input.val == "yes"):
            if see_score: call. ssu_.execute_string (scip, "score -all", code)
            else: call. ssu_.execute_string (scip, "score", code)
            call. ssu_.abort_subsystem (scip, (0))
        elif (input.val == "n") or (input.val == "no"): call. ssu_.abort_line (scip, (0))
        call. ssu_.abort_subsystem (scip, (0))
        
    def self_identify(self, scip, node):
        call. ioa_ ("^a ^a", MAIN, sst_data_.version_string)
        
    def listen(self, scip, node):
        pass
        
    def signal_for_help(self, scip, node):
        pass
    
def calc_move_cost(from_SX, from_SY, from_PX, from_PY, to_SX, to_SY, to_PX, to_PY):
    energy_cost = fixed.bin . init (0) . local

    energy_cost = abs (from_SX - to_SX) + abs (from_SY - to_SY)
    energy_cost = round (energy_cost / 2.0, 0) * 100
    energy_cost = round ((abs (from_PX - to_PX) + abs (from_PY - to_PY)) / 2.0, 0) * 10 + energy_cost
    return (energy_cost)
    
def calc_move_time(from_SX, from_SY, from_PX, from_PY, to_SX, to_SY, to_PX, to_PY):
    time_cost = fixed.dec (5, 2) . init (0) . local

    time_cost = abs (from_SX - to_SX) + abs (from_SY - to_SY)
    time_cost = round (time_cost / 4.0, 2)
    time_cost = time_cost + round ((abs (from_PX - to_PX) + abs (from_PY - to_PY)) / 100.0, 2)
    return (time_cost)

def get_target_point(from_SX, from_SY, from_PX, from_PY, to_SX, to_SY, tp_X, tp_Y):
    if (to_SX < from_SX):
        tp_X.val = 1
        if (to_SY < from_SY): tp_Y.val = 1
        elif (to_SY == from_SY): tp_Y.val = from_PY
        else: tp_Y.val = 10
    elif (to_SX == from_SX):
        tp_X.val = from_PX
        if (to_SY < from_SY): tp_Y.val = 1
        else: tp_Y.val = 10
    else:
        tp_X.val = 10
        if (to_SY < from_SY): tp_Y.val = 1
        elif (to_SY == from_SY): tp_Y.val = from_PY
        else: tp_Y.val = 10
    # end if
    
def move(type, node, to_PX, to_PY):
    slope_X            = fixed.bin . parm . init (0)
    slope_Y            = fixed.bin . parm . init (0)
    original_PX        = fixed.bin . init (0) . local
    original_PY        = fixed.bin . init (0) . local
    new_X              = fixed.bin . init (0) . local
    new_Y              = fixed.bin . init (0) . local
    Point              = char (1) . init ("") . local
    blank_line_printed = False
    
    node.encamped = False
    original_PX = node.PX
    original_PY = node.PY
    while ((node.PX != to_PX) or (node.PY != to_PY)):
        get_slope (node.PX, node.PY, to_PX, to_PY, slope_X, slope_Y)
        new_X = node.PX + slope_X.val
        new_Y = node.PY + slope_Y.val
        if (node.sector[node.SX][node.SY].point[new_X][new_Y] == ".") or (node.sector[node.SX][node.SY].point[new_X][new_Y] == BEACON):
            node.PX = new_X
            node.PY = new_Y
            node.sitting_in_rad = False
        elif (node.sector[node.SX][node.SY].point[new_X][new_Y] == RADIATION):
            if (not blank_line_printed):
                call. ioa_ ()
                blank_line_printed = True
            # end if
            call. ioa_.nnl ("***RADIATION at Mark ^d - d.  ", new_X, new_Y)
            damage_the_trooper ((mode (clock (), 10) + 1), node)
            node.PX = new_X
            node.PY = new_Y
            node.sitting_in_rad = True
        else:
            node.jet_energy = node.jet_energy - calc_move_cost (node.SX, node.SY, original_PX, original_PY, node.SX, node.SY, node.PX, node.PY)
            node.jet_energy = max (0, node.jet_energy - 50)
            Point = node.sector[node.SX][node.SY].point[new_X][new_Y]
            if (Point == MOUNTAIN): call. ioa_ ("^/***MOUNTAIN at Mark ^d - ^d.  ^a discontinued.", new_X, new_Y, type)
            elif (Point == FORT): call. ioa_ ("^/***FORT at Mark ^d - ^d.  ^a discontinued.", new_X, new_Y, type)
            elif (Point == SUPPLY_SHIP): call. ioa_ ("^/***SUPPLY at Mark ^d - ^d.  ^a discontinued.", new_X, new_Y, type)
            elif (Point == BREACH): call. ioa_ ("^/***BREACH at Mark ^d - ^d.  ^a discontinued.", new_X, new_Y, type)
            elif (Point == ARACHNID): call. ioa_ ("^/***ARACHNID at Mark ^d - ^d.  ^a discontinued.", new_X, new_Y, type)
            elif (Point == SKINNY): call. ioa_ ("^/***SKINNY at Mark ^d - ^d.  ^a discontinued.", new_X, new_Y, type)
            elif (Point == HEAVY_BEAM): call. ioa_ ("^/***HEAVY BEAM at Mark ^d - ^d.  ^a discontinued.", new_X, new_Y, type)
            elif (Point == MISSILE_L): call. ioa_ ("^/***MISSILE-L at Mark ^d - ^d.  ^a discontinued.", new_X, new_Y, type)
            node.sector[node.SX][node.SY].point[original_PX][original_PY] = "."
            node.sector[node.SX][node.SY].point[node.PX][node.PY] = TROOPER
            call. ioa_ ("^/***LOCUS PROXIMITY: Sector ^d - ^d, Mark ^d - ^d", node.SX, node.SY, node.PX, node.PY)
            enemy_attack (node)
            call. ssu_.abort_line (scip, (0))
        # end if
    # end while
     
def get_slope(from_X, from_Y, to_X, to_Y, slope_X, slope_Y):
    if (to_X < from_X): slope_X.val = -1
    elif (to_X > from_X): slope_X.val = 1
    else: slope_X.val = 0
    if (to_Y < from_Y): slope_Y.val = -1
    elif (to_Y > from_Y): slope_Y.val = 1
    else: slope_Y.val = 0
    
def update_chart(node):
    pass
    
def you_lose (reason):
    pass
    
def H_or_M_present (sx, sy, node):
    return True

def got_there_ok(node):
    pass
    
def enemies_present(node):
    return True
    
def allot_flamer_energy(type, x, y, energy_tally, node):
    energy_tally.val = 10
    pass
    
def flame_that_sucker(type, where_X, where_Y, allotted_energy, node):
    call. ioa_ ("^a at Mark ^d - ^d (^d energy needed)", type, where_X, where_Y, allotted_energy)
    pass

def launch_it(weapon, where_X, where_Y, x, node):
    pass
    
def get_target_for_bomb(where_X, where_Y, x):
    pass
    
def enemy_attack(node):
    pass
    
def attack_supply_ships(node):
    pass

def damage_the_trooper(damage, node):
    pass
    
def calc_score(node, type):
    return 0
    
def repair_damage(device, node):
    pass
    
def yes_no(input):
    pass
    
def convert_to_real(x):
    return float_(x)
    