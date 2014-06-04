import os
import re
import shutil
import cPickle as pickle
from pprint import pprint

from multics.globals import *

include.pdt

@system_privileged
def up_pmf():

    declare (arg_list    = parm,
             person      = parm,
             project     = parm,
             current_dir = parm)
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 1:
        call.ioa_("Usage: up_pmf [pdt file]")
        return
        
    pdt_file = arg_list.args.pop()
    project_id, _ = os.path.split(pdt_file)
    
    pdtab = system.session_thread.pdt.get(project_id)
    call.user_info_.whoami(person, project)
    if not ((pdtab and person.id in pdtab.admins) or (project.id == "SysAdmin")):
        call.ioa_("You are not authorized to upload PDT files")
        return
    
    call.sys_.get_current_directory(current_dir)
    src_dir = current_dir.name
    dst_dir = system.hardware.filesystem.system_control_dir
    src_pdt_path = system.hardware.filesystem.path2path(src_dir, pdt_file)
    dst_pdt_path = system.hardware.filesystem.path2path(dst_dir, pdt_file)
    
    if not os.path.exists(src_pdt_path):
        call.ioa_("File not found {0}", pdt_file)
        return
        
    shutil.move(src_pdt_path, dst_pdt_path)
    
    call.ioa_("{0} uploaded", pdt_file)
    
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
    