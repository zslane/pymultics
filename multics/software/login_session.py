import datetime

from ..globals import *

from PySide import QtCore, QtGui

class LoginSession(QtCore.QObject):

    def __init__(self, system_services, login_session_manager, user_id, cp_path):
        super(LoginSession, self).__init__()
        
        self.__system_services = system_services
        self.__login_session_manager = login_session_manager
        self.__session_datetime = datetime.datetime.now()
        self.__user_id = user_id
        self.__homedir = None
        self.__process = None
        self.__cp_path = cp_path
        
    @property
    def process(self):
        return self.__process
        
    @property
    def login_time(self):
        return self.__session_datetime
        
    @property
    def user_id(self):
        return self.__user_id
        
    @property
    def person_id(self):
        return self.__user_id.split(".")[0]
        
    @property
    def project_id(self):
        return self.__user_id.split(".")[1]
        
    @property
    def homedir(self):
        #== Get this from the user account database instead someday
        return "%s>%s>%s" % (self.__system_services.hardware.filesystem.user_dir_dir, self.project_id, self.person_id)
        
    def start(self):
        self.__system_services.llout("\n%s logged in on %s\n" % (self.__user_id, self.__session_datetime.ctime()))
        return self._main_loop()
        
    def kill(self):
        if self.__process:
            self.__process.kill()
        # end if
        self._cleanup()
        
    def register_process(self, process_id, process_dir):
        self.__login_session_manager.register_process(self.__user_id, process_id, process_dir)
        
    def _main_loop(self):
        declare (command = parm)
        
        code = 0
        while code != System.LOGOUT and code != System.SHUTDOWN:
            call.hcs_.get_entry_point(self.__cp_path, command)
            if command.processor == null():
                self.__system_services.llout("Could not find/run command processor %s. Logging out.\n" % (self.__cp_path))
                code = System.LOGOUT
            elif not self.__system_services.hardware.filesystem.file_exists(self.homedir):
                self.__system_services.llout("No home directory for user. Please contact System Administrator. Logging out.\n")
                code = System.LOGOUT
            else:
                from vmprocess import VirtualMulticsProcess
                self.__process = VirtualMulticsProcess(self.__system_services, self, command.processor)
                code = self.__process.start()
            # end if
        # end while
        
        # do any cleanup necessary at the LoginSession level
        self._cleanup()
        
        self.__system_services.llout("%s logged out on %s\n" % (self.__user_id, datetime.datetime.now().ctime()))
        return code
    
    def _on_condition__break(self):
        if self.__process:
            self.__process._on_condition__break()
        
    def _cleanup(self):
        self.__process = None
        