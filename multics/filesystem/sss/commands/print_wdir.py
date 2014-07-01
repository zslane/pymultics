
from multics.globals import *

def print_wdir():
    declare (get_wdir_ = entry . returns (char(168)))
    call.ioa_(get_wdir_())
#-- end def print_wdir

pwd = print_wdir
