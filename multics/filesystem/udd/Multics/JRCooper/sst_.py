
from multics.globals import *

include. sst_node
# include. sst_macros
include. sst_constants

dcl ( clock                  = entry . returns (fixed.bin (36)) )
dcl ( ssu_                   = entry )
dcl ( sst_data_              = external_static )

class sst_(Subroutine):

    def __init__(self):
        super(sst_, self).__init__(self.__class__.__name__)

    def set_up_game(self, node, game_length, rank):
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
        pass
        
    def status(self, scip, node):
        pass
        
    def jump(self, scip, node):
        pass
        
    def fly(self, scip, node):
        pass
        
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
        