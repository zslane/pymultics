import re

from multics.globals import *

def get_system_search_rules():
    ALL_RULES = ''
    segment   = parm()
    code      = parm()
    
    #== Load the system search rules
    call.hcs_.initiate(GlobalEnvironment.fs.system_control_dir, "system_search_rules", "", 0, 0, segment, code)
    if segment.ptr != null():
        search_rules = dict(segment.ptr)
        rules_dict = {}
        for rule in search_rules[ALL_RULES]:
            rules_dict[rule] = [re.sub("^-", "", rule)]
        # end for
        for keyword in search_rules:
            if keyword:
                for rule in search_rules[keyword]:
                    rules_dict[rule].append(keyword)
                # end for
            # end if
        # end for
        
        for rule in search_rules[ALL_RULES]:
            call.ioa_("^a", (", ").join(rules_dict[rule]))
        # end for
        call.ioa_()
    else:
        call.ioa_("Could not find system search rules.")
    # end if

gssr = get_system_search_rules
