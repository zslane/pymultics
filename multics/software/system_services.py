from pprint import pprint
import os
import imp
import sys
import rsa
import time
import datetime

from ..globals import *
from pit import *

from PySide import QtCore, QtGui

include.login_info
include.sl_info

class SystemServices(QtCore.QObject):

    __version__ = "v1.0.0"
    
    IDLE_DELAY_TIME = 20
    
    def __init__(self, hardware):
        super(SystemServices, self).__init__()
        self.setObjectName("Multics.Supervisor")
        
        self.__hardware = hardware
        self.__dynamic_linker = DynamicLinker(self)
        self.__initializer = None
        self.__daemons = []
        self.__startup_datetime = None
        self.__shutdown_datetime = None
        self.__system_timers = {}
        self.__signalled_conditions = []
        self.__person_name_table = None
        self.__project_definition_tables = {}
        self.__whotab = None
        self.__shutdown_time_left = -1
        self.__shutdown_message = ""
        self.__shutdown_signal = False
        
        self.__hardware.io.terminalClosed.connect(self._kill_daemons)
        self.__hardware.io.heartbeat.connect(self._heartbeat)
        
        GlobalEnvironment.register_system_services(self, self.__dynamic_linker)
        
        from process_overseer import ProcessOverseer, ProcessStack
        self.__process_overseer = ProcessOverseer(self)
        self.__system_stack = ProcessStack()
        
        self._load_site_config()
        
    @property
    def hardware(self):
        return self.__hardware
    @property
    def fs(self):
        return self.__hardware.filesystem
    @property
    def dynamic_linker(self):
        return self.__dynamic_linker
    @property
    def pnt(self):
        return self.__person_name_table
    @property
    def pdt(self):
        return self.__project_definition_tables
    @property
    def whotab(self):
        return self.__whotab
    @property
    def stack(self):
        return self.__system_stack
        
    def id(self):
        return 0
    
    def _msleep(self, milliseconds):
        QtCore.QThread.msleep(milliseconds)
        
    def _heartbeat(self):
        self._process_timers()
        
    def _process_timers(self):
        for routine_key in self.__system_timers.keys():
            timer = self.__system_timers[routine_key]
            if timer.dead():
                del self.__system_timers[routine_key]
            else:
                timer.check()
        
    def _load_site_config(self):
        SYSTEMROOT = os.path.dirname(self.fs.FILESYSTEMROOT)
        with open(os.path.join(SYSTEMROOT, "site.config"), "r") as f:
            config_text = f.read()
        # end with
        self.site_config = eval(config_text)
        self.site_config['site_name'] = os.path.basename(os.path.dirname(SYSTEMROOT))
    
    def _send_system_greeting(self):
        self.__hardware.io.put_output("%s\n" % (self.__hardware.announce))
        self.__hardware.io.put_output("System Services %s started on %s\n" % (self.__version__, self.__startup_datetime.ctime()))
        
    def _send_system_farewell(self):
        self.__hardware.io.put_output("\n:System Services shutdown on %s:\n" % (self.__shutdown_datetime.ctime()))
        
    #== CONDITION HANDLERS ==#
    
    def _on_condition__break(self):
        # do cleanup ... like clearing application timers and stuff
        # self.__session_thread._on_condition__break()
        pass
        
    #== STARTUP/SHUTDOWN ==#
    
    def startup(self):
        self.__startup_datetime = datetime.datetime.now()
        self._send_system_greeting()
        self.__dynamic_linker.initialize()
        DEFAULT_SHUTDOWN_TIME = 10 * 60 # 10 minutes
        self.add_system_timer(DEFAULT_SHUTDOWN_TIME, self._shutdown_task)
        
    def shutdown(self):
        print get_calling_process_().objectName() + " calling system_services.shutdown()"
        self.__shutdown_signal = True
        timer = self.add_system_timer(3, self._shutdown_procedure)
        timer.start()
        
    def _shutdown_procedure(self):
        self.__system_timers[self._shutdown_procedure].stop()
        self._kill_daemons()
        self.__shutdown_datetime = datetime.datetime.now()
        self._send_system_farewell()
        self.__hardware.shutdown()
        
    def shutting_down(self):
        return self.__shutdown_signal
        
    def shutdown_started(self):
        return self.__system_timers[self._shutdown_task].active()
    
    def start_shutdown(self, time_left, message):
        self.__shutdown_time_left = time_left
        self.__shutdown_message = message
        self._shutdown_task()
        
    def cancel_shutdown(self):
        CANCELLED = -1
        if self.shutdown_started():
            self.__system_timers[self._shutdown_task].stop()
            self._send_shutdown_message("shutdown_announcement", CANCELLED)
    
    def _send_shutdown_message(self, msgtype, how_long=-1):
        code = parm()
        
        announcement = ""
        if msgtype == "shutdown_announcement":
            if how_long > 0:
                if how_long >= 60:
                    how_long /= 60
                    units = "minutes"
                else:
                    units = "seconds"
                # end if
                announcement = "System is shutting down in %d %s. %s" % (how_long, units, self.__shutdown_message)
            else:
                announcement = "System shutdown cancelled."
            # end if
        # end if
        
        from multics.globals import call
        
        msg = ProcessMessage(msgtype, **{'from':"Multics.Supervisor", 'to':"*.*", 'text':announcement})
        call.sys_.add_process_msg("Messenger.SysDaemon", msg, code)
    
    def _shutdown_task(self):
        self.__system_timers[self._shutdown_task].stop()
        
        if self.__shutdown_time_left > 0:
            self._send_shutdown_message("shutdown_announcement", self.__shutdown_time_left)
            
            if self.__shutdown_time_left > 600: # 10 mins
                next_time = 600
                self.__shutdown_time_left -= 600
            elif self.__shutdown_time_left > 60: # 1 min
                next_time = 60
                self.__shutdown_time_left -= 60
            elif self.__shutdown_time_left > 15:
                next_time = 10
                self.__shutdown_time_left -= 10
            else:
                next_time = self.__shutdown_time_left
                self.__shutdown_time_left = 0
            # end if
            
            self.__system_timers[self._shutdown_task].start(next_time)
            
        elif self.__shutdown_time_left == 0:
            self._send_shutdown_message("shutdown") # <-- this is how we force shutdown logout for other logged in users
            self.shutdown()
        
    #== LOW-LEVEL I/O ==#
    #== These functions can be used to do basic TTY I/O in the absence of
    #== a process
    
    def llout(self, s, tty_channel=None):
        self.__hardware.io.put_output(s, tty_channel)
        
    def llin(self, block=False, tty_channel=None):
        while not self.__hardware.io.has_input(tty_channel) and block:
        
            if self.__hardware.io.terminal_closed(tty_channel):
                raise DisconnectCondition
            # end if
            if self.__hardware.io.break_received(tty_channel):
                print "Break signal detected by " + get_calling_process_().objectName()
                raise BreakCondition
            # end if
            if self.shutting_down():
                print "Shutdown signal detected by " + get_calling_process_().objectName()
                raise ShutdownCondition
            # end if
            if self.condition_signalled():
                condition_instance = self.pop_condition()
                print type(condition_instance), "signal detected by " + get_calling_process_().objectName()
                raise condition_instance
            # end if
            
            QtCore.QCoreApplication.processEvents()
            
            self._msleep(self.IDLE_DELAY_TIME) # in milliseconds
        # end while
        
        if self.__hardware.io.terminal_closed(tty_channel):
            raise DisconnectCondition
        # end if
        if self.__hardware.io.break_received(tty_channel):
            print "Break signal detected by " + get_calling_process_().objectName()
            raise BreakCondition
        # end if
        if self.shutting_down():
            print "Shutdown signal detected by " + get_calling_process_().objectName()
            raise ShutdownCondition
        # end if
        if self.condition_signalled():
            condition_instance = self.pop_condition()
            print type(condition_instance), "signal detected by " + get_calling_process_().objectName()
            raise condition_instance
        # end if
        
        input = self.__hardware.io.get_input(tty_channel)
        return input
        
    def wait_for_linefeed(self, tty_channel=None):
        while not self.__hardware.io.linefeed_received(tty_channel):
            QtCore.QCoreApplication.processEvents()
            
            if self.__hardware.io.terminal_closed(tty_channel):
                raise DisconnectCondition
            # end if
            if self.shutting_down():
                print "Shutdown signal detected by " + get_calling_process_().objectName()
                raise ShutdownCondition
            # end if
            
            self._msleep(self.IDLE_DELAY_TIME) # in milliseconds
        # end while
        self.__hardware.io.flush_input(tty_channel)
        
    def set_input_mode(self, mode, tty_channel=None):
        self.__hardware.io.set_input_mode(mode, tty_channel)
        
    def make_timer(self, interval, callback, data=None):
        timer = SystemTimer(self, interval, callback, data)
        return timer
    
    def add_system_timer(self, interval, callback, data=None):
        timer = self.make_timer(interval, callback, data)
        self.__system_timers[callback] = timer
        return timer
    
    def sleep(self, seconds):
        self._msleep(seconds * 1000)
        
    def encrypt_password(self, password, pubkey=None):
        if pubkey:
            return rsa.encode(password, pubkey)
        else:
            pubkey, prvkey = rsa.keygen(2 ** 128)
            encrypted_password = rsa.encode(password, pubkey)
            return (encrypted_password, pubkey)
    
    #== BREAK CONDITION HANDLING ==#
    
    def signal_break(self, tty_channel=None):
        self.__hardware.io.put_output("BREAK\n", tty_channel)
        self._on_condition__break()
        
    def signal_condition(self, signalling_process, condition_instance):
        self.__signalled_conditions.append( (signalling_process, condition_instance) )
        
    def condition_signalled(self):
        process = get_calling_process_()
        conditions = [ c for p, c in self.__signalled_conditions if p == process ]
        return conditions != []
        
    def pop_condition(self):
        process = get_calling_process_()
        for signalling_process, condition_instance in self.__signalled_conditions:
            if signalling_process == process:
                self.__signalled_conditions.remove( (signalling_process, condition_instance) )
                return condition_instance
            # end if
        # end for
        return None
        
    #== THREAD CONTROL ==#
    
    def get_calling_process(self):
        calling_process = QtCore.QThread.currentThread()
        return calling_process
        
    def add_daemon_process(self, process):
        print "Adding daemon process", process.objectName()
        self.__daemons.insert(0, process)
        
    def get_daemon_processes(self):
        return [ daemon for daemon in self.__daemons if daemon.isRunning() ]
        
    def _kill_process(self, process):
        if process:
            keep_process_data = (process == self.__initializer)
            self.__process_overseer.destroy_process(process, keep_process_data)
    
    def _kill_daemons(self):
        for daemon_process in self.__daemons[:]:
            self._kill_process(daemon_process)
            self.__daemons.remove(daemon_process)
        # end for
        
    def start(self):
        self._load_user_accounts_data()
        self._create_initializer_process()
        self._create_messenger_process()
        
    def _create_initializer_process(self):
        login_info.person_id = "Initializer"
        login_info.project_id = "SysDaemon"
        login_info.process_type = pit_process_type_daemon
        login_info.process_id = 0o777777000000
        login_info.homedir = ">sc1"
        login_info.cp_path = ">sss>default_cp"
        try:
            from answering_service import AnsweringService
            self.__initializer = self.__process_overseer.create_process(login_info, AnsweringService)
            if not self.__initializer:
                self.llout("Failed to create Initializer process")
            else:
                self.__initializer.start()
            # end if
        except:
            self.dynamic_linker.dump_traceback_()
        
    def _create_messenger_process(self):
        login_info.person_id = "Messenger"
        login_info.project_id = "SysDaemon"
        login_info.process_type = pit_process_type_daemon
        login_info.process_id = 0
        login_info.homedir = ">sc1"
        login_info.cp_path = ">sss>default_cp"
        try:
            from messenger import Messenger
            daemon = self.__process_overseer.create_process(login_info, Messenger)
            if not daemon:
                self.llout("Failed to create Messenger process")
            else:
                daemon.start()
            # end if
        except:
            self.dynamic_linker.dump_traceback_()
            
    def _load_user_accounts_data(self):
        process_dir = parm()
        branch      = parm()
        segment     = parm()
        code        = parm()
        
        from pnt import PersonNameTable
        from pdt import ProjectDefinitionTable
        from whotab import WhoTable
        from multics.globals import call
        # call = multics.globals.call
        
        #== Get a pointer to the PNT (create it if necessary)
        call.hcs_.initiate(self.fs.system_control_dir, "person_name_table", "", 0, 0, segment, code)
        self.__person_name_table = segment.ptr
        if not self.__person_name_table:
            call.hcs_.make_seg(self.fs.system_control_dir, "person_name_table", "", 0, segment(PersonNameTable()), code)
            self.__person_name_table = segment.ptr
            #== Add JRCooper/jrc as a valid user to start with
            with self.__person_name_table:
                self.__person_name_table.add_person("JRCooper", alias="jrc", default_project_id="SysAdmin")
            # end with
        # end if
        print "PERSON NAME TABLE:"
        print "------------------"
        pprint(self.__person_name_table)
        
        #== Make a dictionary of PDTs (project definition tables)
        call.hcs_.get_directory_contents(self.fs.system_control_dir, branch, segment, code)
        if code.val == 0:
            segment_list = segment.list
            #== Add SysAdmin as a project with JRCooper as a recognized user
            if not any([ name.endswith(".pdt") for name in segment_list ]):
                for project_id, alias in [("SysAdmin", "sa")]:
                    segment_name = "%s.pdt" % (project_id)
                    pdt = ProjectDefinitionTable(project_id, alias)
                    pdt.add_user("JRCooper")
                    call.hcs_.make_seg(self.fs.system_control_dir, segment_name, "", 0, segment(pdt), code)
                    segment_list.append(segment_name)
                # end for
            # end if
            for segment_name in segment_list:
                if segment_name.endswith(".pdt"):
                    call.hcs_.initiate(self.fs.system_control_dir, segment_name, "", 0, 0, segment, code)
                    self.__project_definition_tables[segment.ptr.project_id] = segment.ptr
                    self.__project_definition_tables[segment.ptr.alias] = segment.ptr
                # end if
            # end for
        # end if
        print "PROJECT DEFINITION TABLES:"
        print "--------------------------"
        pprint(self.__project_definition_tables)
        
        #== Get a pointer to the WHOTAB (create it if necessary)
        call.hcs_.initiate(self.fs.system_control_dir, "whotab", "", 0, 0, segment, code)
        self.__whotab = segment.ptr
        if not self.__whotab:
            call.hcs_.make_seg(self.fs.system_control_dir, "whotab", "", 0, segment(WhoTable()), code)
            self.__whotab = segment.ptr
        # end if
        print "WHOTAB:"
        print "-------"
        pprint(self.__whotab)
    
