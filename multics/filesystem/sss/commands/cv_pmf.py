import os
import re
import cPickle as pickle
from pprint import pprint

from multics.globals import *

include.pdt

@system_privileged
def cv_pmf():

    declare (arg_list    = parm,
             current_dir = parm)
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 1:
        call.ioa_("Usage: cv_pmf [project_id]")
        return
        
    project_id = arg_list.args.pop()
    pmf_file = project_id + ".pmf"
    pdt_file = project_id + ".pdt"
    
    # pdtab = system.session_thread.pdt.get(project_id)
    # call.user_info_.whoami(person, project)
    # if (persion.id not in pdtab.admins) and (project.id != "SysAdmin"):
        # call.ioa_("You are not authorized to upload PDT files")
        # return
    
    call.sys_.get_current_directory(current_dir)
    pmf_path = system.hardware.filesystem.path2path(current_dir.name, pmf_file)
    if not system.hardware.filesystem.file_exists(pmf_path):
        call.ioa_("{0}.pmf file not found", project_id)
        return
    # end if
    
    with open(pmf_path, "r") as f:
        pmf_data = load_pmf(f)
    # end with
    pprint(pmf_data)
    
    pdtab = ProjectDefinitionTable(project_id, pmf_data['alias'], pmf_data['admin'])
    for user in pmf_data['users']:
        pdtab.add_user(
        user['person_id'], user.get('command_processor', ""))
    # end for
    pprint(pdtab)
    pdt_path = system.hardware.filesystem.path2path(current_dir.name, pdt_file)
    with open(pdt_path, "wb") as f:
        pickle.dump(pdtab, f)
    # end with
    
    call.ioa_("{0} written", pdt_file)
    
def load_pmf(f):
    alias = ""
    admin_list = []
    users_list = []
    reading_users = False
    
    for line in f:
        line = line.strip()
        if line == "":
            continue
            
        m = re.match(r"alias\s*:\s*(\w*)\s*$", line)
        if m:
            alias = m.group(1).strip()
            continue
            
        m = re.match(r"admin\s*:\s*\[(.*)\]\s*$", line)
        if m:
            admin_list = re.split(r"\s*,\s*", m.group(1).strip())
            reading_users = False
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
                
        raise Exception("Syntax error in PMF file:\n{0}".format(line))
            
    return {'alias': alias, 'admin': admin_list, 'users': users_list }
    