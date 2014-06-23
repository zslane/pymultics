
from multics.globals import *

declare (vfile_ = entry)

@system_privileged
def print_(*func_args):

    declare (arg_list  = parm,
             directory = parm,
             entry     = parm,
             full      = parm,
             segment   = parm,
             code      = parm)
             
    print globals()['vfile_']
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
    call.sys_.split_path_(full.path, directory, entry)
    call.hcs_.fs_file_exists(directory.name, entry.name, code)
    if code.val != 0:
        call.ioa_("File not found {0}", filename)
    # call.hcs_.initiate(directory.name, entry.name, "", 0, 0, segment, code)
    # if segment.ptr == null():
        # call.ioa_("File not found {0}", filename)
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
        
        # file_text = segment.ptr()
        # if type(file_text) is str:
            # #== Convert non-printable (i.e., binary) text into printable hexcodes
            # if not _isprintable(file_text):
                # import binascii
                # file_text = binascii.hexlify(file_text)
            # # end if
        # else:
            # #== Convert python objects into their pickled string form
            # import cPickle as pickle
            # file_text = pickle.dumps(file_text)
        # # end if
        
        lines = file_text.split("\n")
        
        if print_header:
            system.llout("%s:\n\n\n" % (entry.name))
            page_size = 20
        # end if
        
        if end == -1 or end > len(lines):
            end = len(lines)
        # end if
        count = 0
        for i in range(begin, end):
            system.llout(lines[i] + "\n")
            count += 1
            if count % page_size == 0:
                page_size = 24
                system.llout("(press Enter to continue)")
                system.llin(block=True)
                system.llout("\n")
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
