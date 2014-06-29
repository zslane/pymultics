import os
import re
import sys
import time
import glob
import shutil
import cPickle as pickle

from ..globals import *

from PySide import QtCore, QtGui

def collapse(l): return [ item for sublist in l for item in sublist ]

class VirtualMulticsHardware(QtCore.QObject):

    def __init__(self, init_args=[]):
        t = QtCore.QThread.currentThread()
        t.setObjectName("Multics.Supervisor")
        
        self._create_hardware_resources()
        
        #== Create hardware subsystems
        self.__io_subsystem = IOSubsystem()
        self.__filesystem = VirtualMulticsFileSystem(init_args)
        self.__locks_mutex = QtCore.QMutex()
        self.__locks = {}
        
        system_includes_path = os.path.join(self.filesystem.path2path(self.filesystem.system_library_standard), "includes")
        if system_includes_path not in sys.path:
            sys.path.append(system_includes_path)
        
    def _create_hardware_resources(self):
        self.__startup_time = self._load_hardware_statefile()
        self.__clock = HardwareClock(self.__startup_time)
        self.announce = "Virtual Multics Hardware %s Initialized" % (self.version)
    
    @property
    def version(self):
        return "3.0"
    @property
    def clock(self):
        return self.__clock
    @property
    def io(self):
        return self.__io_subsystem
    @property
    def filesystem(self):
        return self.__filesystem
    
    def attach_console(self, console):
        self.__io_subsystem.attach_console(console)
    
    def boot_OS(self):
        from ..software.system_services import SystemServices
        self.__system_services = SystemServices(self)
        self.__system_services.startup()
        return self.__system_services
    
    def shutdown(self):
        self.__io_subsystem.shutdown()
        self._del_hardware_statefile()
    
    def _load_hardware_statefile(self):
        hardware_statefile_path = os.path.join(os.path.dirname(__file__), ".hardware_state")
        
        try:
            with open(hardware_statefile_path, "rb") as hardware_statefile:
                hardware_state = pickle.load(hardware_statefile)
                startup_time = hardware_state['startup_time']
            # end with
        except:
            startup_time = time.time()
            hardware_state = {
                'startup_time': startup_time,
            }
            
            with open(hardware_statefile_path, "wb") as hardware_statefile:
                pickle.dump(hardware_state, hardware_statefile)
            # end with
        # end try
        
        return startup_time
        
    def _del_hardware_statefile(self):
        hardware_statefile_path = os.path.join(os.path.dirname(__file__), ".hardware_state")
        try:
            os.remove(hardware_statefile_path)
        except:
            pass
    
    def generate_lock_word(self):
        return HardwareLock.generate_id()
        
    def acquire_hardware_lock(self, lock_word, process_id, wait_time, code):
        # process_id = get_calling_process_().id() <-- caller (e.g., set_lock_.lock) should do this and pass it in
        self.__locks_mutex.lock()
        lock = self.__locks.setdefault(lock_word, HardwareLock())
        self.__locks_mutex.unlock()
        
        valid_process_list = self.__system_services.whotab.get_process_ids()
        lock.acquire(process_id, valid_process_list, wait_time, code)
        
    def release_hardware_lock(self, lock_word, process_id, code):
        # process_id = get_calling_process_().id() <-- caller (e.g., set_lock_.unlock) should do this and pass it in
        lock = self.__locks.get(lock_word)
        if lock:
            lock.release(process_id, code)
        else:
            code.val = error_table_.lock_not_locked
        
class HardwareClock(QtCore.QObject):

    def __init__(self, wall_time):
        super(HardwareClock, self).__init__()
        
        self.__wall_time = wall_time
        self.__clocktick = time.clock()
        
    def current_time(self):
        dc = time.clock() - self.__clocktick
        return self._asInt(self.__wall_time + dc)
        
    def _asInt(self, t):
        return long(t * 1000000)
        
