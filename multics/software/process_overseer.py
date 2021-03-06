
from ..globals import *

include.pit
include.pds
include.rnt
include.whotab
include.process_env

from pit import pit_structure
from pds import pds_structure
from rnt import rnt_structure
from process_env import process_env_structure
from vmprocess import VirtualMulticsProcess

class ProcessOverseer(object):

    def __init__(self):
        super(ProcessOverseer, self).__init__()
        
        self.__running_processes = []
        self.__system_search_rules = {
            '':        ["-referencing_dir", "-working_dir", ">sss", ">sss>commands"],
            'default': ["-referencing_dir", "-working_dir", ">sss", ">sss>commands"],
        }
        
    @property
    def running_processes(self):
        return self.__running_processes[:]
    
    def create_process(self, login_info, CoreFunction, tty_channel=None):
        declare (clock_   = entry . returns (fixed.bin(32)))
        
        command_processor = parm()
        process_dir       = parm()
        segment           = parm()
        code              = parm()
        
        #== Make sure the specified command processor exists
        if login_info.cp_path:
            call.hcs_.get_entry_point(login_info.cp_path, command_processor)
            if command_processor.ptr == null():
                self._print_error_message("Could not find command processor %s." % (login_info.cp_path), tty_channel)
                return null()
            # end if
        # end if
        
        #== Make sure the specified home directory exists
        if login_info.homedir:
            if not GlobalEnvironment.fs.file_exists(login_info.homedir):
                self._print_error_message("No home directory for user %s." % (login_info.user_id), tty_channel)
                return null()
            # end if
        # end if
            
        #== Create a process id if one is not specified in the login_info
        process_id = login_info.process_id or clock_()
        
        #== Create the process directory
        call.hcs_.create_process_dir(process_id, process_dir, code)
        if code.val != 0 and code.val != error_table_.namedup:
            self._print_error_message("Failed to create process directory.", tty_channel)
            return null()
        # end if
        
        #== Load the system search rules
        call.hcs_.initiate(GlobalEnvironment.fs.system_control_dir, "system_search_rules", "", 0, 0, segment, code)
        if segment.ptr != null():
            self.__system_search_rules = segment.ptr
        # end if
        
        #== Fill the process initialization table structure
        pit = pit_structure()
        pit.login_name   = login_info.person_id
        pit.project      = login_info.project_id
        pit.process_type = login_info.process_type
        pit.homedir      = login_info.homedir
        pit.no_start_up  = login_info.no_start_up
        pit.time_login   = login_info.time_login #datetime.datetime.now()
        pit.process_id   = process_id
        
        #== Create the process initialization table (PIT) segment
        call.hcs_.initiate(process_dir.val, "pit", "", 0, 0, segment, code)
        if segment.ptr == null():
            call.hcs_.make_seg(process_dir.val, "pit", "", 0, segment(pit), code)
            if code.val != 0:
                self._print_error_message("Failed to create process initialization table.", tty_channel)
                return null()
            # end if
        # end if
        pit = segment.ptr
        
        pds = pds_structure()
        pds.process_stack = [ProcessStackFrame()]
        
        #== Create the process data segment (PDS)
        call.hcs_.initiate(process_dir.val, "pds", "", 0, 0, segment, code)
        if segment.ptr == null():
            call.hcs_.make_seg(process_dir.val, "pds", "", 0, segment(pds), code)
            if code.val != 0:
                self._print_error_message("Failed to create process data segment.", tty_channel)
                return null()
            # end if
        # end if
        pds = segment.ptr
        
        rnt = rnt_structure()
        rnt.search_rules = self.__system_search_rules['default']
        
        #== Create the reference name table (RNT)
        call.hcs_.initiate(process_dir.val, "rnt", "", 0, 0, segment, code)
        if segment.ptr == null():
            call.hcs_.make_seg(process_dir.val, "rnt", "", 0, segment(rnt), code)
            if code.val != 0:
                self._print_error_message("Failed to create reference name table.", tty_channel)
                return null()
            # end if
        # end if
        rnt = segment.ptr
        
        #== Create the process message segment (process.ms)
        call.hcs_.initiate(process_dir.val, "process.ms", "", 0, 0, segment, code)
        if segment.ptr == null():
            call.hcs_.make_seg(process_dir.val, "process.ms", "", 0, segment(ProcessMsgSegment()), code)
            if code.val != 0:
                self._print_error_message("Failed to create process message segment.", tty_channel)
                return null()
            # end if
        # end if
        msg = segment.ptr
        
        #== Create the core function object
        core_function = CoreFunction(command_processor.ptr)
        
        #== Fill the process env structure
        process_env = process_env_structure()
        process_env.process_id = process_id
        process_env.process_dir = process_dir.val
        process_env.pit = pit
        process_env.pds = pds
        process_env.rnt = rnt
        process_env.msg = msg
        process_env.core_function = core_function
        
        #== Create a Process object
        process = VirtualMulticsProcess(process_env)
        self.__running_processes.append(process)
        print "Created", process
        
        if process_env.pit.process_type == pit_process_type_daemon:
            GlobalEnvironment.supervisor.register_condition_handler(BreakCondition, process, self._ignore_break_condition)
            GlobalEnvironment.supervisor.add_daemon_process(process)
        elif process_env.pit.process_type == pit_process_type_interactive:
            GlobalEnvironment.supervisor.add_interactive_process(process)
        # end if
        
        return process
        
    def destroy_process(self, process):
        code = parm()
        
        process_type = process.pit().process_type
        
        print get_calling_process_().objectName() + " process_overseer waiting for " + process.objectName() + " to terminate"
        process.kill()
        if not process.wait(5000):
            print "[[[ %s did not terminate ]]]" % (process.objectName())
        
        call.hcs_.delete_branch_(process.dir(), code)
        
        self.__running_processes.remove(process)
        
        if process_type == pit_process_type_daemon:
            GlobalEnvironment.supervisor.remove_daemon_process(process)
        elif process_type == pit_process_type_interactive:
            GlobalEnvironment.supervisor.remove_interactive_process(process)
    
    def _ignore_break_condition(self):
        pass
        
    def _print_error_message(self, s, tty_channel):
        call.iox_.write(tty_channel, "\n%s\n" % (s))
        call.iox_.write(tty_channel, "Please contact System Administrator.\n")
    
