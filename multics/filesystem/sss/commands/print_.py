import datetime

from multics.globals import *

include.query_info

def print_(*func_args):
    arg_list  = parm()
    directory = parm()
    full      = parm()
    segment   = parm()
    answer    = parm("")
    code      = parm()
    
    if func_args:
        arg_list.args = list(func_args)
    else:
        call.cu_.arg_list(arg_list)
    # end if
    if len(arg_list.args) == 0:
        call.ioa_("Usage: print [file] {{begin}} {{end}}")
        return
    # end if
    
    filename = arg_list.args.pop(0)
    begin = 1
    end = -1
    print_header = True
    page_size = 20
    
    if arg_list.args:
        begin = int(arg_list.args.pop(0))
        print_header = False
    if arg_list.args:
        end = int(arg_list.args.pop(0)) + 1
    if arg_list.args:
        call.ioa_("Usage: print [file] {{begin}} {{end}}")
        return
    # end if
    
    call.sys_.get_abs_path(filename, full)
    call.sys_.split_path_(full.path, directory, segment)
    call.hcs_.fs_file_exists(directory.name, segment.name, code)
    if code.val != 0:
        call.ioa_("print: Entry not found. ^a", full.path)
    else:
        f = open(vfile_(full.path))
        file_text = f.read()
        f.close()
        
        try:
            import cPickle as pickle
            pickle.loads(file_text)
        except:
            #== Convert non-printable (i.e., binary) text into printable hexcodes
            if not _isprintable(file_text):
                import binascii
                file_text = binascii.hexlify(file_text)
            # end if
        
        lines = file_text.split("\n")
        
        tty_channel = get_calling_process_().tty()
        
        if print_header:
            header = "%s %s" % (segment.name, datetime.datetime.now().ctime())
            call.iox_.write(tty_channel, "{0:^80}\n\n".format(header))
            page_size = 20
        # end if
        
        if end == -1 or end > len(lines):
            end = len(lines)
        # end if
        nlines = end - begin + 1
        
        query_info.version = query_info_version_5
        query_info.suppress_name_sw = True
        query_info.yes_or_no_sw = True
        
        count = 0
        output_count = 0
        for i in range(begin - 1, end):
            line = _add_continuation(lines[i])
            call.iox_.write(tty_channel, line + "\n")
            count += 1
            output_count += 1 + ((len(lines[i]) - 1) // 80)
            if (count != nlines) and (output_count >= page_size):
                output_count = 0
                call.command_query_(query_info, answer, "print", "Continue ({0} lines)?", nlines - count)
                if answer.val.lower() in ["no", "n"]:
                    break
                # end if
            # end if
        # end for
    # end if
#-- end def print_

def _isprintable(s):
    if type(s) is str:
        import string
        printset = set(string.printable)
        textset = set(s)
        return textset.issubset(printset)
    else:
        return False
    # end if
#-- end def _isprintable

def _add_continuation(s):
    out = []
    while s:
        out.append(s[:80])
        s = s[80:]
    # end while
    return r"\c".join(out)
#-- end def _add_continuation

pr = print_
