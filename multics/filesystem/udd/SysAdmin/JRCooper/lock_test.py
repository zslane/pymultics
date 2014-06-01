
from multics.globals import *

from query_info import *

def lock_test():
    declare (locktest_file = parm,
             input         = parm,
             segment       = parm,
             code          = parm)
    
    dirname = ">udd>SysAdmin>JRCooper"
    filename = "locktest"
    
    call.ioa_("Opening {0}>{1}", dirname, filename)
    call.hcs_.initiate(dirname, filename, segment)
    locktest_file = segment.ptr
    if not locktest_file:
        call.hcs_.make_seg(dirname, filename, segment("locktest"), code)
        locktest_file = segment.ptr
        if not locktest_file:
            call.ioa_("Could not create {0}>{1}", dirname, filename)
            return
            
    call.ioa_("Locking {0}>{1}...", dirname, filename)
    call.set_lock_.lock(locktest_file, 10, code)
    if code.val != 0:
        if code.val == error_table_.invalid_lock_reset:
            call.ioa_("Invalid lock reset")
        else:
            call.ioa_("Lock failed: {0}", code.val)
            return
    call.ioa_("...lock acquired")
    
    query_info = query_info_structure()
    query_info.repeat_time = 4
    call.command_query_(query_info, input, "lock_test", "Hit Enter to unlock:")
    call.set_lock_.unlock(locktest_file, code)
    if code.val != 0:
        call.ioa_("Unlock failed: {0}", code.val)
        