class IOSubsystem(QtCore.QObject):

    heartbeat = QtCore.Signal()
    terminalClosed = QtCore.Signal()
    breakSignal = QtCore.Signal()
    disconnect = QtCore.Signal()

    def __init__(self):
        super(IOSubsystem, self).__init__()

        self.__input_buffer = []
        self.__linefeed = False
        self.__break_signal = False
        self.__closed_signal = False
        self.__console = None
        self.__terminal_process_id = 0

    def _receive_string(self, s):
        self.__linefeed = False
        self.__input_buffer.append(s.strip())
        
    def _receive_linefeed(self):
        self.__linefeed = True
        
    def _receive_break(self):
        self.__linefeed = False
        self.__break_signal = True
        
    def _close_terminal(self):
        self.__closed_signal = True
        self.terminalClosed.emit()
    
    def attach_console(self, console):
        self.__console = console
        if self.__console:
            self.__console.heartbeat.connect(self.heartbeat)
            self.__console.io.textEntered.connect(self._receive_string)
            self.__console.io.lineFeed.connect(self._receive_linefeed)
            self.__console.io.breakSignal.connect(self._receive_break)
            self.__console.closed.connect(self._close_terminal)
            self.disconnect.connect(self.__console.disconnect)
    
    def attach_console_process(self, process_id):
        self.__terminal_process_id = process_id
        
    def detach_console_process(self, process_id):
        if self.__terminal_process_id == process_id:
            self.__terminal_process_id = 0
            
    def attached_console_process(self):
        return self.__terminal_process_id
        
    def linefeed_received(self, tty_channel=None):
        if tty_channel:
            return tty_channel.linefeed_received()
        else:
            flag, self.__linefeed = self.__linefeed, False
            return flag
        
    def break_received(self, tty_channel=None):
        if tty_channel:
            return tty_channel.break_received()
        else:
            flag, self.__break_signal = self.__break_signal, False
            return flag
        
    def terminal_closed(self, tty_channel=None):
        if tty_channel:
            return tty_channel.terminal_closed()
        else:
            return self.__closed_signal
        
    def has_input(self, tty_channel=None):
        if tty_channel:
            return tty_channel.has_input()
        else:
            return self.__input_buffer != []

    def get_input(self, tty_channel=None):
        try:
            if tty_channel:
                return tty_channel.get_input()
            else:
                return self.__input_buffer.pop(0)
        except:
            return None
    
    def flush_input(self, tty_channel=None):
        if tty_channel:
            tty_channel.flush_input()
        else:
            self.__input_buffer = []
            self.__break_signal = False
            self.__linefeed = False
        
    def set_input_mode(self, mode, tty_channel=None):
        if tty_channel:
            tty_channel.set_input_mode(mode)
        elif self.__console:
            self.__console.setEchoMode.emit(mode)
        
    def put_output(self, s, tty_channel=None):
        if tty_channel:
            tty_channel.put_output(s)
        elif self.__console:
            self.__console.transmitString.emit(s)
            
    def disconnect_tty(self, tty_channel=None):
        if tty_channel:
            tty_channel.disconnect()
        elif self.__console:
            self.disconnect.emit()
    
    def shutdown(self, tty_channel=None):
        if tty_channel:
            tty_channel.shutdown()
        elif self.__console:
            self.__console.shutdown.emit()
        