class SystemTimer(object):

    def __init__(self, system_services, interval, callback_slot, callback_args=None):
        self.__system_services = system_services
        self.__interval_time = interval # assumed to be in seconds
        self.__callback_slot = callback_slot
        self.__callback_args = callback_args
        self.__alive = True
        self.__started = False
        
    def start(self, new_interval=None):
        if new_interval is not None:
            self.__interval_time = new_interval
        self.__started = True
        self.__start_time = time.clock()
        
    def stop(self):
        self.__started = False
        
    def kill(self):
        self.stop()
        self.__alive = False
        
    def active(self):
        return self.__started
        
    def dead(self):
        return not self.__alive
        
    def check(self):
        if self.triggered():
            try:
            
                if self.__callback_args is not None:
                    self.__callback_slot(self.__callback_args)
                else:
                    self.__callback_slot()
                    
            except NonLocalGoto as condition:
                self.__system_services.signal_condition(get_calling_process_(), condition)
        
    def triggered(self):
        if self.__started:
            #== Single-shot trigger
            if self.__interval_time == 0:
                self.stop()
                return True
                
            #== Repeating trigger
            time_now = time.clock()
            if time_now - self.__start_time >= self.__interval_time:
                self.__start_time = time_now
                return True
            else:
                return False
        else:
            return False
            
