
from multics.globals import *
        
include. ssu_request_table

dcl (sst_ = entry)

class sst_rqt_(DataSegment):
    
    sst_rqt_ = begin_table([
        
        request   ( "scanner",
                    sst_.scanner,
                    "sc",
                    "Scanner readout.",
                    flags.allow_command ),
        
        request   ( "chart",
                    sst_.chart,
                    "ch",
                    "Planetary chart readout.",
                    flags.allow_command ),
        
        request   ( "quit",
                    sst_.quit,
                    "q",
                    "Quit the game.",
                    flags.allow_command ),
        
    ]) # end_table sst_rqt_