class VirtualMulticsFileSystem(QtCore.QObject):

    FILESYSTEMROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "filesystem")

    def __init__(self, init_args=[]):
        super(VirtualMulticsFileSystem, self).__init__()
        
        self._create_filesystem_directories(init_args)
        
        # print self._resolve_path(">udd>sct>jrc<jjl<<m>rah")
        
    def _create_filesystem_directories(self, init_args):
        self.system_control_dir = ">sc1"
        self.system_library_standard = ">sss"
        self.process_dir_dir = ">pdd"
        self.user_dir_dir = ">udd"
        
        directory_list = [
            self.system_control_dir,
            self.system_library_standard,
            self.process_dir_dir,
            self.user_dir_dir,
        ]
        
        #== If the -clean|-c boot argument was supplied then clean the filesystem.
        if "-clean" in init_args or "-c" in init_args:
            #== Delete pdd so it starts out completely empty
            print "Wiping", self.process_dir_dir
            native_path = self.path2path(self.process_dir_dir)
            shutil.rmtree(native_path, ignore_errors=True)
            #== Delete the whotab so it won't contain any erroneous users
            print "Deleting whotab"
            native_path = self.path2path(self.system_control_dir, "whotab")
            try:
                os.remove(native_path)
            except:
                pass
        # end if
        
        for directory in directory_list:
            native_path = self.path2path(directory)
            if not os.path.exists(native_path):
                os.mkdir(native_path)
                
        system_directories = [
            self.system_control_dir,
        ]
        
        for directory in system_directories:
            native_path = self.path2path(directory)
            with open(os.path.join(native_path, ".system_directory"), "wb") as f:
                pass
    
    def path2path(self, p, f=""):
        if ">" in p:
            if f:
                p += ">" + f
            # # end if
            p = self._resolve_path(p)
            p = p.replace(">", "\\").lstrip("\\")
            p = os.path.join(self.FILESYSTEMROOT, p)
        elif "\\" in p:
            if f:
                p = os.path.join(p, f)
            # end if
            p = p.replace(self.FILESYSTEMROOT, "").replace("\\", ">")
        return p
        
    def native_path(self, p):
        if ">" in p:
            p = self.path2path(p)
        return p
        
    def merge_path(self, *args):
        #== args assumed to be a list of Multics paths
        merged = ">".join(args).replace(">>", ">")
        return self._resolve_path(merged)
        
    def split_path(self, p):
        if ">" in p:
            i = p.rfind(">")
            dir_name = p[:i] or ">"
            entryname = p[i + 1:]
            return (dir_name, entryname)
        else:
            return os.path.split(p)
        
    def _resolve_path(self, path):
        original_path = path
        
        path = path.lstrip("<").rstrip(">").replace(">>", ">").replace("<>", "<").replace("><", "<") or original_path
        l = re.split("([<>])", path)
        root = {'>':'>'}.get(path[0], "")
        l = [ x for x in l if x and x != ">" ]
        result = []
        for x in l:
            if x == "<":
                result.pop()
            else:
                result.append(x)
        path = root + ">".join(result)
        
        path = self._expand_short_names(path)
        # print original_path + " resolves to: " + path
        return path
    
    def list_segments(self, filepath):
        filepath = self.native_path(filepath)
        for module_path in glob.iglob(os.path.join(filepath, "*.py")):
            module_name, _ = os.path.splitext(os.path.basename(module_path))
            yield (module_name, module_path)
    
    def file_exists(self, filepath):
        filepath = self.native_path(filepath)
        return os.path.exists(filepath)
        
    def delete_file(self, filepath):
        filepath = self.native_path(filepath)
        os.remove(filepath)
        print "Deleted", filepath
        
    def write_file(self, filepath, data):
        filepath = self.native_path(filepath)
        f = open(filepath, "wb")
        #== Null data (None) is written as an empty file
        if type(data) in [str, unicode]:
            f.write(data)
        elif data:
            pickle.dump(data, f)
        # end if
        f.close()
    
    def read_file(self, filepath):
        filepath = self.native_path(filepath)
        f = open(filepath, "rb")
        retry_count = 0
        while True:
            try:
                data = pickle.load(f)
                f.close()
                return data
                
            except:
                # f.seek(0)
                # data = f.read()
                if retry_count == 5:
                    f.close()
                    raise InvalidSegmentFault(filepath)
                else:
                    f.close()
                    QtCore.QThread.msleep(200)
                    f = open(filepath, "rb")
                    retry_count += 1
        
    def get_mod_time(self, filepath):
        filepath = self.native_path(filepath)
        return os.path.getmtime(filepath)
        
    def get_size(self, filepath):
        filepath = self.native_path(filepath)
        return os.path.getsize(filepath)
        
    def get_mod_data(self, filepath):
        filepath = self.native_path(filepath)
        return (os.path.getmtime(filepath), os.path.getsize(filepath))
    
    def mkdir(self, filepath):
        filepath = self.native_path(filepath)
        try:
            os.mkdir(filepath)
            return 0
        except:
            return 0 if os.path.exists(filepath) else error_table_.fileioerr
            
    def rmdir(self, filepath):
        filepath = self.native_path(filepath)
        try:
            shutil.rmtree(filepath)
            return 0
        except:
            return error_table_.fileioerr
            
    def add_name(self, filepath, new_name):
        filepath = self.native_path(filepath)
        dirname, fname = os.path.split(filepath)
        add_name_file = ".%s+%s" % (new_name, fname)
        # print "Adding", new_name, "to", full_path.val, "with", os.path.join(dirname, add_name_file)
        fd = os.open(os.path.join(dirname, add_name_file), os.O_CREAT|os.O_BINARY|os.O_TRUNC|os.O_RDWR)
        os.close(fd)
    
    def get_directory_contents(self, dirpath):
        try:
            dirpath = self.native_path(dirpath)
            contents = glob.glob(os.path.join(dirpath, "*")) + glob.glob(os.path.join(dirpath, ".*"))
            file_list = map(os.path.basename, filter(os.path.isfile, contents))
            dir_list = map(os.path.basename, filter(os.path.isdir, contents))
            return (dir_list, file_list, 0)
        except:
            return (None, None, -1)
    
    def _walk_and_match(self, top, part, parts, new_parts):
        for (dirpath, dirnames, filenames) in os.walk(top):
            # print "...resolving", part, "against", (dirpath, dirnames, filenames)
            if part in dirnames or part in filenames:
                new_parts.append(part)
                if not parts:
                    return
                next_part = parts.pop(0)
                top = os.path.join(dirpath, part)
                self._walk_and_match(top, next_part, parts, new_parts)
                return
            if dirnames:
                add_names = [ dirname.partition("+")[-1] for dirname in dirnames if dirname.startswith("." + part + "+") ]
                if add_names:
                    new_parts.append(add_names[0])
                    if not parts:
                        return
                    next_part = parts.pop(0)
                    top = os.path.join(dirpath, add_names[0])
                    self._walk_and_match(top, next_part, parts, new_parts)
                    return
                # end if
            if filenames:
                add_names = [ filename.partition("+")[-1] for filename in filenames if filename.startswith("." + part + "+") ]
                if add_names:
                    new_parts.append(add_names[0])
                    if not parts:
                        return
                    next_part = parts.pop(0)
                    top = os.path.join(dirpath, add_names[0])
                    self._walk_and_match(top, next_part, parts, new_parts)
                    return
                # end if
            new_parts.append(part)
            return
    
    def _expand_short_names(self, path):
        parts = path.split(">")
        new_parts = [parts.pop(0)]
        part = parts.pop(0)
        self._walk_and_match(self.FILESYSTEMROOT, part, parts, new_parts)
        new_path = ">".join(new_parts)
        return new_path
    
    def segment_data_ptr(self, filepath, data_instance=None, force=False):
        filepath = self.native_path(filepath)
        if (data_instance is not None) or force:
            if type(data_instance) is MemoryMappedIOPtr:
                data_instance = data_instance._mapped_data()
            self.write_file(filepath, data_instance)
        return MemoryMappedIOPtr(self, filepath)
        
