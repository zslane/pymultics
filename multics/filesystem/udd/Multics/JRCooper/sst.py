
from multics.globals import *

def sst():
    
    include. sst_node
    # include. sst_macros
    include. sst_constants
    # include. arg_processing
    
    argn                         = fixed.bin . parm . init (0)
    argp                         = ptr . init (null ())
    code                         = fixed.bin (35) . parm . init ("")
    
    input                        = char (100) . parm . init ("")
    x                            = fixed.bin . init (0) . local
    y                            = fixed.bin . init (0) . local
    z                            = fixed.bin . init (0) . local
    game_length                  = fixed.bin . init (0) . local
    difficulty                   = fixed.bin . init (0) . local
    
    # dcl     sst_rqt_$sst_rqt_      ext static fixed bin;
    dcl ( sst_rqt_               = entry )
    dcl ( sst_data_              = entry )
    
    scip                         = ptr . init (null ())
    USER_INPUT_IOCB              = ptr . init (null ())
    PROMPT_MODE                  = bit (3) . init (b'011') . local
    prompt_string                = char (64) . varying . init ("^/Command > ") . local
    INFO_PREFIX                  = char (32) . init ("sst") . local
    PRE_REQUEST_LINE             = char (30) . init ("pre_request_line") . local
    POST_REQUEST_LINE            = char (30) . init ("post_request_line") . local
    
    dcl ( sst_                   = entry )
    
    last_name                    = char (21) . init ("") . local
    
    call. cu_.arg_count (argn, code)
    if (code.val != 0):
        call. com_err_ (code.val, MAIN)
        return
    # end if
    for x in range(argn.val):
        call. cu_.arg_ptr (x, argp, code)
        arg = argp.val
        if (arg == "-short") or (arg == "-sh"): game_length = 1
        elif (arg == "-medium") or (arg == "-med"): game_length = 2
        elif (arg == "-long") or (arg == "-lg"): game_length = 3
        elif (arg == "-leutenant") or (arg == "-lt"): difficulty = 1
        elif (arg == "-sergeant") or (arg == "-sr"): difficulty = 2
        elif (arg == "-captain") or (arg == "-cp"): difficulty = 3
        else:
            call. com_err_ ((0), MAIN, "Usage: sst {{-control_args}}")
            return
        # end if
    # end for
    
    call. ioa_ ("*** Starship Troopers ^a ***^/", sst_data_.version_string)
    while (game_length == 0):
       call. ioa_.nnl ("Do you wish to play a (s)hort, (m)edium, or (l)ong game? ")
       getline (input)
       if (input.val == "s") or (input.val == "short"): game_length = 1
       elif (input.val == "m") or (input.val == "medium"): game_length = 2
       elif (input.val == "l") or (input.val == "long"): game_length = 3
    # end while
    
    call. ioa_ ()
    
    while (difficulty == 0):
       call. ioa_.nnl ("Are you (l)eutenant, (s)ergeant, or (c)aptain level? ")
       getline (input)
       if (input.val == "l") or (input.val == "leutenant"): difficulty = 1
       elif (input.val == "s") or (input.val == "sergeant"): difficulty = 2
       elif (input.val == "c") or (input.val == "captain"): difficulty = 3
    # end while
    
    last_name = derive_lname_ ()
    call. sst_.set_up_game (addr (NODE), game_length, difficulty)
    call. sst_.print_introduction (addr (NODE), last_name);
    call. ssu_.create_invocation (MAIN, sst_data_.version_string, addr (NODE), addr (sst_rqt_.sst_rqt_), sst_data_.info_directory, scip, code)
    # call. ssu_.set_prompt_mode (scip, PROMPT_MODE)
    # call. ssu_.set_prompt (scip, prompt_string)
    # call. ssu_.set_procedure (scip, PRE_REQUEST_LINE, sst_.daemon, code)
    # call. ssu_.set_procedure (scip, POST_REQUEST_LINE, sst_.daemon, code)
    # call. ssu_.set_info_prefix (scip, INFO_PREFIX)
    # call. ssu_.listen (scip, USER_INPUT_IOCB, code)
    # call. ssu_.destroy_invocation (scip)

#-- end def sst

def getline(input_var):
    include. query_info
    
    MAIN = "starship_troopers"
    
    query_info.version = query_info_version_5
    query_info.suppress_spacing = True
    query_info.suppress_name_sw = True
    # query_info.cp_escape_control = "10"b;
    
    call.command_query_(query_info, input_var, MAIN)
    
#-- end def getline

def derive_lname_():
    person = char (21) . parm . init("")
    project = char (9) . parm . init("")
    acct = char (8) . parm . init ("")
    
    call. user_info_.whoami (person, project, acct)
    for i, c in enumerate(list(person.val)):
        if c in "abcdefghijklmnopqrstuvwxyz":
            return person.val[i - 1:]
    
#-- end def derive_lname_
