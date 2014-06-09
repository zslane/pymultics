import datetime
from pprint import pformat

from ..globals import *

from PySide import QtCore, QtGui

declare (clock_ = entry . returns (fixed.bin(32)))

class VirtualMulticsProcess(QtCore.QObject):

    PROCESS_TIMER_DURATION = 1.0
    
    def __init__(self, system_services, login_session, core_function, pit):
        super(VirtualMulticsProcess, self).__init__()
        
        self.__system_services = system_services
        self.__login_session = login_session
        self.__core_function = core_function
        self.__pit = pit
        self.__process_id = None
        self.__process_dir = None
        self.__mbx = None
        self.__process_stack = ProcessStack()
        
    @property
    def process_id(self):
        return self.__process_id
        
    @property
    def process_dir(self):
        return self.__process_dir
        
    @property
    def stack(self):
        return self.__process_stack
        
    @property
    def search_paths(self):
        return self.__process_stack.search_paths
        
    @search_paths.setter
    def search_paths(self, path_list):
        self.__process_stack.search_paths = path_list
        
    @property
    def directory_stack(self):
        return self.__process_stack.directory_stack
        
    def start(self):
        declare (process_dir  = parm,
                 data         = parm,
                 code         = parm,
                 search_paths = parm)
                 
        self.__process_id = clock_()
        call.hcs_.create_process_dir(self.__process_id, process_dir, code)
        if code.val != 0:
            self.__system_services.llout("Failed to create process directory. Logging out.\n")
            return System.LOGOUT
        # end if
        self.__process_dir = process_dir.name
        self.__pit.process_id = self.__process_id
        call.hcs_.make_seg(self.__process_dir, "pit", data(self.__pit), code)
        if code.val != 0:
            self.__system_services.llout("Failed to create process initialization table. Logging out.\n")
            return System.LOGOUT
        # end if
        
        self._create_mbx()
        self.__login_session.register_process(self.__process_id, self.__process_dir)
        call.sys_.get_default_search_paths(search_paths)
        self.__process_stack.search_paths = search_paths.list
        
        #== Start the MBX process timer
        call.timer_manager_.alarm_call(self.PROCESS_TIMER_DURATION, self._process_mbx)
        
        return self._main_loop()
        
    def kill(self):
        if self.__core_function:
            self.__core_function.kill()
        # end if
        self._cleanup()
    
    def _create_mbx(self):
        declare (segment = parm . init (ProcessMbx()))
        call.hcs_.make_seg(self.__process_dir, "process_mbx", segment, code)
        self.__mbx = segment.ptr
        print self.__mbx
        
    def _delete_mbx(self):
        declare (code = parm)
        call.hcs_.delentry_seg(self.__mbx, code)
        
    @QtCore.Slot()
    def _process_mbx(self):
        if self.__mbx.messages:
            call.timer_manager_.reset_alarm_call(self._process_mbx)
            #== Process mbx messages one per timer trigger
            with self.__mbx:
                next_message = self.__mbx.messages.pop(0)
            # end with
            self._dispatch_mbx_message(next_message)
            call.timer_manager_.alarm_call(self.PROCESS_TIMER_DURATION, self._process_mbx)
    
    def _main_loop(self):
        self.__system_services.llout("New process started on %s\n" % (datetime.datetime.now().ctime()))
        code = self.__core_function.start()
        
        # do any cleanup necessary at the VirtualMulticsProcess level
        self._cleanup()
        
        return code
    
    def _on_condition__break(self):
        if self.__core_function:
            self.__core_function._on_condition__break()
        
    def _cleanup(self):
        declare (code = parm)
        self.__core_function = None
        call.timer_manager_.reset_alarm_call(self._process_mbx)
        self._delete_mbx()
        call.hcs_.delete_branch_(self.__process_dir, code)
        call.hcs_.clear_kst()
        
    def _dispatch_mbx_message(self, mbx_message):
        print "process message found", mbx_message
        if mbx_message['type'] == "user_message":
            call.sys_.recv_message_(mbx_message)
    
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
    
    def __init__(self):
        self.search_paths = []
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
            s = pformat(self.messages)
            return "<%s.%s with %d messages>\n%s" % (__name__, self.__class__.__name__, len(self.messages), s)
        