class SegmentDescriptor(QtCore.QObject):
    def __init__(self, system_services, segment_name, path_to_segment, module_containing_segment):
        self.name = segment_name
        self.path = path_to_segment
        self.fs = system_services.fs
        self.last_modified = system_services.fs.get_mod_data(path_to_segment)
        self.module = module_containing_segment
        
        entry_point = getattr(module_containing_segment, segment_name)
        
        if hasattr(entry_point, "__bases__"):
            import inspect
            base_classes = inspect.getmro(entry_point)
            #== Is it a SystemExecutable-derived class?
            if SystemExecutable in base_classes:
                #== Instantiate one and return the object
                # print "Creating SystemExecutable segment"
                self.segment = entry_point(system_services)
                
            #== Is it an Executable-derived class?
            elif Executable in inspect.getmro(entry_point):
                #== Instantiate one and return the object
                # print "Creating Executable segment"
                self.segment = entry_point()
                
            else:
                self.segment = None
            
        #== Is it a function (or other callable)?
        elif callable(entry_point):
            #== Wrap it up as an Executable object
            # print "Creating function segment"
            self.segment = Executable(segment_name, entry_point)
            
        else:
            # print "Creating null segment"
            self.segment = None
            
    def _filepath(self):
        return self.path
        
    def is_out_of_date(self):
        return self.last_modified != self.fs.get_mod_data(self.path)
    
    def __repr__(self):
        return "<%s.SegmentDescriptor %s>" % (__name__, self.path)
        
