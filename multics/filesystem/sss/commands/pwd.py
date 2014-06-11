
from multics.globals import *

def pwd():
    declare (get_wdir_ = entry . returns (char(168)))
    call.ioa_(get_wdir_())
    