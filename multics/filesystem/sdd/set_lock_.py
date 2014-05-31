import os
import time
import glob
import errno

from multics.globals import *

class set_lock_(SystemExecutable):
    def __init__(self, system_services):
        super(set_lock_, self).__init__(self.__class__.__name__, system_services)
        
    def lock(self, segment_data_ptr, wait_time):
        self.system.session_thread.session.process.stack.assert_create("file_locks", dict)
        lock_id = segment_data_ptr.filepath
        if lock_id in self.system.session_thread.session.process.stack.file_locks:
            return error_table_.locked_by_this_process
        try:
            process_id = self.system.session_thread.session.process.process_id
            file_lock = FileLock(segment_data_ptr, process_id, wait_time, self.system.session_thread.login_db)
            code = file_lock.acquire()
            self.system.session_thread.session.process.stack.file_locks[lock_id] = file_lock
            return code
        except FileLockException as e:
            return e.code
        
    def unlock(self, segment_data_ptr):
        self.system.session_thread.session.process.stack.assert_create("file_locks", dict)
        lock_id = segment_data_ptr.filepath
        file_lock = self.system.session_thread.session.process.stack.file_locks.get(lock_id)
        if file_lock:
            file_lock.release()
            del self.system.session_thread.session.process.stack.file_locks[lock_id]
            return 0
        else:
            return error_table_.lock_not_locked
    
class FileLockException(Exception):

    def __init__(self, errcode):
        self.code = errcode
        
class FileLock(object):
    """ A file locking mechanism that has context-manager support so 
        you can use it in a with statement. This should be relatively cross
        compatible as it doesn't rely on msvcrt or fcntl for the locking.
    """
    
    def __init__(self, segment_data_ptr, process_id, timeout, login_db):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        dirname, filename = os.path.split(segment_data_ptr.filepath)
        self.is_locked = False
        self.lockfile = os.path.join(dirname, "%s.lock" % (filename))
        self.lockidfile = os.path.join(dirname, "%s.lock.%s" % (filename, call.unique_name_(process_id)))
        self.lockidglob = os.path.join(dirname, "%s.lock.*" % (filename))
        self.timeout = timeout
        self.login_db = login_db
        self.process_id = process_id
        self.delay = 0.05
        self.fd = None
        self.fdi = None
    
    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
        self.release()
    
    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every self.delay seconds. It does this until it either gets the lock or
            exceeds self.timeout number of seconds, in which case it throws 
            an exception.
        """
        code = 0
        start_time = time.clock()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                self.fdi = os.open(self.lockidfile, os.O_CREAT|os.O_RDWR)
                break;
                
            except OSError as e:
                if e.errno == errno.EPERM:
                    raise FileLockException(error_table_.no_w_permission)
                elif e.errno != errno.EEXIST:
                    raise FileLockException(e.errno)
                elif self.invalid_lock_id():
                    code = error_table_.invalid_lock_reset
                    
                if (time.clock() - start_time) >= self.timeout:
                    raise FileLockException(error_table_.lock_wait_time_exceeded)
                    
                time.sleep(self.delay)
                
        self.is_locked = True
        return code
    
    def release(self):
        """ Get rid of the lock by deleting the lockfile. 
        """
        if self.is_locked:
            os.close(self.fd)
            os.unlink(self.lockfile)
            os.close(self.fdi)
            os.unlink(self.lockidfile)
            self.is_locked = False
    
    def invalid_lock_id(self):
        session_blocks = self.login_db.session_blocks
        valid_processes = [ call.unique_name_(session_block.process_id) for session_block in session_blocks.values() if session_block.process_id != self.process_id ]
        print valid_processes
        found = False
        for path in glob.glob(self.lockidglob):
            _, unique_name = os.path.splitext(path)
            if unique_name not in valid_processes:
                print "removing invalid process lock file", path
                found = True
                try:
                    os.unlink(path)
                except:
                    pass
            # end if
        # end for
        if found:
            try:
                os.unlink(self.lockfile)
            except:
                pass
        return found
        
