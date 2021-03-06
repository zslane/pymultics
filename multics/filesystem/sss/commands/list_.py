from collections import defaultdict

from multics.globals import *

include.query_info

def list_():
    declare (get_wdir_ = entry . returns (char(168)))
    arg_list    = parm()
    dir_to_list = parm()
    branch      = parm()
    segment     = parm()
    seglen      = parm()
    return_str  = parm()
    full        = parm()
    code        = parm()
    
    EXCLUDED_EXTENSIONS = (".pyc", ".pyd")
    SPECIAL_EXTENSIONS  = (".mbx")
    RECORD_LENGTH       = 1024 * 4
    
    current_dir = get_wdir_()
    dir_to_list.name = current_dir
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) > 0:
        dir_ref = arg_list.args.pop()
        call.sys_.get_rel_directory(dir_ref, current_dir, dir_to_list, code)
        if code.val != 0:
            call.ioa_("list: Entry not found. ^a", dir_to_list.name)
            return
        # end if
    # end if
    
    call.hcs_.get_directory_contents(dir_to_list.name, branch, segment, code)
    
    if code.val == error_table_.no_directory_entry:
        call.sys_.get_abs_path(dir_to_list.name, full)
        call.sys_.split_path_(full.path, dir_to_list, segment)
        branch.list = []
        segment.list = [ segment.name ]
    # end if
    
    branch.list = _sift_hidden_files(branch.list)
    segment.list = _sift_hidden_files(segment.list)
    
    if len(branch.list) + len(segment.list) == 0:
        call.ioa_("Directory empty.")
    else:
        #== Sift out add_names and files with excluded file extensions
        segment.list = filter(lambda s: not s.endswith(EXCLUDED_EXTENSIONS), segment.list)
        branch_add_names = _sift_add_names(branch.list, segment.list) # <-- branch add names exist as *files* with the .xxx+yyyyy naming format
        segment_add_names = _sift_add_names(segment.list, segment.list)
        
        total_lengths = 0
        segment_lengths = {}
        segment_acl = {}
        for segment_name in segment.list:
            seglen.val = 0
            acl = ""
            if not segment_name.endswith(SPECIAL_EXTENSIONS):
                call.hcs_.get_segment_length(dir_to_list.name, segment_name, seglen, code)
                seglen.val = (seglen.val // RECORD_LENGTH) + (1 if seglen.val % RECORD_LENGTH else 0)
                acl = _get_acl(dir_to_list.name, segment_name)
            # end if
            segment_lengths[segment_name] = seglen.val
            segment_acl[segment_name] = acl
            total_lengths += seglen.val
        # end for
        
        lines = []
        
        #== List files first
        if segment.list:
            lines.append("\nSegments = {0}, Lengths = {1}\n".format(len(segment.list), total_lengths))
        # end if
        for segment_name in segment.list:
            if not segment_name.endswith(EXCLUDED_EXTENSIONS):
                lines.append("{0:3} {1:5}  {2}".format(segment_acl[segment_name], segment_lengths[segment_name], re.sub(r"\.pyo$", "", segment_name)))
            # end if
            for add_name in sorted(segment_add_names.get(segment_name, []), key=len, reverse=True):
                lines.append("{0:11}{1}".format("", re.sub(r"\.pyo$", "", add_name)))
            # end for
        # end for
        
        #== List directories second
        if branch.list:
            lines.append("\nDirectories = {0}.\n".format(len(branch.list)))
        # end if
        for branch_name in branch.list:
            lines.append("sma   {1}".format("", branch_name))
            for add_name in sorted(branch_add_names.get(branch_name, []), key=len, reverse=True):
                lines.append("{0:8}{1}".format("", add_name))
            # end for
        # end for
        
        _print_lines(lines)
        
        call.ioa_()
        
#-- end def list_

def _get_acl(dir_name, segment_name):
    if GlobalEnvironment.fs.is_archive(dir_name + ">" + segment_name) and not segment_name.endswith(".archive"):
        #== Bound archives
        return "re"
    elif segment_name.endswith((".py", ".pyo")):
        #== Python scripts
        return "rew"
    else:
        #== Everything else
        return "r w"
        
#-- end def _get_acl

def _sift_hidden_files(file_list):
    sifted_list = []
    for fname in file_list:
        if fname.startswith("."):
            match = re.match(r"\.(.*)\+(.*)", fname)
            if not match:
                continue
            # end if
        # end if
        sifted_list.append(fname)
    # end for
    return sifted_list
    
#-- end def _sift_hidden_files
        
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

def _print_lines(lines):
    answer = parm("")
    
    query_info.version = query_info_version_5
    query_info.suppress_name_sw = True
    query_info.yes_or_no_sw = True
    
    count = 0
    while lines:
        line = lines.pop(0)
        count += 1
        call.ioa_(line)
        if count == 20 and lines != []:
            count = 0
            call.command_query_(query_info, answer, "list", "Continue (^d names)? ", len(lines))
            if answer.val.lower() in ["no", "n"]:
                break
    
#-- end def _print_lines

ls = list_
