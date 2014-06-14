import os
import time
import glob
import errno
import cPickle as pickle

from multics.globals import *

from PySide import QtCore

class set_lock_(SystemExecutable):
    def __init__(self, system_services):
        super(set_lock_, self).__init__(self.__class__.__name__, system_services)
        
    def lock(self, segment_data_ptr, wait_time, code):
        declare (process_id_list = parm)
        
        process = get_calling_process_()
        file_locks = process.stack.assert_create("file_locks", dict)
        lock_id = segment_data_ptr.filepath
        if lock_id in file_locks:
            code.val = error_table_.locked_by_this_process
            return
        # end if
        
        try:
            process_id = process.id()
            call.sys_.get_process_ids(process_id_list)
            file_lock = FileLock(segment_data_ptr, process_id, wait_time, process_id_list.ids)
            code.val = file_lock.acquire()
            #== Make sure that if we had to wait for the lock that the previous locker
            #== wasn't locking it in order to set_lock_.lock()safely delete it. If the file has been
            #== deleted, then return error_table_.no_directory_entry in the result code.
            if not os.path.exists(segment_data_ptr.filepath):
                print "    File doesn't exist!", filepath
                file_lock.release()
                code.val = error_table_.no_directory_entry
            else:
                file_locks[lock_id] = file_lock
            # end if
        except MulticsCondition:
            raise
        except FileLockException as e:
            code.val = e.code
        
    def unlock(self, segment_data_ptr, code):
        process = get_calling_process_()
        file_locks = process.stack.assert_create("file_locks", dict)
        lock_id = segment_data_ptr.filepath
        file_lock = file_locks.get(lock_id)
        if file_lock:
            file_lock.release()
            del file_locks[lock_id]
            code.val = 0
        else:
            code.val = error_table_.lock_not_locked
    
class FileLockException(Exception):

    def __init__(self, errcode):
        self.code = errcode
        
class FileLock(object):
    """ A file locking mechanism that has context-manager support so 
        you can use it in a with statement. This should be relatively cross
        compatible as it doesn't rely on msvcrt or fcntl for the locking.
    """
    
    def __init__(self, segment_data_ptr, process_id, timeout, process_id_list):
        """ Prepare the file locker. Specify the file to lock and optionally
            the maximum timeout and the delay between each attempt to lock.
        """
        dirname, filename = os.path.split(segment_data_ptr.filepath)
        self.is_locked = False
        self.lockfile = os.path.join(dirname, "%s.lock" % (filename))
        self.timeout = timeout
        self.process_id_list = process_id_list
        self.process_id = process_id
        self.delay = 0.05
        self.fd = None
    
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
        FOREVER = -1
        code = 0
        start_time = time.clock()
        while True:
            try:
                self.fd = os.open(self.lockfile, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                os.write(self.fd, str(self.process_id))
                os.close(self.fd)
                # self.store_process_id()
                break;
                
            except OSError as e:
                if e.errno == errno.EPERM:
                    raise FileLockException(error_table_.no_w_permission)
                elif e.errno != errno.EEXIST:
                    raise FileLockException(e.errno)
                # elif self.invalid_lock_id2():
                    # code = error_table_.invalid_lock_reset
                    
                if (self.timeout != FOREVER and
                    (time.clock() - start_time) >= self.timeout):
                    raise FileLockException(error_table_.lock_wait_time_exceeded)
                else:
                    check_conditions_()
                    
                time.sleep(self.delay)
                
        self.is_locked = True
        return code
    
    def release(self):
        """ Get rid of the lock by deleting the lockfile. 
        """
        if self.is_locked:
            os.unlink(self.lockfile)
            self.is_locked = False
    
    def store_process_id(self):
        os.close(self.fd)
        with open(self.lockfile, "wb") as f:
            pickle.dump(self.process_id, f)
        # end with
        
    def invalid_lock_id2(self):
        fd = os.open(self.lockfile, os.O_RDWR)
        s = os.read(fd, 32)
        os.lseek(fd, 0, 0)
        lock_owner_id = int(s)
        if lock_owner_id not in self.process_id_list:
            os.write(fd, str(self.process_id))
        os.close(fd)
        return lock_owner_id not in self.process_id_list
        
    def invalid_lock_id(self):
        valid_processes = self.process_id_list
        with open(self.lockfile, "rb") as f:
            lock_owner_id = pickle.load(f)
        # end with
        invalid = lock_owner_id not in valid_processes
        if invalid:
            with open(self.lockfile, "wb") as f:
                pickle.dump(self.process_id, f)
            # end with
            return True
        else:
            return False
