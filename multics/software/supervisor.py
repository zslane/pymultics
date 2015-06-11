from pprint import pprint
import os
import re
import imp
import sys
import rsa
import time
import datetime
from collections import defaultdict

from ..globals import *
from pit import *

from PySide import QtCore, QtGui

include.login_info
include.sl_info

bitstr_pat  = r'([\'"])([01]+)\1b'
dquote_pat  = r'"[^"]*"'
squote_pat  = r'\'[^\']*\''
comment_pat = r'#[^\n]*'
calldot_pat = r'\bcall\s*\.'
callkwd_pat = r'\b(call)\s+'
dollar_pat  = r'(\$)'
pointer_pat = r'\s*(->)\s*'
patterns    = re.compile("|".join([bitstr_pat, dquote_pat, squote_pat, comment_pat, calldot_pat, callkwd_pat, dollar_pat, pointer_pat]))

class Supervisor(QtCore.QObject):

    IDLE_DELAY_TIME = 20
    
    def __init__(self, hardware):
        super(Supervisor, self).__init__()
        self.setObjectName("Multics.Supervisor")
        
        self.__hardware                  = hardware
        self.__dynamic_linker            = DynamicLinker(self)
        self.__referencing_dir           = {}
        
        GlobalEnvironment.register_supervisor(self)
        
        #== This import must occur AFTER the supervisor has been registered with the GlobalEnvironment
        import process_overseer ; reload(process_overseer)
        from process_overseer import ProcessOverseer, ProcessStackFrame
        
        self.__process_overseer          = ProcessOverseer()
        self.__system_stack              = ProcessStackFrame()
        self.__startup_datetime          = None
        self.__shutdown_datetime         = None
        self.__daemons                   = []
        self.__interactive_users         = []
        self.__system_timers             = {}
        self.__signalled_conditions      = []
        self.__condition_handlers        = defaultdict(dict)
        self.__person_name_table         = None
        self.__project_definition_tables = {}
        self.__whotab                    = None
        self.__shutdown_time_left        = -1
        self.__shutdown_message          = ""
        self.__shutdown_signal           = False
        
        self._load_site_config()
        
        self.__hardware.io.poweredDown.connect(self.hard_shutdown)
        self.__hardware.io.heartbeat.connect(self._heartbeat)
        
    @property
    def version(self):
        return "3.0"
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
        
    #== REFERENCING DIR routines ==#
    
    def get_referencing_dir(self, id):
        try:
            return self.__referencing_dir[id]
        except:
            return ""
            
    def set_referencing_dir(self, dir):
        id = self.__hardware.clock.current_time()
        self.__referencing_dir[id] = dir
        return id
        
    def clear_referencing_dir(self, id):
        try:
            self.__referencing_dir[id] = ""
        except:
            pass
            
    def is_bound_archive(self, id):
        try:
            dir = self.__referencing_dir[id]
            return ("pdd" in dir) and ("!bound_archives" in dir)
        except:
            return False
        
    def id(self):
        return 0
        
    def uid(self):
        return "Multics.Supervisor"
    
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
        with open(os.path.join(self.fs.SYSTEMROOT, "site.config"), "r") as f:
            config_text = f.read()
        # end with
        self.site_config = eval(config_text)
        self.site_config['site_name'] = os.path.basename(os.path.dirname(self.fs.SYSTEMROOT))
    
    def _send_system_greeting(self):
        self.send_to_console("%s\n" % (self.__hardware.announce))
        print                "%s" % (self.__hardware.announce)
        self.send_to_console("Multics Supervisor %s started %s, %s\n" % (self.version, self.__startup_datetime.ctime(), self.site_config['site_name']))
        print                "Multics Supervisor %s started %s, %s\n" % (self.version, self.__startup_datetime.ctime(), self.site_config['site_name'])
        self.__hardware.io.set_console_title("pyMultics Virtual Mainframe (%s)" % (self.site_config['site_name']))
        
    def _send_system_farewell(self):
        import multiprocessing
        self.send_to_console("\n:Multics Supervisor shutdown %s:\n" % (self.__shutdown_datetime.ctime()))
        print                "\n:Multics Supervisor shutdown %s:" % (self.__shutdown_datetime.ctime())
        self.send_to_console(":Virtual Multics Hardware shutdown (%d cpus offline):\n" % (self.__hardware.num_cpus))
        print                ":Virtual Multics Hardware shutdown (%d cpus offline):" % (self.__hardware.num_cpus)
        
    #== STARTUP/SHUTDOWN ==#
    
    def startup(self):
        self.__startup_datetime = datetime.datetime.now()
        self._send_system_greeting()
        self.__dynamic_linker.initialize()
        DEFAULT_SHUTDOWN_TIME = 10 * 60 # 10 minutes
        self.add_system_timer(DEFAULT_SHUTDOWN_TIME, self._shutdown_task)
        PAUSE_TO_SHUTDOWN = 3 # 3 seconds
        self.add_system_timer(PAUSE_TO_SHUTDOWN, self._shutdown_procedure)
        
    #== Unexpected shutdown (console window closed). System timers non-functioning at this point.
    def hard_shutdown(self):
        if not self.shutting_down():
            print get_calling_process_().objectName() + " calling supervisor.hard_shutdown()"
            self.__shutdown_signal = True
            self._shutdown_procedure()
    
    #== Controlled shutdown (via shutdown command). Requires system timers still be running.
    def shutdown(self):
        print get_calling_process_().objectName() + " calling supervisor.shutdown()"
        self.__shutdown_signal = True
        self.__system_timers[self._shutdown_procedure].start()
        
    def _shutdown_procedure(self):
        self.__system_timers[self._shutdown_procedure].stop()
        self._kill_daemons()
        GlobalEnvironment.deregister_supervisor()        
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
        
        # from multics.globals import call
        
        msg = ProcessMessage(msgtype, **{'from':"Multics.Supervisor", 'to':"*.*", 'text':announcement})
        call. sys_.add_process_msg ("Messenger.SysDaemon", msg, code)
    
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
            self.shutdown()
        
    #== LOW-LEVEL I/O ==#
    
    #== I/O sent to a 'null' TTY device goes to the system console
        
    def send_to_tty(self, s, tty_channel=None):
        self.__hardware.io.put_output(s, tty_channel)
    
    def send_to_console(self, s):
        self.send_to_tty(s)
    
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
        
    #== SYSTEM TIMERS ==#
    
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
    
    #== CONDITION HANDLING ==#
    
    def check_conditions(self, tty_channel, process, ignore_break_signals=False):
        if process:
            if self.__hardware.io.terminal_closed(tty_channel):
                raise DisconnectCondition
            # end if
            if not ignore_break_signals and self.__hardware.io.break_received(tty_channel):
                print "Break signal detected by " + process.objectName()
                self.send_to_tty("QUIT\n", tty_channel)
                self.invoke_condition_handler(BreakCondition, process) ### ! EXPERIMENTAL ! ###
                # raise BreakCondition
            # end if
            if self.shutting_down():
                print "Shutdown signal detected by " + process.objectName()
                raise ShutdownCondition
            # end if
            if self.condition_signalled():
                condition_instance = self.pop_condition()
                print type(condition_instance), "signal detected by " + process.objectName()
                raise condition_instance
            # end if
        # end if
        QtCore.QCoreApplication.processEvents()
    
    def signal_break(self, tty_channel=None):
        self.send_to_tty("QUIT\n", tty_channel)
        
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
        
    def register_condition_handler(self, condition, process, handler_function):
        print process.objectName(), "registering condition handler", handler_function, "for", condition.name()
        pid = process.id()
        if condition.name() not in self.__condition_handlers[pid]:
            self.__condition_handlers[pid][condition.name()] = []
        self.__condition_handlers[pid][condition.name()].append(handler_function)
        
    def deregister_condition_handler(self, condition, process):
        try:
            print process.objectName(), "deregistering condition handler for", condition.name()
            self.__condition_handlers[process.id()][condition.name()].pop()
        except:
            print process.objectName(), "No condition handler to deregister for %s." % (condition.name())
            
    def invoke_condition_handler(self, condition, process):
        print process.objectName(), "invoking %s condition handler" % (condition.name()),
        try:
            handler_function = self.__condition_handlers[process.id()][condition.name()][-1]
            print handler_function
            handler_function()
            
        except (KeyError, IndexError):
            raise condition
        except:
            raise
    
    #== DAEMON PROCESS CONTROL ==#
    
    def add_daemon_process(self, process):
        print "Supervisor adding daemon process", process.objectName()
        self.__daemons.insert(0, process)
        
    def remove_daemon_process(self, process):
        print "Supervisor removing daemon process", process.objectName()
        self.__daemons.remove(process)
        
    def get_daemon_processes(self):
        return [ daemon for daemon in self.__daemons if daemon.isRunning() ]
        
    def _kill_process(self, process):
        if process:
            self.__process_overseer.destroy_process(process)
    
    def _kill_daemons(self):
        for daemon_process in self.__daemons[:]:
            self._kill_process(daemon_process)
            # self.__daemons.remove(daemon_process)
        
    def start(self):
        self._load_user_accounts_data()
        self._create_initializer_process()
        self._create_messenger_process()
        
    def _create_initializer_process(self):
        login_info.person_id    = "Initializer"
        login_info.project_id   = "SysDaemon"
        login_info.process_type = pit_process_type_daemon
        login_info.process_id   = 0o777777000000
        try:
            import answering_service ; reload(answering_service)
            from   answering_service import AnsweringService
            initializer_daemon = self.__process_overseer.create_process(login_info, AnsweringService)
            if not initializer_daemon:
                self.send_to_console("Failed to create Initializer daemon process")
            else:
                initializer_daemon.start()
            # end if
        except:
            self.dynamic_linker.dump_traceback_()
        
    def _create_messenger_process(self):
        login_info.person_id    = "Messenger"
        login_info.project_id   = "SysDaemon"
        login_info.process_type = pit_process_type_daemon
        login_info.process_id   = 0
        try:
            import messenger ; reload(messenger)
            from   messenger import Messenger
            messenger_daemon = self.__process_overseer.create_process(login_info, Messenger)
            if not messenger_daemon:
                self.send_to_console("Failed to create Messenger daemon process")
            else:
                messenger_daemon.start()
            # end if
        except:
            self.dynamic_linker.dump_traceback_()
    
    def add_interactive_process(self, process):
        print "Supervisor adding interactive process", process.objectName()
        self.__interactive_users.insert(0, process)
        
    def remove_interactive_process(self, process):
        print "Supervisor removing interactive process", process.objectName()
        self.__interactive_users.remove(process)
        
    def get_interactive_processes(self):
        return [ process for process in self.__interactive_users if process.isRunning() ]
    
    def _load_user_accounts_data(self):
        process_dir = parm()
        branch      = parm()
        segment     = parm()
        code        = parm()
        
        from pnt import PersonNameTable
        from pdt import ProjectDefinitionTable
        from whotab import WhoTable
        
        #== Get a pointer to the PNT (create it if necessary)
        call. hcs_.initiate (self.fs.system_control_dir, "PNT.pnt", "", 0, 0, segment, code)
        self.__person_name_table = segment.ptr
        if not self.__person_name_table:
            call. hcs_.make_seg (self.fs.system_control_dir, "PNT.pnt", "", 0, segment(PersonNameTable()), code)
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
        call. hcs_.get_directory_contents (self.fs.system_control_dir, branch, segment, code)
        if code.val == 0:
            segment_list = segment.list
            #== Add SysAdmin as a project with JRCooper as a recognized user
            if not any([ name.endswith(".pdt") for name in segment_list ]):
                for project_id, alias in [("SysAdmin", "sa")]:
                    segment_name = "%s.pdt" % (project_id)
                    pdt = ProjectDefinitionTable(project_id, alias)
                    pdt.add_user("JRCooper")
                    call. hcs_.make_seg (self.fs.system_control_dir, segment_name, "", 0, segment(pdt), code)
                    segment_list.append(segment_name)
                # end for
            # end if
            for segment_name in segment_list:
                if segment_name.endswith(".pdt"):
                    call. hcs_.initiate (self.fs.system_control_dir, segment_name, "", 0, 0, segment, code)
                    self.__project_definition_tables[segment.ptr.project_id] = segment.ptr
                    if segment.ptr.alias:
                        self.__project_definition_tables[segment.ptr.alias] = segment.ptr
                    # end if
                # end if
            # end for
        # end if
        print "PROJECT DEFINITION TABLES:"
        print "--------------------------"
        pprint(self.__project_definition_tables)
        
        #== Get a pointer to the WHOTAB (create it if necessary)
        call. hcs_.initiate (self.fs.system_control_dir, "whotab", "", 0, 0, segment, code)
        self.__whotab = segment.ptr
        if not self.__whotab:
            call. hcs_.make_seg (self.fs.system_control_dir, "whotab", "", 0, segment(WhoTable()), code)
            self.__whotab = segment.ptr
            self.__whotab.sysid = self.site_config['site_name']
        # end if
        print "WHOTAB:"
        print "-------"
        pprint(self.__whotab)
        
        #== Create the LOGIN JOURNAL if necessary
        call. hcs_.make_seg (self.fs.system_control_dir, "login_journal", "", 0, segment({}), code)
        print "LOGIN JOURNAL:"
        print "--------------"
        pprint(segment.ptr)
    
