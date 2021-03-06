import re

from multics.globals import *

include.sl_info

SEARCH_PATH_SYMBOLS = [
    "home_dir",
    "process_dir",
    "working_dir",
    "referencing_dir",
]

def set_search_rules():
    rules_file  = PL1.File()
    sl_info_ptr = parm()
    arg_list    = parm()
    full_path   = parm()
    dirname     = parm()
    entryname   = parm()
    code        = parm()
    rule        = parm()
    rule_list   = []
    
    system_search_rules = _get_system_search_rules()
    # site_defined_keywords = filter(None, system_search_rules.keys())
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        rule_list = [ re.sub(r"^-", "", rule) for rule in system_search_rules['default'] ]
        
    elif len(arg_list.args) == 1:
        segment_name = arg_list.args[0]
        call.sys_.get_abs_path(segment_name, full_path)
        call.sys_.split_path_(full_path.val, dirname, entryname)
        call.hcs_.fs_file_exists(dirname.val, entryname.val, code)
        if code.val != 0:
            call.ioa_("Segment ^a not found.", segment_name)
            return
        # end if
        
    else:
        call.ioa_("Usage: set_search_rules {path}")
        return
    # end if
    
    call.search_paths_.get("object", null(), sl_info_ptr, sl_info_version_1, code)
    if code.val == error_table_.no_search_list:
        sl_info_ptr.sl_info = alloc(sl_info_p) # make a fresh sl_info object
    else:
        sl_info_ptr.sl_info.num_paths.reset(0)
    # end if
    
    if rule_list == []:
        rules_list = _read_rules_file(full_path.val, system_search_rules)
    # end if
    
    for rule in rule_list:
        _add_rule(rule, sl_info_ptr, code)
    
ssr = set_search_rules

def _read_rules_file(rules_path, system_search_rules):
    rules_file  = PL1.File()
    rule        = parm()
    
    site_defined_keywords = filter(None, system_search_rules.keys())
    
    rules_list = []
    max_rules = 21
    PL1.open.file(rules_file).title(vfile_(rules_path)).stream.input
    while max_rules:
        PL1.read.file(rules_file).into(rule)
        if rule.val == null():
            break
        elif rule.val != "":
            if rule.val in site_defined_keywords:
                keyword_rules = system_search_rules[rule.val]
                rule_list.extend(keyword_rules[:max_rules])
                max_rules = max(0, max_rules - len(keyword_rules))
            else:
                rule_list.append(rule.val)
                max_rules -= 1
            # end if
        # end if
    # end while
    PL1.close.file(rules_file)
    return rules_list

def _add_rule(rule, sl_info_ptr, code):
    if rule not in SEARCH_PATH_SYMBOLS:
        full_path = parm()
        call.sys_.get_abs_path(rule, full_path)
        rule = full_path.val
    else:
        rule = "-" + rule
    # end if
    
    sl_info_ptr.sl_info.num_paths += 1
    sl_info_ptr.sl_info.paths[sl_info_ptr.sl_info.num_paths - 1].pathname = rule
    
    call.search_paths_.set("object", null(), sl_info_ptr, code)
    if code.val == error_table_.action_not_performed:
        call.ioa_("Invalid path ^a", rule)

def _get_system_search_rules():
    segment = parm()
    code    = parm()
    
    call.hcs_.initiate(GlobalEnvironment.fs.system_control_dir, "system_search_rules", "", 0, 0, segment, code)
    if segment.ptr != null():
        return dict(segment.ptr)
    else:
        return {
            '':        ["-referencing_dir", "-working_dir", ">sss", ">sss>commands"],
            'default': ["-referencing_dir", "-working_dir", ">sss", ">sss>commands"],
        }
        