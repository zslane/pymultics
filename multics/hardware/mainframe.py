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

    __version__ = "v1.0.0"
    
    def __init__(self, init_args=[]):
        t = QtCore.QThread.currentThread()
        t.setObjectName("Multics.Supervisor")
        
        self._create_hardware_resources()

        #== Create hardware subsystems
        self.__io_subsystem = IOSubsystem()
        self.__filesystem = VirtualMulticsFileSystem(init_args)

        system_includes_path = os.path.join(self.filesystem.path2path(self.filesystem.system_library_standard), "includes")
        if system_includes_path not in sys.path:
            sys.path.append(system_includes_path)
        
    def _create_hardware_resources(self):
        self.__startup_time = self._load_hardware_statefile()
        self.__clock = HardwareClock(self.__startup_time)
        self.announce = "Virtual Multics Hardware %s Initialized" % (self.__version__)

    @property
    def clock(self): return self.__clock
    @property
    def io(self): return self.__io_subsystem
    @property
    def filesystem(self): return self.__filesystem

    def attach_terminal(self, terminal):
        self.__io_subsystem.attach_terminal(terminal)

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

    def __init__(self):
        super(IOSubsystem, self).__init__()

        self.__input_buffer = []
        self.__linefeed = False
        self.__break_signal = False
        self.__closed_signal = False
        self.__terminal = None
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
    
    def attach_terminal(self, terminal):
        self.__terminal = terminal
        if self.__terminal:
            self.__terminal.heartbeat.connect(self.heartbeat)
            self.__terminal.io.textEntered.connect(self._receive_string)
            self.__terminal.io.lineFeed.connect(self._receive_linefeed)
            self.__terminal.io.breakSignal.connect(self._receive_break)
            self.__terminal.closed.connect(self._close_terminal)

    def attach_tty_process(self, process_id):
        self.__terminal_process_id = process_id
        
    def detach_tty_process(self, process_id):
        if self.__terminal_process_id == process_id:
            self.__terminal_process_id = 0
            
    def attached_tty_process(self):
        return self.__terminal_process_id
        
    def linefeed_received(self):
        flag, self.__linefeed = self.__linefeed, False
        return flag
        
    def break_received(self):
        flag, self.__break_signal = self.__break_signal, False
        return flag
        
    def terminal_closed(self):
        return self.__closed_signal
        
    def has_input(self):
        return self.__input_buffer != []

    def get_input(self):
        try:
            return self.__input_buffer.pop(0)
        except:
            return None
    
    def flush_input(self):
        self.__input_buffer = []
        self.__break_signal = False
        self.__linefeed = False
        
    def set_input_mode(self, mode):
        if self.__terminal:
            self.__terminal.setEchoMode.emit(mode)
        
    def put_output(self, s):
        if self.__terminal:
            self.__terminal.transmitString.emit(s)

    def shutdown(self):
        if self.__terminal:
            self.__terminal.shutdown.emit()
        
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
            p = p.replace(">", "\\").lstrip("\\")
            p = os.path.join(self.FILESYSTEMROOT, p)
            if f:
                p = os.path.join(p, f)
            # end if
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
        print "_resolve_path:", path
        path = path.lstrip("<").rstrip(">").replace(">>", ">").replace("<>", "<").replace("><", "<")
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
        print "resolves to:", path
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
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
    
    def read_file(self, filepath):
        filepath = self.native_path(filepath)
        with open(filepath, "rb") as f:
            try:
                return pickle.load(f)
            except:
                f.seek(0)
                return f.read()
            
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
            
    def get_directory_contents(self, dirpath):
        try:
            dirpath = self.native_path(dirpath)
            contents = glob.glob(os.path.join(dirpath, "*"))
            file_list = map(os.path.basename, filter(os.path.isfile, contents))
            dir_list = map(os.path.basename, filter(os.path.isdir, contents))
            return (dir_list, file_list, 0)
        except:
            return (None, None, -1)
    
    def segment_data_ptr(self, filepath, data_instance=None):
        filepath = self.native_path(filepath)
        if data_instance is not None:
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
        self._update_data(self.CACHE_IN)
        
    @property
    def filepath(self):
        return self.__filepath
        
    def update(self):
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
        pass
        
    def __exit__(self, etype, value, traceback):
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
        
    def __repr__(self):
        return repr(self.__data)
        
class LockedSegment(object):

    def __init__(self, memory_mapped_ptr, timeout):
        self.__ptr = memory_mapped_ptr
        self.__timeout = timeout
        
    def __enter__(self):
        declare (code = parm)
        call.set_lock_.lock(self.__ptr, self.__timeout, code)
        if code.val != 0:
            self.__ptr = None
        return code.val
        
    def __exit__(self, etype, value, traceback):
        declare (code = parm)
        if etype:
            pass
        elif self.__ptr:
            self.__ptr.update()
            call.set_lock_.unlock(self.__ptr, code)
            