
from multics.globals import *

include.query_info

def lock_test():
    declare (clock_ = entry . returns(fixed.bin(36)))
    segment         = parm()
    input           = char('*') . parm . init("")
    code            = fixed.bin(35) . parm . init(0)
    
    dirname = ">udd>SysAdmin>JRCooper"
    filename = "locktest"
    
    call ioa_ ("Opening ^a>^a", dirname, filename)
    call hcs_$initiate (dirname, filename, "", 0, 0, segment, code)
    locktest_file = segment.ptr
    if locktest_file == null():
        call hcs_$make_seg (dirname, filename, "", 0, segment(["locktest"]), code)
        locktest_file = segment.ptr
        if locktest_file == null():
            call ioa_ ("Could not create ^a>^a", dirname, filename)
            return
            
    call ioa_ ("Locking ^a>^a...", dirname, filename)
    call set_lock_$lock (locktest_file.lock_word(), 30, code)
    if code.val != 0:
        if code.val == error_table_$invalid_lock_reset:
            call ioa_ ("Invalid lock reset")
        else:
            call ioa_ ("Lock failed: ^r", code.val)
            return
    call ioa_ ("...lock acquired")
    
    # query_info.repeat_time = 4
    call command_query_ (query_info, input, "lock_test", "Hit Enter to unlock:")
    call set_lock_$unlock (locktest_file.lock_word(), code)
    if code.val != 0:
        call ioa_ ("Unlock failed: ^r", code.val)
        return
    call ioa_ ("...lock released")
    