class MemoryMappedIOPtr(object):

    CACHE_IN = 1
    CACHE_OUT = 2
    
    def __init__(self, filesystem, filepath):
        self._set("__filesystem", filesystem)
        self._set("__filepath", filepath)
        self._set("__last_modified", None)
        self._set("__data", None)
        self._set("__deferred_writes", False)
        self._update_data(self.CACHE_IN)
        
    def _mapped_data(self):
        return self.__data
    
    def _filepath(self):
        return self.__filepath
        
    def _update(self):
        self._update_data(self.CACHE_OUT)
        
    def _set(self, attrname, value):
        super(MemoryMappedIOPtr, self).__setattr__("_%s%s" % (self.__class__.__name__, attrname), value)
        
    def _update_data(self, direction):
        if direction == self.CACHE_IN:
            if self.__filesystem.file_exists(self.__filepath):
                mod_data = self.__filesystem.get_mod_data(self.__filepath)
                if self.__last_modified != mod_data:
                    self._set("__data", self.__filesystem.read_file(self.__filepath))
                    self._set("__last_modified", mod_data)
                # end if
            else:
                raise SegmentFault(self.__filepath)
            # end if
        elif direction == self.CACHE_OUT:
            if not self.__deferred_writes:
                self.__filesystem.write_file(self.__filepath, self.__data)
                self._set("__last_modified", self.__filesystem.get_mod_data(self.__filepath))
    
    def __getattr__(self, attrname):
        self._update_data(self.CACHE_IN)
        return getattr(self.__data, attrname)
        
    def __setattr__(self, attrname, value):
        setattr(self.__data, attrname, value)
        self._update_data(self.CACHE_OUT)
    
    def __getitem__(self, key):
        self._update_data(self.CACHE_IN)
        return self.__data[key]
        
    def __setitem__(self, key, value):
        self.__data[key] = value
        self._update_data(self.CACHE_OUT)
        
    def __call__(self, value=None):
        if value is None:
            self._update_data(self.CACHE_IN)
            return self.__data
        else:
            self._set("__data", value)
            self._update_data(self.CACHE_OUT)
            
    def __enter__(self):
        self._set("__deferred_writes", True)
        pass
        
    def __exit__(self, etype, value, traceback):
        self._set("__deferred_writes", False)
        if etype:
            pass
        else:
            self._update_data(self.CACHE_OUT)
        
    def delete_file(self):
        try:
            self.__filesystem.delete_file(self.__filepath)
            return 0
        except:
            return error_table_.fileioerr
            
    def lock_word(self):
        import zlib
        return (zlib.crc32(self.__filepath) & 0xFFFFFFFF)
        
    def __repr__(self):
        return repr(self.__data)
        
