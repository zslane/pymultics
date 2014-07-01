from collections import defaultdict

from multics.globals import *

def list_():
    declare (get_wdir_ = entry . returns (char(168)))
    arg_list    = parm()
    dir_to_list = parm()
    branch      = parm()
    segment     = parm()
    code        = parm()
    
    excluded_extensions = (".pyc", ".pyo")
    
    current_dir = get_wdir_()
    dir_to_list.name = current_dir
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) > 0:
        dir_ref = arg_list.args.pop()
        call.sys_.get_rel_directory(dir_ref, current_dir, dir_to_list, code)
        if code.val != 0:
            call.ioa_("No such directory")
            return
        # end if
    # end if
    call.hcs_.get_directory_contents(dir_to_list.name, branch, segment, code)
    if code.val == 0:
        if len(branch.list) + len(segment.list) == 0:
            call.ioa_("Directory empty")
        else:
            #== Sift out add_names and files with excluded file extensions
            segment.list = filter(lambda s: not s.endswith(excluded_extensions), segment.list)
            branch_add_names = _sift_add_names(branch.list, segment.list)
            segment_add_names = _sift_add_names(segment.list, segment.list)
            
            call.ioa_("{0} segments in directory: {1}", len(branch.list) + len(segment.list), dir_to_list.name)
            
            #== List directories first
            for branch_name in branch.list:
                call.ioa_("d {0}", branch_name)
                for add_name in sorted(branch_add_names.get(branch_name, []), key=len, reverse=True):
                    call.ioa_("    {0}", add_name)
                # end for
            # end for
            
            #== List files second
            for segment_name in segment.list:
                if not segment_name.endswith(excluded_extensions):
                    call.ioa_("  {0}", segment_name)
                # end if
                for add_name in sorted(segment_add_names.get(segment_name, []), key=len, reverse=True):
                    call.ioa_("    {0}", add_name)
                    
#-- end def list_
    
def _sift_add_names(name_list, file_list):
    add_names = defaultdict(list)
    for fname in file_list[:]:
        match = re.match(r"\.(.*)\+(.*)", fname)
        if match:
            add_name = match.group(1)
            long_name = match.group(2)
            if long_name in name_list:
                add_names[long_name].append(add_name)
                file_list.remove(fname)
            # end if
        # end if
    # end for
    return dict(add_names)
    
#-- end def _sift_add_names

ls = list_
