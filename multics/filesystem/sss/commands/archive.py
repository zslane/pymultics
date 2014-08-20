
from multics.globals import *

@system_privileged
def archive():

    LIST_TOC   = "list"
    APPEND     = "append"
    REPLACE    = "replace"
    UPDATE     = "update"
    DELETE     = "delete"
    EXTRACT    = "extract"
    
    operations = {
        LIST_TOC: ("t", "tl", "tb", "tlb"),
        APPEND  : ("a", "ad", "adf", "ca", "cad", "cadf"),
        REPLACE : ("r", "rd", "rdf", "cr", "crd", "crdf"),
        UPDATE  : ("u", "ud", "udf", "cu", "cud", "cudf"),
        DELETE  : ("d", "cd"),
        EXTRACT : ("x", "xf"),
    }
    
    arg_list  = parm()
    full_path = parm()
    code      = parm()
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) < 2:
        call.ioa_("Usage: archive key archive_file paths...")
        return
    # end if
    
    keyword = arg_list.args.pop(0)
    archive_name = arg_list.args.pop(0)
    paths = arg_list.args
    
    if not archive_name.endswith(".archive"):
        archive_name += ".archive"
    # end if
    
    call.sys_.get_abs_path(archive_name, full_path)
    archive_path = full_path.val
    
    component_paths = []
    for path in paths:
        call.sys_.get_abs_path(path, full_path)
        component_paths.append(full_path.val)
    # end for
    
    for op in operations:
        if keyword in operations[op]:
            break
    else:
        call.ioa_("Invalid operation keyword. ^a", keyword)
        return
    # end for
    
    if not supervisor.fs.file_exists(archive_path) and (op in [LIST_TOC, UPDATE, DELETE, EXTRACT]):
        call.ioa_("archive ^a not found.", archive_name)
        return
    elif not supervisor.fs.is_archive(archive_path):
        call.ioa_("^a is not an archive segment.", archive_name)
        return
    elif (component_paths == []) and (op in [APPEND, DELETE]):
        call.ioa_("No components specified.")
        return
    # end if
    
    features = keyword.replace(operations[op][0], "")
    
    if op == LIST_TOC:
        call.ioa_()
        #== Print header
        if "b" not in features:
            call.ioa_("^/^vx^a^/", (80 - len(archive_path)) // 2, archive_path)
            if "l" in features:
                call.ioa_("name                    updated    mode      modified   length^/")
            else:
                call.ioa_("name              length^/")
            # end if
        # end if
        
        #== Print component file info
        info_list = supervisor.fs.get_archive_info(archive_path)
        for info in info_list:
            if (info.filename in paths) or (paths == []):
            
                upd_date       = datetime.datetime(*info.comment)
                upd_sec_tenths = info.comment[-1] // 6
                mode           = "rew" if info.filename.endswith((".py", ".pyo")) else "rw"
                mod_date       = datetime.datetime(*info.date_time)
                mod_sec_tenths = info.date_time[-1] // 6
                file_size      = (info.file_size // 1024) + (1 if info.file_size % 1024 else 0)
                
                if "l" in features:
                    call.ioa_("^20a^a.^d ^3a  ^a.^d  ^d", info.filename[:19], upd_date.strftime("%m/%d/%y %H%M"), upd_sec_tenths, mode, mod_date.strftime("%m/%d/%y %H%M"), mod_sec_tenths, file_size)
                else:
                    call.ioa_("^20a^d", info.filename[:19], file_size)
                # end if
            # end if
        # end for
        call.ioa_()
    
    elif op == APPEND:
        supervisor.fs.pack_archive(archive_path, component_paths, features)
        
    elif op == REPLACE:
        supervisor.fs.replace_in_archive(archive_path, component_paths, features)
        
    elif op == UPDATE:
        supervisor.fs.update_archive(archive_path, component_paths, features)
        
    elif op == DELETE:
        supervisor.fs.delete_from_archive(archive_path, component_paths, features)    
    
    elif op == EXTRACT:
        supervisor.fs.extract_from_archive(archive_path, component_paths, features)
        
#-- end def archive

ac = archive
