
from ..globals import *

include.pit
include.pds
include.whotab
include.process_env

from pit import pit_structure
from pds import pds_structure
from process_env import process_env_structure

class ProcessOverseer(object):

    def __init__(self, supervisor):
        super(ProcessOverseer, self).__init__()
        
        self.supervisor = supervisor
        self.__running_processes = []
        
    @property
    def running_processes(self):
        return self.__running_processes[:]
    
    def create_process(self, login_info, CoreFunction):
        
        declare (clock_            = entry . returns (fixed.bin(32)),
                 command_processor = parm,
                 process_dir       = parm,
                 segment           = parm,
                 code              = parm)
        
        #== Make sure the specified command processor exists
        call.hcs_.get_entry_point(login_info.cp_path, command_processor)
        if command_processor.ptr == null():
            self._print_error_message("Could not find command processor %s." % (login_info.cp_path))
            return null() #System.LOGOUT
        # end if
            
        #== Make sure the specified home directory exists
        if not self.supervisor.hardware.filesystem.file_exists(login_info.homedir):
            self._print_error_message("No home directory for user %s." % (login_info.user_id))
            return null() #System.LOGOUT
        # end if
            
        #== Create a process id if one is not specified in the login_info
        process_id = login_info.process_id or clock_()
        
        #== Create the process directory
        call.hcs_.create_process_dir(process_id, process_dir, code)
        if code.val != 0 and code.val != error_table_.namedup:
            self._print_error_message("Failed to create process directory.")
            return null() #System.LOGOUT
        # end if
        
        #== Fill the process initialization table structure
        pit = pit_structure()
        pit.login_name   = login_info.person_id
        pit.project      = login_info.project_id
        pit.process_type = login_info.process_type
        pit.homedir      = login_info.homedir
        pit.time_login   = login_info.time_login #datetime.datetime.now()
        pit.process_id   = process_id
        
        #== Create the process initialization table (PIT) segment
        call.hcs_.initiate(process_dir.val, "pit", segment, code)
        if segment.ptr == null():
            call.hcs_.make_seg(process_dir.val, "pit", segment(pit), code)
            if code.val != 0:
                self._print_error_message("Failed to create process initialization table.")
                return null() #ystem.LOGOUT
            # end if
        # end if
        pit = segment.ptr
        
        pds = pds_structure()
        pds.process_stack = ProcessStack(login_info.homedir)
        pds.lock_id = clock_()
        
        #== Create the process data segment (PDS)
        call.hcs_.initiate(process_dir.val, "pds", segment, code)
        if segment.ptr == null():
            call.hcs_.make_seg(process_dir.val, "pds", segment(pds), code)
            if code.val != 0:
                self._print_error_message("Failed to create process data segment.")
                return null() #ystem.LOGOUT
            # end if
        # end if
        pds = segment.ptr
        
        #== Create the process message segment (Person_Id.mbx)
        call.hcs_.initiate(process_dir.val, login_info.person_id + ".mbx", segment, code)
        if segment.ptr == null():
            call.hcs_.make_seg(process_dir.val, login_info.person_id + ".mbx", segment(ProcessMbx()), code)
            if code.val != 0:
                self._print_error_message("Failed to create process message segment.")
                return null() #ystem.LOGOUT
            # end if
        # end if
        mbx = segment.ptr
        
        #== Create the core function object
        core_function = CoreFunction(self.supervisor, command_processor.ptr)
        
        #== Fill the process env structure
        process_env = process_env_structure()
        process_env.process_id = process_id
        process_env.process_dir = process_dir.val
        process_env.pit = pit
        process_env.pds = pds
        process_env.mbx = mbx
        process_env.core_function = core_function
        
        #== Create a Process object
        from vmprocess import VirtualMulticsProcess
        process = VirtualMulticsProcess(self.supervisor, process_env)
        self.__running_processes.append(process)
        print "Created", process
        
        if process_env.pit.process_type == pit_process_type_daemon:
            self.supervisor.add_daemon_process(process)
        # end if
        
        return process
        
    def destroy_process(self, process):
        declare (code = parm)
        call.set_lock_.lock(process.mbx(), 5, code)
        call.hcs_.delentry_seg(process.mbx(), code)
        call.set_lock_.unlock(process.mbx(), code)
        call.hcs_.delete_branch_(process.dir(), code)
        self.__running_processes.remove(process)
    
    def _print_error_message(self, s):
        self.supervisor.llout(s + "\n")
        self.supervisor.llout("Please contact System Administrator.\n")
    
#-- end class ProcessOverseer
    
class ProcessStack(object):
    #== Various system services can use this to store persistent data for the process.
    #== E.g., the send_message_ facility can keep track of whether or not messages are
    #== being accepted as a flag in the process stack. This information would not be
    #== accessed directly by the process object itself (it wouldn't even know about the
    #== data attributes added by system services), but used behind the scenes when
    #== the associated system service functions are called. This is better than
    #== keeping the data as resident attributes of the SystemExecutable class instances
    #== because even though it is data only those methods know or care about, the data
    #== really 'belongs' to the process, not the system service.
    
    def __init__(self, homedir):
        self.search_paths = [
            ">sss",
            ">sss>commands",
            homedir,
        ]
        self.directory_stack = []
        #== More attributes added as needed by system services...
        
    def assert_create(self, attrname, attrtype):
        if not hasattr(self, attrname):
            setattr(self, attrname, attrtype())

class ProcessMbx(object):

    def __init__(self):
        self.messages = []
        
    def __repr__(self):
        if not self.messages:
            return "<%s.%s with %d messages>" % (__name__, self.__class__.__name__, len(self.messages))
        else:
            from pprint import pformat
            s = pformat(self.messages)
            return "<%s.%s with %d messages>\n%s\n" % (__name__, self.__class__.__name__, len(self.messages), s)
        