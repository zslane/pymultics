import py_compile
import os

from multics.globals import *

def compile():
    declare (get_wdir_ = entry . returns (char(168)))
    arg_list    = parm()
    arg_count   = parm()
    source_file = parm()
    object_file = parm()
    code        = parm()
    
    call.cu_.arg_count(arg_count)
    if arg_count.val != 1:
        call.ioa_("Usage: compile [module.py]")
        return
    # end if
    call.cu_.arg_list(arg_list)
    
    file_name = arg_list.args.pop(0)
    module_name, _ = os.path.splitext(file_name)
    out_file_name = module_name + ".pyo"
    current_dir = get_wdir_()
    call.ioa_("Compiling ^a to ^a in ^a", file_name, out_file_name, current_dir)
    try:
        call.hcs_.make_path(current_dir, file_name, source_file)
        call.hcs_.make_path(current_dir, out_file_name, object_file)
        py_compile.compile(source_file.path, object_file.path)
    except:
        import sys
        call.ioa_(str(sys.exc_info()[1]))
        call.ioa_("Compilation failed.")
        return
        
    call.term_.single_refname(module_name, code)
    