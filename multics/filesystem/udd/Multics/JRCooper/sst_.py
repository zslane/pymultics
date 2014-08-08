
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

class goto_place_supply_ship(NonLocalGoto): pass

class sst_(Subroutine):

    def __init__(self):
        super(sst_, self).__init__(self.__class__.__name__)

    def set_up_game(self, node, game_length, rank):
        # These are fields that don't retain their initial values defined in sst_node_.py
        node.suit_pts = 50
        node.body_pts = 20
        node.jet_energy = 1000
        node.flamer_energy = 1000
        node.nuke_bombN = 4
        node.nuke_bonus_score = 5000
        node.score.success_ratio = -1
        
        node.arachnidT = mod (clock (), (game_length * 10)) + game_length * 10
        node.skinnyT = mod (clock (), (game_length * 5)) + game_length * 5
        for sx in range(5):
            for sy in range(5):
                node.sector[sx][sy].arachnidN = 0
                node.sector[sx][sy].skinnyN = 0
                node.sector[sx][sy].radiation = "0"
                node.sector[sx][sy].supply = "0"
                for px in range(10):
                    for py in range(10):
                        node.sector[sx][sy].point[px][py] = "."
                    # end for
                # end for
                node.chart[sx][sy].arachnidN = "."
                node.chart[sx][sy].skinnyN = "."
                node.chart[sx][sy].radiation = "."
                node.chart[sx][sy].supply = "."
            # end for
        # end for
        node.rank = rank
        node.time_left = ((node.arachnidT + node.heavy_beamT) + ((4 - node.rank) * .25))
        node.SX = mod (clock (), 5) + 1
        node.SY = mod (clock (), 5) + 1
        node.PX = mod (clock (), 10) + 1
        node.PY = mod (clock (), 10) + 1
        node.sector[node.SX - 1][node.SY - 1].point[node.PX - 1][node.PY - 1] = TROOPER
        node.HE_bombN = mod (clock (), 6) + 10
        node.supplyN = mod (clock (), (5 - rank)) + 2
        for i in range(6):
            node.supply[i].uses_left = 0
        # end for
        node.beacon.SX = mod (clock (), 5) + 1
        node.beacon.SY = mod (clock (), 5) + 1
        node.beacon.PX = mod (clock (), 10) + 1
        node.beacon.PY = mod (clock (), 10) + 1
        node.score.total = 0
        
        # /* Set up the ARACHNIDS */

        for x in range(node.arachnidT):
            it_was_not_placed = True
            while (it_was_not_placed):
                y = mod (clock (), 5) + 1
                z = mod (clock (), 5) + 1
                if ((y != node.SX - 1) or (z != node.SY - 1)) and (node.sector[y - 1][z - 1].arachnidN < 9):
                    node.Arachnid[x].SX = y
                    node.Arachnid[x].SY = z
                    y = mod (clock (), 10) + 1
                    z = mod (clock (), 10) + 1
                    if (node.sector[node.Arachnid[x].SX - 1][node.Arachnid[x].SY - 1].point[y - 1][z - 1] == "."):
                        node.Arachnid[x].PX = y
                        node.Arachnid[x].PY = z
                        node.Arachnid[x].life_pts = mod (clock (), rank * 100) + 100
                        node.sector[node.Arachnid[x].SX - 1][node.Arachnid[x].SY - 1].point[node.Arachnid[x].PX - 1][node.Arachnid[x].PY - 1] = ARACHNID
                        node.sector[node.Arachnid[x].SX - 1][node.Arachnid[x].SY - 1].arachnidN = node.sector[node.Arachnid[x].SX - 1][node.Arachnid[x].SY - 1].arachnidN + 1
                        it_was_not_placed = False
                    # end if
                # end if
            # end while
        # end for
        
        # /* Set up the SKINNIES */

        for x in range(node.skinnyT):
            it_was_not_placed = True
            while (it_was_not_placed):
                y = mod (clock (), 5) + 1
                z = mod (clock (), 5) + 1
                if ((y != node.SX - 1) or (z != node.SY - 1)) and (node.sector[y - 1][z - 1].skinnyN < 9):
                    node.Skinny[x].SX = y
                    node.Skinny[x].SY = z
                    y = mod (clock (), 10) + 1
                    z = mod (clock (), 10) + 1
                    if (node.sector[node.Skinny[x].SX - 1][node.Skinny[x].SY - 1].point[y - 1][z - 1] == "."):
                        node.Skinny[x].PX = y
                        node.Skinny[x].PY = z
                        node.Skinny[x].life_pts = mod (clock (), rank * 50) + 50
                        node.sector[node.Skinny[x].SX - 1][node.Skinny[x].SY - 1].skinnyN = node.sector[node.Skinny[x].SX - 1][node.Skinny[x].SY - 1].skinnyN + 1
                        node.sector[node.Skinny[x].SX - 1][node.Skinny[x].SY - 1].point[node.Skinny[x].PX - 1][node.Skinny[x].PY - 1] = SKINNY
                        it_was_not_placed = False
                    # end if
                # end if
            # end while
        # end for
        
        # /* Set up the HEAVY BEAMS */

        node.heavy_beamT = int (round ((node.arachnidT / 10.0), 0))
        for x in range(node.heavy_beamT):
            it_was_not_placed = True
            while (it_was_not_placed):
                y = mod (clock (), 5) + 1
                z = mod (clock (), 5) + 1
                if ((y != node.SX - 1) or (z != node.SY - 1)) and (node.sector[y - 1][z - 1].arachnidN < 9):
                    node.Heavy_beam[x].SX = y
                    node.Heavy_beam[x].SY = z
                    y = mod (clock (), 10) + 1
                    z = mod (clock (), 10) + 1
                    if (node.sector[node.Heavy_beam[x].SX - 1][node.Heavy_beam[x].SY - 1].point[y - 1][z - 1] == "."):
                        node.Heavy_beam[x].PX = y
                        node.Heavy_beam[x].PY = z
                        node.Heavy_beam[x].life_pts = mod (clock (), rank * 200) + 200
                        node.sector[node.Heavy_beam[x].SX - 1][node.Heavy_beam[x].SY - 1].point[node.Heavy_beam[x].PX - 1][node.Heavy_beam[x].PY - 1] = HEAVY_BEAM
                        node.sector[node.Heavy_beam[x].SX - 1][node.Heavy_beam[x].SY - 1].arachnidN = node.sector[node.Heavy_beam[x].SX - 1][node.Heavy_beam[x].SY - 1].arachnidN + 1
                        it_was_not_placed = False
                    # end if
                # end if
            # end while
        # end for
        
        # /* Set up the MISSILE_LAUNCHERS */

        node.missile_lT = int (round ((node.skinnyT / 5.0), 0))
        for x in range(node.missile_lT):
            it_was_not_placed = True
            while (it_was_not_placed):
                y = mod (clock (), 5) + 1
                z = mod (clock (), 5) + 1
                if ((y != node.SX - 1) or (z != node.SY - 1)) and (node.sector[y - 1][z - 1].skinnyN < 9):
                    node.Missile_l[x].SX = y
                    node.Missile_l[x].SY = z
                    y = mod (clock (), 10) + 1
                    z = mod (clock (), 10) + 1
                    if (node.sector[node.Missile_l[x].SX - 1][node.Missile_l[x].SY - 1].point[y - 1][z - 1] == "."):
                        node.Missile_l[x].PX = y
                        node.Missile_l[x].PY = z
                        node.Missile_l[x].life_pts = mod (clock (), rank * 150) + 150
                        node.sector[node.Missile_l[x].SX - 1][node.Missile_l[x].SY - 1].point[node.Missile_l[x].PX - 1][node.Missile_l[x].PY - 1] = MISSILE_L
                        node.sector[node.Missile_l[x].SX - 1][node.Missile_l[x].SY - 1].skinnyN = node.sector[node.Missile_l[x].SX - 1][node.Missile_l[x].SY - 1].skinnyN + 1
                        it_was_not_placed = False
                    # end if
                # end if
            # end while
        # end for

        # /* Set up the MOUNTAINS */

        for x in range(5):
            for y in range(5):
                z = mod (clock (), 10)
                for a in range(z):
                    it_was_not_placed = True
                    while (it_was_not_placed):
                        b = mod (clock (), 10) + 1
                        c = mod (clock (), 10) + 1
                        if (node.sector[x][y].point[b - 1][c - 1] == "."):
                            node.sector[x][y].point[b - 1][c - 1] = MOUNTAIN
                            it_was_not_placed = False
                        # end if
                    # end while
                # end for
            # end for
        # end for
          
        # /* Set up the SUPPLY_SHIPS *
        
        for x in range(node.supplyN):
            it_was_not_placed = True
            while (it_was_not_placed):
                try:
                    y = mod (clock (), 5) + 1
                    z = mod (clock (), 5) + 1
                    if ((y != node.SX) or (z != node.SY)):
                        for a in range(x):
                        # do a = 1 to (x - 1);
                            if (y == node.supply[a].SX) and (z == node.supply[a].SY): raise goto_place_supply_ship
                        # end for
                        node.supply[x].SX = y
                        node.supply[x].SY = z
                        y = mod (clock (), 10) + 1
                        z = mod (clock (), 10) + 1
                        if (node.sector[node.supply[x].SX - 1][node.supply[x].SY - 1].point[y - 1][z - 1] == "."):
                            node.supply[x].PX = y
                            node.supply[x].PY = z
                            node.supply[x].uses_left = game_length
                            node.sector[node.supply[x].SX - 1][node.supply[x].SY - 1].point[node.supply[x].PX - 1][node.supply[x].PY - 1] = SUPPLY_SHIP
                            node.sector[node.supply[x].SX - 1][node.supply[x].SY - 1].supply = "S"
                            node.chart[node.supply[x].SX - 1][node.supply[x].SY - 1].supply = "S"
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
            for x in range(5):
                for y in range(5):
                    z = 0
                    if (node.sector[x][y].arachnidN > 0): z = mod (clock (), 3) + 1
                    if (z == 1):
                        it_was_not_placed = True
                        while (it_was_not_placed):
                            b = mod (clock (), 10) + 1
                            c = mod (clock (), 10) + 1
                            if (node.sector[x][y].point[b - 1][c - 1] == "."):
                                node.breachN = node.breachN + 1
                                node.breach[node.breachN - 1].SX = x
                                node.breach[node.breachN - 1].SY = y
                                node.breach[node.breachN - 1].PX = b
                                node.breach[node.breachN - 1].PY = c
                                node.breach[node.breachN - 1].engineer = mod (clock (), 250) + 250
                                node.breach[node.breachN - 1].prisoners = max (0, mod (clock (), 5) - 3)
                                node.sector[x][y].point[b - 1][c - 1] = BREACH
                                it_was_not_placed = False
                            # end if
                        # end while
                    # end if
                # end for
            # end for
        # end while
        
        # /* Set up the FORTS */
        
        for x in range(5):
            for y in range(5):
                z = 0
                if (x != node.SX - 1) or (y != node.SY - 1): z = mod (clock (), 10) + 1
                if (z == 1):
                    it_was_not_placed = True
                    while (it_was_not_placed):
                        b = mod (clock (), 10) + 1
                        c = mod (clock (), 10) + 1
                        if (node.sector[x][y].point[b - 1][c - 1] == "."):
                            node.fortN = node.fortN + 1
                            node.fort[node.fortN - 1].SX = x
                            node.fort[node.fortN - 1].SY = y
                            node.fort[node.fortN - 1].PX = b
                            node.fort[node.fortN - 1].PY = c
                            node.fort[node.fortN - 1].guard = mod (clock (), 250) + 250
                            a = mod (clock (), 10) + 1
                            # if (a == 1) and not node.secret_plans_found:
                                # node.secret_plans_found = True
                                # node.fort[node.fortN - 1].secret_plans_here = True
                            # # end if
                            node.sector[x][y].point[b - 1][c - 1] = FORT
                            it_was_not_placed = False
                        # end if
                    # end while
                # end if
            # end for
        # end for
        
    def print_introduction(self, node, last_name):
        call. ioa_ ("^/*************************")
        call. ioa_ ("^/To: M.I. ^a ^a", RANK[node.rank - 1], last_name)
        call. ioa_ ("Planetary Strike Mission")
        call. ioa_ ("Mission briefing:")
        call. ioa_ ("^10t^d Arachnids", node.arachnidT + node.heavy_beamT)
        call. ioa_ ("^10t?? Skinnies")
        call. ioa_.nnl ("^10t^d Supply ships:", node.supplyN)
        for x in range(node.supplyN):
            call. ioa_.nnl (" ^d - ^d^[,^]", node.supply[x].SX, node.supply[x].SY, (x != node.supplyN - 1))
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
            Node.sector[Node.beacon.SX - 1][Node.beacon.SY - 1].point[Node.beacon.PX - 1][Node.beacon.PY - 1] = BEACON
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
        for x in range(node.SX - 1, node.SX + 2):
            for y in range(node.SY - 1, node.SY + 2):
                if (x < 1) or (x > 5) or (y < 1) or (y > 5): call. ioa_.nnl ("   ----")
                else:
                    call. ioa_.nnl ("^3x^d^d^a^a", node.sector[x - 1][y - 1].arachnidN, node.sector[x - 1][y - 1].skinnyN, node.sector[x - 1][y - 1].radiation, node.sector[x - 1][y - 1].supply)
                    node.chart[x - 1][y - 1].arachnidN = str(node.sector[x - 1][y - 1].arachnidN)
                    node.chart[x - 1][y - 1].skinnyN = str(node.sector[x - 1][y - 1].skinnyN)
                    node.chart[x - 1][y - 1].radiation = node.sector[x - 1][y - 1].radiation
                    node.chart[x - 1][y - 1].supply = node.sector[x - 1][y - 1].supply
                # end if
            # end for
            call. ioa_ ()
        # end for
        
    def chart(self, scip, node):
        call. ioa_ ("^/PLANETARY CHART:")
        call. ioa_ ("^/     1      2      3      4      5")
        call. ioa_ ("    --------------------------------")
        for x in range(5):
            call. ioa_.nnl ("^d:  ", x + 1)
            for y in range(5):
                call. ioa_.nnl ("^a^a^a^a^3x", node.chart[x][y].arachnidN, node.chart[x][y].skinnyN, node.chart[x][y].radiation, node.chart[x][y].supply)
            # end for
            call. ioa_ ()
        # end for
        call. ioa_ ("^/LOCUS PROXIMITY: Sector ^d - ^d, Mark ^d - ^d", node.SX, node.SY, node.PX, node.PY)        
        
    def snooper(self, scip, node):
        
        def snooper_status(line_no):
            if (line_no == 1): call. ioa_.nnl ("^5xSuit condition:^25t^d pts.", node.suit_pts)
            elif (line_no == 2): call. ioa_.nnl ("^5xBody condition:^25t^d pts.", node.body_pts)
            elif (line_no == 3): call. ioa_.nnl ("^5xBooster energy:^25t^d units", node.jet_energy)
            elif (line_no == 4): call. ioa_.nnl ("^5xFlamer energy:^25t^d units", node.flamer_energy)
            elif (line_no == 5): call. ioa_.nnl ("^5xHE bombs left:^25t^d", node.HE_bombN)
            elif (line_no == 6): call. ioa_.nnl ("^5xNuke bombs left:^25t^d", node.nuke_bombN)
            elif (line_no == 7): call. ioa_.nnl ("^5xArachnids left:^25t^d", (node.arachnidT + node.heavy_beamT - node.score.arachnids_Xed - node.score.heavy_beams_Xed))
            elif (line_no == 8): call. ioa_.nnl ("^5xTime left:^25t^.1f hrs.", node.time_left)
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
        for x in range(10):
            if (x < 9): call. ioa_.nnl (" ^d ", x + 1)
            else: call. ioa_.nnl ("10 ")
            for y in range(10):
                call. ioa_.nnl (" ^a", node.sector[node.SX - 1][node.SY - 1].point[x][y])
            # end for
            if print_status and (x > 0): snooper_status(x)
            call. ioa_ ()
        # end for
        node.chart[node.SX - 1][node.SY - 1].arachnidN = str(node.sector[node.SX - 1][node.SY - 1].arachnidN)
        node.chart[node.SX - 1][node.SY - 1].skinnyN = str(node.sector[node.SX - 1][node.SY - 1].skinnyN)
        node.chart[node.SX - 1][node.SY - 1].radiation = node.sector[node.SX - 1][node.SY - 1].radiation
        node.chart[node.SX - 1][node.SY - 1].supply = node.sector[node.SX - 1][node.SY - 1].supply
        
    def status(self, scip, node):

        all_switch     = False
        damage_switch  = False
        general_status = False
        damage_report  = False
        I_want_to_see  = [False] * 23

        call. ssu_.arg_count (scip, argn)
        if (argn.val == 0):
            general_status = True
            I_want_to_see = [True] * 23
        # end if
        for x in range(argn.val):
            call. ssu_.arg_ptr (scip, x, argp) ; arg = argp.val
            if (arg == "-damage") or (arg == "-dmg"): damage_switch = True
            elif (arg == "-all") or (arg == "-a"): all_switch = True
            elif (substr (arg, 1, 1) == "-"): call. ssu_.abort_line (scip, (0), "^/^5xUsage: status {item} {-damage {item}} {-all}")
            elif (not damage_switch):
                if (arg == "locus") or (arg == "loc"): I_want_to_see[LOCUS - 1] = True
                elif (arg == "suit"): I_want_to_see[SUIT - 1] = True
                elif (arg == "body"): I_want_to_see[BODY - 1] = True
                elif (arg == "boosters") or (arg == "jets") or (arg == "jet_boosters"): I_want_to_see[BOOSTER_ENERGY - 1] = True
                elif (arg == "flamer_rifle") or (arg == "flamer") or (arg == "rifle"): I_want_to_see[FLAMER_ENERGY - 1] = True
                elif (arg == "he_bombs") or (arg == "he"): I_want_to_see[HE_BOMBN - 1] = True
                elif (arg == "nuke_bombs") or (arg == "nukes"): I_want_to_see[NUKE_BOMBN - 1] = True
                elif (arg == "arachnids") or (arg == "bugs"): I_want_to_see[BUGS_LEFT - 1] = True
                elif (arg == "time"): I_want_to_see[TIME_LEFT - 1] = True
                else: call. ssu_.abort_line (scip, (0), "^/^xNo status for ""^a"".", arg)
                general_status = True
            else:
                if (arg == "scanner"): I_want_to_see[SCANNER - 1] = True
                elif (arg == "snooper"): I_want_to_see[SNOOPER - 1] = True
                elif (arg == "flamer_rifle") or (arg == "flamer") or (arg == "rifle"): I_want_to_see[FLAMER_RIFLE - 1] = True
                elif (arg == "he_launcher") or (arg == "he"): I_want_to_see[HE_LAUNCHER - 1] = True
                elif (arg == "nuke_launcher") or (arg == "nuker"): I_want_to_see[NUKE_LAUNCHER - 1] = True
                elif (arg == "listening_device") or (arg == "ld"): I_want_to_see[LISTENING_DEV - 1] = True
                elif (arg == "jet_boosters") or (arg == "boosters") or (arg == "jets"): I_want_to_see[JET_BOOSTERS - 1] = True
                else: call. ssu_.abort_line (scip, (0), "^/^5xNo such device. ^a", arg)
                damage_report = True
            # end if
        # end for
        if all_switch:
            general_status = True
            damage_report = True
            I_want_to_see = [True] * 23
        # end if
        if damage_switch and (not damage_report):
            damage_report = True
            for x in range(10, 16 + 1):
                I_want_to_see[x - 1] = True
            # end for
        # end if
        if general_status:
            call. ioa_ ("^/Trooper status report:")
            if I_want_to_see[LOCUS - 1]: call. ioa_ ("^3xLocus proximity:^25tSector ^d - ^d, Mark ^d - ^d", node.SX, node.SY, node.PX, node.PY)
            if I_want_to_see[SUIT - 1]: call. ioa_ ("^3xSuit condition:^25t^d pts.", node.suit_pts)
            if I_want_to_see[BODY - 1]: call. ioa_ ("^3xBody condition:^25t^d pts.", node.body_pts)
            if I_want_to_see[BOOSTER_ENERGY - 1]: call. ioa_ ("^3xBooster energy:^25t^d units", node.jet_energy)
            if I_want_to_see[FLAMER_ENERGY - 1]: call. ioa_ ("^3xFlamer energy:^25t^d units", node.flamer_energy)
            if I_want_to_see[HE_BOMBN - 1]: call. ioa_ ("^3xHE bombs left:^25t^d", node.HE_bombN)
            if I_want_to_see[NUKE_BOMBN - 1]: call. ioa_ ("^3xNuke bombs left:^25t^d", node.nuke_bombN)
            if I_want_to_see[BUGS_LEFT - 1]: call. ioa_ ("^3xArachnids left:^25t^d", (node.arachnidT + node.heavy_beamT - node.score.arachnids_Xed - node.score.heavy_beams_Xed))
            if I_want_to_see[TIME_LEFT - 1]: call. ioa_ ("^3xTime left:^25t^.1f hrs.", node.time_left)
        # end if
        if damage_report:
            call. ioa_ ("^/Trooper damage report:")
            if I_want_to_see[SCANNER - 1]:
                call. ioa_ ("^3xScanner^25t^[WORKING^]^[DAMAGED^]", node.equipment.scanner.working, not node.equipment.scanner.working)
                if (not node.equipment.scanner.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.scanner.repair_time, max (0, node.equipment.scanner.repair_time - 1))
            # end if
            if I_want_to_see[SNOOPER - 1]:
                call. ioa_ ("^3xSnooper^25t^[WORKING^]^[DAMAGED^]", node.equipment.snooper.working, not node.equipment.snooper.working)
                if (not node.equipment.snooper.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.snooper.repair_time, max (0, node.equipment.snooper.repair_time - 1))
            # end if
            if I_want_to_see[JET_BOOSTERS - 1]:
                call. ioa_ ("^3xJet boosters^25t^[WORKING^]^[DAMAGED^]", node.equipment.jet_boosters.working, not node.equipment.jet_boosters.working)
                if (not node.equipment.jet_boosters.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.jet_boosters.repair_time, max (0, node.equipment.jet_boosters.repair_time - 1))
            # end if
            if I_want_to_see[FLAMER_RIFLE - 1]:
                call. ioa_ ("^3xFlamer rifle^25t^[WORKING^]^[DAMAGED^]", node.equipment.flamer.working, not node.equipment.flamer.working)
                if (not node.equipment.flamer.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.flamer.repair_time, max (0, node.equipment.flamer.repair_time - 1))
            # end if
            if I_want_to_see[HE_LAUNCHER - 1]:
                call. ioa_ ("^3xHE launcher^25t^[WORKING^]^[DAMAGED^]", node.equipment.HE_launcher.working, not node.equipment.HE_launcher.working)
                if (not node.equipment.HE_launcher.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.HE_launcher.repair_time, max (0, node.equipment.HE_launcher.repair_time - 1))
            # end if
            if I_want_to_see[NUKE_LAUNCHER - 1]:
                call. ioa_ ("^3xNuke launcher^25t^[WORKING^]^[DAMAGED^]", node.equipment.nuke_launcher.working, not node.equipment.nuke_launcher.working)
                if (not node.equipment.nuke_launcher.working): call. ioa_ ("^6xRepair time: ^.1f hrs. (^.1f hrs.)", node.equipment.nuke_launcher.repair_time, max (0, node.equipment.nuke_launcher.repair_time - 1))
            # end if
            if I_want_to_see[LISTENING_DEV - 1]:
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
        node.sector[original_SX - 1][original_SY - 1].point[original_PX - 1][original_PY - 1] = "."
        if node.was_in_rad:
            node.sector[original_SX - 1][original_SY - 1].point[original_PX - 1][original_PY - 1] = RADIATION
            if not node.sitting_in_rad: node.was_in_rad = False
        # end if
        if node.sitting_in_rad: node.was_in_rad = True
        node.sector[node.SX - 1][node.SY - 1].point[node.PX - 1][node.PY - 1] = TROOPER
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
        node.sector[node.SX - 1][node.SY - 1].point[original_PX - 1][original_PY - 1] = "."
        if node.was_in_rad:
            node.sector[node.SX - 1][node.SY - 1].point[original_PX - 1][original_PY - 1] = RADIATION
            if (not node.sitting_in_rad): node.was_in_rad = False
        # end if
        if node.sitting_in_rad: node.was_in_rad = True
        node.sector[node.SX - 1][node.SY - 1].point[node.PX - 1][node.PY - 1] = TROOPER
        enemy_attack (node)
    
    def flamer(self, scip, node):
        pass
        
    def launch(self, scip, node):
        pass
        
    def signal_for_help(self, scip, node):
        pass
        
    def score(self, scip, node):
        pass
        
    def repair(self, scip, node):
        pass
        
    def rest(self, scip, node):
        pass
        
    def rescue(self, scip, node):
        pass
        
    def encamp(self, scip, node):
        pass
        
    def listen(self, scip, node):
        pass
        
    def transfer(self, scip, node):
        pass
        
    def quit(self, scip, node):
        call. ssu_.abort_subsystem (scip, (0))
        
    def self_identify(self, scip, node):
        call. ioa_ ("^a ^a", MAIN, sst_data_.version_string)
        
def update_chart(node):
    pass
    
def you_lose (reason):
    pass
    
def H_or_M_present (sx, sy, node):
    return True
    
def calc_move_cost(sx1, sy1, px1, py1, sx2, sy2, px2, py2):
    return 0
    
def calc_move_time(sx1, sy1, px1, py1, sx2, sy2, px2, py2):
    return 0

def get_target_point(sx1, sy1, px1, py1, sx2, sy2, px2, py2):
    pass
    
def move(move_type, node, target_PX, target_PY):
    pass

def got_there_ok(node):
    pass
    
def enemy_attack(node):
    pass
    
def attack_supply_ships(node):
    pass
    
def calc_score(node, type):
    return 0
    