import datetime

from ..globals import *

from PySide import QtCore, QtGui

class LoginSession(QtCore.QObject):

    def __init__(self, system_services, login_session_manager, cp_path, pit):
        super(LoginSession, self).__init__()
        
        self.__system_services = system_services
        self.__login_session_manager = login_session_manager
        self.__homedir = None
        self.__process = None
        self.__cp_path = cp_path
        self.__command_processor = None
        self.__pit = pit
        
    @property
    def process(self):
        return self.__process
        
    def start(self):
        declare (command = parm)
        call.hcs_.get_entry_point(self.__cp_path, command)
        if command.processor == null():
            self.__system_services.llout("Could not find command processor %s. Please contact System Administrator.\n" % (self.__cp_path))
            return System.LOGOUT
        elif not self.__system_services.hardware.filesystem.file_exists(self.__pit.homedir):
            self.__system_services.llout("No home directory for user. Please contact System Administrator.\n")
            return System.LOGOUT
        else:
            self.__command_processor = command.processor
            self.__pit.time_login = datetime.datetime.now()
            self.__login_session_manager._add_user_to_whotab(self.__pit.user_id, self.__pit.time_login)
            self.__system_services.llout("\n%s logged in on %s\n" % (self.__pit.user_id, self.__pit.time_login.ctime()))
            return self._main_loop()
        
    def kill(self):
        if self.__process:
            self.__process.kill()
        # end if
        self._cleanup()
        
    def register_process(self, process_id, process_dir):
        self.__login_session_manager.register_process(self.__pit.user_id, process_id, process_dir)
        
    def _main_loop(self):
        print self.__pit
        code = 0
        while code != System.LOGOUT and code != System.SHUTDOWN:
            from listener import Listener
            core_function = Listener(self.__system_services, self.__command_processor)
            
            from vmprocess0 import OldVirtualMulticsProcess
            self.__process = OldVirtualMulticsProcess(self.__system_services, self, core_function, self.__pit)
            
            code = self.__process.start()
        # end while
        
        # do any cleanup necessary at the LoginSession level
        self._cleanup()
        
        self.__system_services.llout("%s logged out on %s\n" % (self.__pit.user_id, datetime.datetime.now().ctime()))
        return code
    
    def _on_condition__break(self):
        if self.__process:
            self.__process._on_condition__break()
        
    def _cleanup(self):
        self.__process = None
        