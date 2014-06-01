import py_compile
import os

from multics.globals import *

def compile():
    declare (arg_list    = parm,
             arg_count   = parm,
             current_dir = parm,
             source_file = parm,
             object_file = parm)
             
    call.cu_.arg_count(arg_count)
    if arg_count.val != 1:
        call.ioa_("Usage: compile [module.py]")
        return
    # end if
    call.cu_.arg_list(arg_list)
    
    file_name = arg_list.args.pop(0)
    module_name, _ = os.path.splitext(file_name)
    out_file_name = module_name + ".pyo"
    call.sys_.get_current_directory(current_dir)
    call.ioa_("Compiling {0} to {1} in {2}", file_name, out_file_name, current_dir.name)
    try:
        call.hcs_.make_path(current_dir.name, file_name, source_file)
        call.hcs_.make_path(current_dir.name, out_file_name, object_file)
        py_compile.compile(source_file.path, object_file.path)
    except:
        import sys
        call.ioa_(str(sys.exc_info()[1]))
        call.ioa_("Compilation failed.")
        return
        
    try:
        call.hcs_.del_entry_point(module_name)
    except:
        pass
        