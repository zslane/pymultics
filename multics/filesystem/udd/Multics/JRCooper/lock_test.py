
from multics.globals import *

def lock_test():
    dirname = ">udd>SysAdmin>JRCooper"
    filename = "locktest"
    
    call.ioa_("Opening {0}>{1}", dirname, filename)
    locktest_file = call.hcs_.initiate(dirname, filename)
    if not locktest_file:
        (locktest_file, code) = call.hcs_.make_seg(dirname, filename, str)
        if not locktest_file:
            call.ioa_("Could not create {0}>{1}", dirname, filename)
            return
            
    call.ioa_("Locking {0}>{1}...", dirname, filename)
    code = call.set_lock_.lock(locktest_file, 6)
    if code != 0:
        call.ioa_("Lock failed: {0}", code)
        return
    call.ioa_("...lock acquired")
        
    call.ioa_.nnl("Hit Enter to unlock:")
    call.command_query_()
    code = call.set_lock_.unlock(locktest_file)
    if code != 0:
        call.ioa_("Unlock failed: {0}", code)
        