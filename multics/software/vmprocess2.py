import datetime
from pprint import pformat

from ..globals import *

from PySide import QtCore, QtGui

class NewVirtualMulticsProcess(QtCore.QThread):

    PROCESS_TIMER_DURATION = 1.0
    
    def __init__(self, supervisor, process_env):
        super(NewVirtualMulticsProcess, self).__init__()
        self.supervisor = supervisor
        self.__process_env = process_env
        self.__known_segment_table = {}
        
        self.setObjectName(self.gid())
        
    @property
    def stack(self):
        return self.__process_env.pds.process_stack
        
    @property
    def search_paths(self):
        return self.__process_env.pds.process_stack.search_paths
        
    @search_paths.setter
    def search_paths(self, path_list):
        self.__process_env.pds.process_stack.search_paths = path_list
        
    @property
    def directory_stack(self):
        return self.__process_env.pds.process_stack.directory_stack
        
    def id(self):
        return self.__process_env.process_id
        
    def dir(self):
        return self.__process_env.process_dir
        
    def kst(self):
        return self.__known_segment_table
        
    def pds(self):
        return self.__process_env.pds
        
    def pit(self):
        return self.__process_env.pit
        
    def mbx(self):
        return self.__process_env.mbx
        
    def uid(self):
        return "%s.%s" % (self.__process_env.pit.login_name, self.__process_env.pit.project)
        
    def gid(self):
        return "%s.%s.%s" % (self.__process_env.pit.login_name, self.__process_env.pit.project, self.__process_env.pit.instance_tag)
        
    def run(self):
        self._initialize()
        
        self.exit_code = self._main_loop()
        
        # do any cleanup necessary at the VirtualMulticsProcess level
        self._cleanup()
        
    def kill(self):
        self.__process_env.core_function.kill()
        self._cleanup()
    
    @QtCore.Slot()
    def _process_mbx(self):
        if self.__process_env.mbx.messages:
            call.timer_manager_.reset_alarm_call(self.__timer_entry)
            #== Process mbx messages one per timer trigger
            with self.__process_env.mbx:
                next_message = self.__process_env.mbx.messages.pop(0)
            # end with
            self._dispatch_mbx_message(next_message)
            call.timer_manager_.alarm_call(self.PROCESS_TIMER_DURATION, self.__timer_entry)
    
    def _main_loop(self):
        self.__system_services.llout("New process for %s started on %s\n" % (self.uid(), datetime.datetime.now().ctime()))
        code = self.__process_env.core_function.start()
        return code
    
    def _on_condition__break(self):
        self.__process_env.core_function._on_condition__break()
        
    def _initialize(self):
        #== Start the MBX process timer
        self.__timer_entry = TimerEntry(self.__process_mbx)
        call.timer_manager_.alarm_call(self.PROCESS_TIMER_DURATION, self.__timer_entry)
    
    def _cleanup(self):
        #== Kill the MBX process timer
        call.timer_manager_.reset_alarm_call(self.__timer_entry)
        
    def _dispatch_mbx_message(self, mbx_message):
        print "process message found", mbx_message
        if mbx_message['type'] == "user_message":
            call.sys_.recv_message_(mbx_message)
