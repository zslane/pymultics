import re

from multics.globals import *

@system_privileged
def set_system_search_rules():
    person        = parm()
    project       = parm()
    acct          = parm()
    rules_segment = parm()
    arg_list      = parm()
    full_path     = parm()
    dirname       = parm()
    entryname     = parm()
    code          = parm()
    
    call.user_info_.whoami(person, project, acct)
    if project.val != "SysAdmin":
        call.ioa_("You are not authorized to use the set_system_search_rules command.")
        return
    # end if
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 1:
        call.ioa_("Usage: set_system_search_rules [path]")
        return
    # end if
    
    segment_name = arg_list.args[0]
    call.sys_.get_abs_path(segment_name, full_path)
    call.sys_.split_path_(full_path.val, dirname, entryname)
    call.hcs_.fs_file_exists(dirname.val, entryname.val, code)
    if code.val != 0:
        call.ioa_("Segment ^a not found.", segment_name)
        return
    # end if
    
    rules_dict = _read_rules_file(full_path.val)
    
    call.hcs_.initiate(supervisor.fs.system_control_dir, "system_search_rules", "", 0, 0, rules_segment, code)
    if code.val == 0:
        call.hcs_.delentry_seg(rules_segment.ptr, code)
    # end if
    call.hcs_.make_seg(supervisor.fs.system_control_dir, "system_search_rules", "", 0, rules_segment(rules_dict), code)
    if code.val != 0:
        call.ioa_("Could not save system search rules.")
    
sssr = set_system_search_rules

SEARCH_PATH_SYMBOLS = [
    "home_dir",
    "process_dir",
    "working_dir",
    "referencing_dir",
]

def _read_rules_file(rules_path):
    ALL_RULES  = ''
    rules_file = PL1.File()
    rule       = parm()
    full_path  = parm()
    
    rules_dict = {'':[]}
    max_rules = 50
    PL1.open.file(rules_file).title(vfile_(rules_path)).stream.input
    while max_rules:
        PL1.read.file(rules_file).into(rule)
        if rule.val == null():
            break
        elif rule.val != "":
            rule_data = re.split(r"\s*,\s*", rule.val)
            path = rule_data[0]
            if path not in SEARCH_PATH_SYMBOLS:
                full_path = parm()
                call.sys_.get_abs_path(path, full_path)
                path = full_path.val
            else:
                path = "-" + path
            # end if
            rules_dict[ALL_RULES].append(path)
            site_defined_keywords = rule_data[1:]
            for keyword in site_defined_keywords:
                if keyword not in rules_dict:
                    rules_dict[keyword] = []
                # end if
                rules_dict[keyword].append(path)
            # end for
            max_rules -= 1
        # end if
    # end while
    PL1.close.file(rules_file)
    return rules_dict
