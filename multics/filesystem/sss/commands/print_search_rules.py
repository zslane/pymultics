
from multics.globals import *

from sl_info import *

def print_search_rules():
    sl_info_ptr = parm()
    code        = parm()
    
    call.search_paths_.get("object", null(), sl_info_ptr, sl_info_version_1, code)
    path_list = [ p.pathname for p in sl_info_ptr.data.paths ]
    call.ioa_("Search rules:^(\n    ^a^)", path_list)
    
#-- end def print_search_rules

psr = print_search_rules
