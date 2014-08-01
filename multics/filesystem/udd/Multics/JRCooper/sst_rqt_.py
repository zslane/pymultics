
from multics.globals import *
        
include. ssu_request_macros

dcl (sst_          = entry)
dcl (ssu_requests_ = entry)

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
        
        request   ( "snooper",
                    sst_.snooper,
                    "sn",
                    "Snooper readout.",
                    flags.allow_command ),
                    
        request   ( "status",
                    sst_.status,
                    "st",
                    "Status and damage reports.",
                    flags.allow_command ),
                    
        request   ( "jump",
                    sst_.jump,
                    "ju",
                    "Jump to new Point.",
                    flags.allow_command ),
                    
        request   ( "fly",
                    sst_.fly,
                    "fl",
                    "Fly to new Sector/Point.",
                    flags.allow_command ),
                    
        request   ( "flamer",
                    sst_.flamer,
                    "fr",
                    "Fire flamer rifle.",
                    flags.allow_command ),
                    
        request   ( "launch",
                    sst_.launch,
                    "la",
                    "Launch H.E. or Nuclear bombs.",
                    flags.allow_command ),
                    
        request   ( "signal",
                    sst_.signal_for_help,
                    "si",
                    "Signal the Retrieval Beacon for help.",
                    flags.unimplemented ),
                    
        request   ( "score",
                    sst_.score,
                    "sr",
                    "Print player score layout.",
                    flags.allow_command ),
                    
        request   ( "repair",
                    sst_.repair,
                    "rp",
                    "Repair a damaged piece of equipment.",
                    flags.allow_command ),
                    
        request   ( "rest",
                    sst_.rest,
                    "re",
                    "Take time for rest/recovery of Body points.",
                    flags.allow_command ),
                    
        request   ( "rescue",
                    sst_.rescue,
                    "rs",
                    "Rescue prisoners from Breach or Fort.",
                    flags.allow_command ),
                    
        request   ( "encamp",
                    sst_.encamp,
                    "en",
                    "Camp at adjacent Supply Ship.",
                    flags.allow_command ),
                    
        request   ( "listen",
                    sst_.listen,
                    "li",
                    "Use Listening Device to detect enemy nuclear demos.",
                    flags.unimplemented ),
                    
        request   ( "transfer",
                    sst_.transfer,
                    "tr",
                    "Transfer energy from/to Jets/Flamer.",
                    flags.allow_command ),
                    
        request   ( "quit",
                    sst_.quit,
                    "q",
                    "Quit the game.",
                    flags.allow_command ),
        
        request   ( "execute",
                    ssu_requests_.execute,
                    "e",
                    "Execute a multics command.",
                    flags.allow_command ),
                    
        request   ( "help",
                    ssu_requests_.help,
                    "",
                    "Print info segment for a particular request.",
                    flags.allow_command ),
                    
        request   ( "list_requests",
                    ssu_requests_.list_requests,
                    "lr",
                    "Summary of game requests.",
                    flags.allow_command ),
                    
        request   ( ".",
                    sst_.self_identify,
                    "",
                    "Game version.",
                    flags.allow_command ),
                    
        request   ( "?",
                    ssu_requests_.summarize_requests,
                    "",
                    "List of available game requests.",
                    flags.allow_command ),
                    
    ]) # end_table sst_rqt_
