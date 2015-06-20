
from multics.pl1types import PL1

iox_control_version_1 = 1

#== This filter set allows users to type Ctrl-H (backspace), Ctrl-I (tab),
#== Ctrl-J (linefeed), Ctrl-M (carriage return)
common_ctrl_chars = map(chr, set(range(32)) - set([8, 9, 10, 13]))

class iox_control_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            version             = iox_control_version_1,
            echo_input_sw       = False,
            enable_signals_sw   = False,
            filter_chars        = [],
        )