class DynamicLinker(QtCore.QObject):

    system_preloads = [
        #== CRITICAL SYSTEM CLASSES NEEDED FOR BOOTING
        "hcs_",
        "sys_",
    ]
    
    def __init__(self, system_services):
        super(DynamicLinker, self).__init__()
        
        self.__system_services = system_services
        self.__filesystem = system_services.hardware.filesystem
        self.__system_function_table = {}
        self.__system_segment_table = {}
        self.__segfault_count = 0
        
    def initialize(self):
        self._initialize_system_functions()
        print "SYSTEM FUNCTION TABLE:"
        print "----------------------"
        pprint(self.__system_function_table)
        
    def _initialize_system_functions(self):
        import types
        excluded_symbols = ["system_privileged"]
        for module_name, module_path in self.__filesystem.list_segments(self.__filesystem.system_library_standard):
            module = self._load_python_code(module_name, module_path)
            if module:
                # print "checking for functions in", module_path
                # print dir(module)
                for symbol in dir(module):
                    if (not symbol.startswith("_")) and (symbol not in excluded_symbols):
                        obj = getattr(module, symbol)
                        if isinstance(obj, (types.FunctionType, types.BuiltinFunctionType)):
                            # print "...adding", symbol, obj
                            self.__system_function_table[symbol] = SegmentDescriptor(self.__system_services, symbol, module_path, module)
    
    def __getattr__(self, entry_point_name):
        entry_point = self.snap(entry_point_name)
        if entry_point:
            return entry_point
        else:
            raise SegmentFault(entry_point_name)
    
    #== Callable by anyone
    def dump_traceback_(self):
        import traceback
        traceback.print_exc()
        excmsg = traceback.format_exc().replace("{", "{{").replace("}", "}}")
        self.__system_services.llout(excmsg)
        
    #== Called by hcs_ ==#
    
    #== clear_kst() won't be necessary once KSTs are stored on the new Process objects.
    # def clear_kst(self):
        # process = self.__system_services.get_calling_process()
        # process.clear_kst()
    
    @property
    def segfault_count(self):
        return self.__segfault_count
        
    @property
    def known_segment_table(self):
        # return self.__known_segment_table
        process = get_calling_process_()
        try:
            return process.kst()
        except:
            return self.__system_segment_table
            # return self.__system_services.session_thread.kst()
        
    def load(self, dir_name, segment_name):
        # print "Trying to load", dir_name, segment_name
        multics_path = dir_name + ">" + segment_name
        native_path = self.__filesystem.path2path(multics_path)
        
        #== First look in the KST for a matching filepath
        for segment_data_ptr in self.known_segment_table.values():
            if segment_data_ptr._filepath() == native_path:
                # print "...found in KST by filepath", segment_data_ptr
                return segment_data_ptr
            # end if
        # end for
        
        # print "...opening", native_path
        try:
            # print "File exists =", self.__filesystem.file_exists(native_path)
            if self.__filesystem.file_exists(native_path):
                segment_data_ptr = self.__filesystem.segment_data_ptr(native_path)
                # print "Adding to KST:", segment_name, "->", segment_data_ptr, native_path
                self.known_segment_table[segment_name] = segment_data_ptr
                return segment_data_ptr
            else:
                return None
            # end if
        except:
            # print "...failed to find/load file...trying to snap it instead"
            return None # self.snap(segment_name, dir_name)
        
    def snap(self, segment_name, known_location=None):
        #== Special case segment names: 'print',
        if segment_name == "print":
            segment_name = "print_"
        # end if
        
        try:
            entry_point = self._find_segment(segment_name)
            return entry_point
            
        except SegmentFault:
            # print "...segment fault"
            self.__segfault_count += 1
            if known_location:
                search_paths = [ known_location ]
            else:
                try:
                    process = get_calling_process_()
                    search_paths = process.search_paths
                except:
                    search_paths = [ self.__filesystem.system_library_standard ]
                # end try
            # end if
            
            #== Try to find the segment and add it to the KST
            for multics_path in search_paths:
                # print "...searching", multics_path
                module_path = self.__filesystem.path2path(multics_path, segment_name + ".py")
                # module_path = os.path.join(native_path, segment_name + ".py")
                # print module_path
                if self.__filesystem.file_exists(module_path):
                    try:
                        module = self._load_python_code(segment_name, module_path)
                    except SyntaxError:
                        raise
                    except:
                        #== Invalid python module...probably a syntax error...
                        self.dump_traceback_()
                        raise InvalidSegmentFault(segment_name)
                        
                    self.known_segment_table[segment_name] = SegmentDescriptor(self.__system_services, segment_name, module_path, module)
                    entry_point = self.known_segment_table[segment_name].segment
                    # print "   found", entry_point
                    return entry_point
                # end if
            # end for
            return None
            
    def unsnap(self, segment_name):
        self._unlink_segment(segment_name)
        
    def _find_segment(self, segment_name):
        # print "Searching for segment", segment_name
        try:
            entry_point = self.__system_function_table[segment_name].segment
            # print "...found in SFT"
            return entry_point
        except KeyError:
            try:
                # process = get_calling_process_()
                # print "Current process", process.objectName(), segment_name
                seg_desc = self.known_segment_table[segment_name]
                if seg_desc.is_out_of_date():
                    # print "...found in KST but newer version available"
                    raise SegmentFault(segment_name)
                # entry_point = self.known_segment_table[segment_name].segment
                # print "...found in KST"
                # return entry_point
                return seg_desc.segment
            except KeyError:
                raise SegmentFault(segment_name)

    def _unlink_segment(self, segment_name):
        # print "Unlinking segment", segment_name
        try:
            del self.__system_function_table[segment_name]
            # print "...removed from SFT"
        except KeyError:
            try:
                del self.known_segment_table[segment_name]
                # print "...removed from KST"
            except KeyError:
                raise SegmentFault(segment_name)
    
    def _load_python_code(self, module_name, module_path):
        # base_path, _ = os.path.split(module_path)
        # for ext in [".pyo", ".pyc"]:
            # compiled_module_path = os.path.join(base_path, ext)
            # if self.__filesystem.file_exists(compiled_module_path):
                # return imp.load_compiled(module_name, compiled_module_path)
                
        #== We disable the loading of optimized modules until main development is done
        return imp.load_source(module_name, module_path)
        