
from multics.globals import *

@system_privileged
def print_(*func_args):
    arg_list  = parm()
    directory = parm()
    full      = parm()
    segment   = parm()
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
    begin = 0
    end = -1
    print_header = True
    page_size = 24
    
    if arg_list.args:
        begin = int(arg_list.args.pop(0)) - 1
        print_header = False
    if arg_list.args:
        end = int(arg_list.args.pop(0)) + 1
    if arg_list.args:
        call.ioa_("Usage: print [file] {{begin}} {{end}}")
        return
    # end if
    
    # call.ioa_("clock_ = {0}", clock_())
    
    call.sys_.get_abs_path(filename, full)
    call.sys_.split_path_(full.path, directory, segment)
    call.hcs_.fs_file_exists(directory.name, segment.name, code)
    if code.val != 0:
        call.ioa_("File not found {0}", filename)
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
            supervisor.llout("%s:\n\n\n" % (segment.name), tty_channel)
            page_size = 20
        # end if
        
        if end == -1 or end > len(lines):
            end = len(lines)
        # end if
        count = 0
        for i in range(begin, end):
            supervisor.llout(lines[i] + "\n", tty_channel)
            count += 1
            if count % page_size == 0:
                page_size = 24
                supervisor.llout("(press Enter to continue)", tty_channel)
                supervisor.llin(block=True, tty_channel=tty_channel)
                supervisor.llout("\n", tty_channel)
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

pr = print_