class SystemTimer(object):

    def __init__(self, supervisor, interval, callback_slot, callback_args=None):
        self.__supervisor = supervisor
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
                self.__supervisor.signal_condition(get_calling_process_(), condition)
        
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
    def __init__(self, supervisor, segment_name, path_to_segment, module_containing_segment):
        segment_name = segment_name[segment_name.rfind('$')+1:]
        
        self.name = segment_name
        self.path = path_to_segment
        self.fs = supervisor.fs
        self.last_modified = supervisor.fs.get_mod_data(path_to_segment)
        self.module = module_containing_segment
        
        entry_point = getattr(module_containing_segment, segment_name)
        
        if hasattr(entry_point, "__bases__"):
            import inspect
            base_classes = inspect.getmro(entry_point)
            #== Is it a SystemSubroutine-derived class?
            if SystemSubroutine in base_classes:
                #== Instantiate one and return the object
                # print "Creating SystemSubroutine segment"
                self.segment = entry_point(supervisor)
                
            #== Is it an Subroutine-derived class?
            elif Subroutine in inspect.getmro(entry_point):
                #== Instantiate one and return the object
                # print "Creating Subroutine segment"
                self.segment = entry_point()
                
            else:
                self.segment = None
            
        #== Is it a function (or other callable)?
        elif callable(entry_point):
            #== Wrap it up as an Subroutine object
            # print "Creating function segment"
            self.segment = Subroutine(segment_name, entry_point)
            
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

    def __init__(self, supervisor):
        super(DynamicLinker, self).__init__()
        
        self.__supervisor = supervisor
        self.__filesystem = supervisor.hardware.filesystem
        self.__system_function_table = {}
        self.__system_segment_table = {}
        self.__segfault_count = 0
        
        #== CRITICAL SYSTEM CLASSES NEEDED FOR BOOTING
        self.__system_preloads = [
            (self.__filesystem.system_library_standard, "iox_"),
            (self.__filesystem.system_library_standard, "hcs_"),
            (self.__filesystem.system_library_standard, "sys_"),
        ]
        
    def initialize(self):
        self._initialize_system_functions()
        print "SYSTEM FUNCTION TABLE:"
        print "----------------------"
        pprint(self.__system_function_table)
        self._preload_critical_segments()
        print "SYSTEM SEGMENT TABLE:"
        print "---------------------"
        pprint(self.__system_segment_table)
        
    def _initialize_system_functions(self):
        import types
        excluded_symbols = ["system_privileged"]
        for module_name, module_path in self.__filesystem.list_segments(self.__filesystem.system_library_standard):
            module = self._load_python_code(module_name, module_path)
            if module:
                # print "checking for functions in", module_path
                # print dir(module)
                for symbol in dir(module):
                    if (not symbol.startswith("_")) and (symbol not in excluded_symbols) and (symbol not in self.__system_function_table):
                        obj = getattr(module, symbol)
                        if isinstance(obj, (types.FunctionType, types.BuiltinFunctionType)):
                            # print "...adding", symbol, obj
                            self.__system_function_table[symbol] = SegmentDescriptor(self.__supervisor, symbol, module_path, module)
    
    def _preload_critical_segments(self):
        for dir_name, segment_name in self.__system_preloads:
            self.load(dir_name, segment_name)
            
    def __getattr__(self, entry_point_name):
        # self.__supervisor.referencing_dir = self.__filesystem.path2path(os.path.dirname(inspect.currentframe().f_back.f_code.co_filename))
        with reference_frame(inspect.currentframe().f_back) as frame_id:
            entry_point = self.snap(entry_point_name, frame_id=frame_id)
        # self.__supervisor.referencing_dir = ""
        if entry_point:
            return entry_point
        else:
            raise SegmentFault(entry_point_name)
    
    #== Callable by anyone
    def dump_traceback_(self):
        import traceback
        traceback.print_exc()
        excmsg = traceback.format_exc().replace("{", "{{").replace("}", "}}")
        self.__supervisor.send_to_tty(excmsg, get_calling_process_().tty())
        
    #== Called by hcs_ ==#
    
    @property
    def segfault_count(self):
        return self.__segfault_count
        
    @property
    def known_segment_table(self):
        process = get_calling_process_()
        try:
            return process.kst()
        except:
            return self.__system_segment_table
        
    def load(self, dir_name, segment_name):
        multics_path = self.__filesystem.merge_path(dir_name, segment_name)
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
                # self.known_segment_table[segment_name] = segment_data_ptr
                self.known_segment_table[multics_path] = segment_data_ptr
                return segment_data_ptr
            else:
                #== This allows us to load object segments via hcs_.initiate() as
                #== is done (repeatedly) in starrunners with >sss>do.py. Does this
                #== mess something up though? Maybe not now that we're using the
                #== full Multics path as the KST key. Something to keep an eye on.
                
                # print "...failed to find/load file...trying to snap it instead"
                segment_data_ptr = self.snap(segment_name, dir_name)
                # print "...snap results:", segment_data_ptr
                return segment_data_ptr
            # end if
        except:
            # print "...failed to find/load file...trying to snap it instead"
            segment_data_ptr = self.snap(segment_name, dir_name)
            # print "...snap results:", segment_data_ptr
            return segment_data_ptr
        
    def snap(self, segment_name, known_location=None, frame_id=None):
        #== Special case segment names: 'print', 'list'
        special_seg_names = {
            'print': "print_",
            'list' : "list_",
        }
        segment_name = special_seg_names.get(segment_name, segment_name)
        
        try:
            entry_point = self._find_segment(segment_name)
            return entry_point
            
        except SegmentFault:
            # print "...segment fault"
            self.__segfault_count += 1
            module, module_path = self._find_module(segment_name, known_location, frame_id=frame_id)
            if module:
                self.known_segment_table[segment_name] = SegmentDescriptor(self.__supervisor, segment_name, module_path, module)
                entry_point = self.known_segment_table[segment_name].segment
                # print "   found", entry_point
                return entry_point
            else:
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
                # print "...found in KST"
                return seg_desc.segment
            except KeyError:
                # print "...raising SegmentFault"
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
                # print "...raising SegmentFault"
                raise SegmentFault(segment_name)
                
    def _find_module(self, segment_name, known_location=None, additional_locations=[], frame_id=None): 
        if known_location:
            search_paths = [ known_location ]
        else:
            try:
                process = get_calling_process_()
                search_paths = process.search_rules(frame_id)
            except:
                search_paths = [ self.__filesystem.system_library_standard ]
            # end try
        # end if
        search_paths.extend(additional_locations)
        
        segment_name, _, entryname = segment_name.partition('$')
        
        #== Try to find the segment and add it to the KST
        for multics_path in search_paths:
            # print "...searching", multics_path
            for ext in [".pyo", ".py", ""]: # <-- empty string at end for finding bound archives (which have no extension)
                module_path = self.__filesystem.path2path(multics_path, segment_name + ext)
                # print module_path
                if self.__filesystem.file_exists(module_path):
                    #== If module_path isn't a bound archive, this is a NOP
                    module_path = self.__filesystem.unpack_bound_archive(entryname or segment_name, module_path)
                    # print module_path
                    try:
                        module = self._load_python_code(segment_name, module_path)
                        return module, module_path
                    except SyntaxError:
                        raise
                    except:
                        #== Invalid python module, but not a syntax error...
                        self.dump_traceback_()
                        raise InvalidSegmentFault(segment_name)
                    # end try
                # end if
            # end for
        # end for
        return None, None
    
    def _load_python_code(self, module_name, module_path):
        #== Turn the module name into a unique namespace based on the process id
        process = get_calling_process_()
        idstring = "%015X" % (process.id())
        namespace = module_name + "_" + idstring
        # print "%s: import %s as %s\t(using %s)" % (process.uid(), module_name, namespace, module_path)
        
        if module_path.endswith(".pyo"):
            return imp.load_compiled(namespace, module_path)
        else:
            return imp.load_source(namespace, module_path)
            # return imp.load_source(namespace, self.pl1_preprocess(process.uid(), module_path))
        
    def pl1_preprocess(self, user_id, module_path):
        def replacer(m):
            if m.group(2):
                return "0b" + m.group(2)
            elif m.group(3):
                return "GlobalEnvironment.linker."
            elif m.group(4) or m.group(5):
                return "."
            else:
                return m.group(0)
            # end if
        # end def
        with open(module_path) as inf:
            text = inf.read()
        # end with
        module_name = os.path.basename(module_path)
        temp_path = self.__filesystem.path2path(self.__filesystem.temp_dir_dir, "%s.%s" % (user_id, module_name))
        with open(temp_path, "w") as outf:
            outf.write(patterns.sub(replacer, text))
        # end with
        return temp_path
        