class HardwareLock(QtCore.QObject):

    unique_lock_id = 0
    gen_mutex      = QtCore.QMutex()
    
    def __init__(self):
        super(HardwareLock, self).__init__()
        self.semaphore = QtCore.QSemaphore(1)
        self.process_id = 0
        
    @staticmethod
    def generate_id():
        HardwareLock.gen_mutex.lock()
        HardwareLock.unique_lock_id += 1
        HardwareLock.gen_mutex.unlock()
        return HardwareLock.unique_lock_id
        
    def acquire(self, process_id, valid_process_list, timeout, code):
        if self.process_id == process_id:
            code.val = error_table_.locked_by_this_process
            return
            
        if self.process_id and (self.process_id not in valid_process_list):
            self.semaphore.release() # invalid_lock_reset
            #== ...and then try to acquire it
            
        if self.semaphore.tryAcquire(1, timeout * 1000):
            #== Double-check this...
            if self.process_id and (self.process_id not in valid_process_list):
                code.val = error_table_.invalid_lock_reset
            else:
                code.val = 0
            # end if
            self.process_id = process_id
        else:
            # lock_wait_time_exceeded
            code.val = error_table_.lock_wait_time_exceeded
        
    def release(self, process_id, code):
        if self.semaphore.available():
            code.val = error_table_.lock_not_locked
            
        elif self.process_id != process_id:
            code.val = error_table_.locked_by_other_process
            
        else:
            self.process_id = 0
            self.semaphore.release()
            code.val = 0
            