#-- end class ProcessOverseer

class ProcessStackFrame(object):
    #== Various system services can use this to store persistent data for the process.
    #== E.g., the send_message_ facility can keep track of whether or not messages are
    #== being accepted as a flag in the process stack. This information would not be
    #== accessed directly by the process object itself (it wouldn't even know about the
    #== data attributes added by system services), but used behind the scenes when
    #== the associated system service functions are called. This is better than
    #== keeping the data as resident attributes of the Subroutine class instances
    #== because even though it is data only those methods know or care about, the data
    #== really 'belongs' to the process, not the system service.
    
    def __init__(self):
        self.process_timers = {}
        #== More attributes added as needed by system services...
        
    def copy(self):
        new_stack = ProcessStackFrame()
        new_stack.__dict__.update(self.__dict__.copy())
        return new_stack
        
    def assert_create(self, attrname, attrtype):
        if not hasattr(self, attrname):
            setattr(self, attrname, attrtype())
        return getattr(self, attrname)

class ProcessMsgSegment(object):

    def __init__(self):
        self.messages = []
        
    def __repr__(self):
        if not self.messages:
            return "<%s.%s with %d messages>" % (__name__, self.__class__.__name__, len(self.messages))
        else:
            from pprint import pformat
            s = pformat(self.messages)
            return "<%s.%s with %d messages>\n%s\n" % (__name__, self.__class__.__name__, len(self.messages), s)
        