
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
    if len(arg_list.args) < 3:
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
    
    features = keyword.replace(operations[op][0], "")
    
    if op == APPEND:
        supervisor.fs.pack_archive(archive_path, component_paths, features)
    
#-- end def archive

ac = archive
