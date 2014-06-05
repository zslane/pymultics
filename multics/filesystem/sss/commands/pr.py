
from multics.globals import *

@system_privileged
def pr():

    declare (arg_list = parm,
             directory = parm,
             entry = parm,
             full = parm,
             segment  = parm,
             code     = parm)
             
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        call.ioa_("Usage: print [file]")
        return
        
    filename = arg_list.args.pop(0)
    call.sys_.get_abs_path(filename, full)
    call.sys_.split_path_(full.path, directory, entry)
    call.hcs_.initiate(directory.name, entry.name, segment)
    if segment.ptr == nullptr():
        call.ioa_("File not found {0}", filename)
    else:
        file_text = segment.ptr()
        if type(file_text) is str:
            #== Convert non-printable (i.e., binary) text into printable hexcodes
            if not _isprintable(file_text):
                import binascii
                file_text = binascii.hexlify(file_text)
            # end if
        else:
            #== Convert python objects into their pickled string form
            import cPickle as pickle
            file_text = pickle.dumps(file_text)
        # end if
        system.hardware.io.put_output(file_text + "\n")

def _isprintable(s):
    if type(s) is str:
        import string
        printset = set(string.printable)
        textset = set(s)
        return textset.issubset(printset)
    else:
        return False
        