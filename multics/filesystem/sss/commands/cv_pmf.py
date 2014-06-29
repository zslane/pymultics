import cPickle as pickle
from pprint import pprint

from multics.globals import *

include.pdt

@system_privileged
def cv_pmf():

    declare (get_wdir_ = entry . returns (char(168)))
    arg_list = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 1:
        call.ioa_("Usage: cv_pmf [project_id]")
        return
        
    project_id = arg_list.args.pop()
    pmf_file = project_id + ".pmf"
    pdt_file = project_id + ".pdt"
    
    current_dir = get_wdir_()
    pmf_path = system.hardware.filesystem.path2path(current_dir, pmf_file)
    if not system.hardware.filesystem.file_exists(pmf_path):
        call.ioa_("{0}.pmf file not found", project_id)
        return
    # end if
    
    pmf_data = None
    with open(pmf_path, "r") as f:
        pmf_data = load_pmf2(f)
    # end with
    pprint(pmf_data)
    
    pdtab = ProjectDefinitionTable(project_id, pmf_data['alias'])
    for user in pmf_data['users']:
        pdtab.add_user(user['person_id'], user.get('home_dir', ""), user.get('command_processor', ""))
    # end for
    pprint(pdtab)
    pdt_path = system.hardware.filesystem.path2path(current_dir, pdt_file)
    with open(pdt_path, "wb") as f:
        pickle.dump(pdtab, f)
    # end with
    
    call.ioa_("{0} written", pdt_file)
    
def load_pmf2(f):
    return eval(f.read())
    
def load_pmf(f):
    import re
    alias = ""
    admin_list = []
    users_list = []
    reading_users = False
    
    for line in f:
        pos = command_string.find("#")
        if pos != -1:
            return command_string[:pos].strip()
        else:
            line = line.strip()
        # end if
        
        if line == "":
            continue
            
        m = re.match(r"alias\s*:\s*(\w*)\s*$", line)
        if m:
            alias = m.group(1).strip()
            continue
            
        elif re.match(r"users\s*:\s*$", line):
            reading_users = True
            continue
            
        elif reading_users:
            m = re.match(r"\s*-\s*{(.*)}\s*$", line)
            if m:
                name_entry_items = re.split(r"\s*,\s*", m.group(1).strip())
                d = {}
                for item in name_entry_items:
                    k, _, v = item.strip().partition(":")
                    d[k.strip()] = v.strip()
                # end for
                users_list.append(d)
                continue
                
        raise SyntaxError("Syntax error in PMF file:\n{0}".format(line))
            
    return {'alias': alias, 'admin': admin_list, 'users': users_list }
    