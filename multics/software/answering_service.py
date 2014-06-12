import rsa
import datetime
from pprint import pprint

from ..globals import *
from process_overseer import ProcessOverseer

from PySide import QtCore, QtGui

include.pnt
include.pdt
include.whotab
include.pit
include.login_info

class AnsweringService(SystemExecutable):

    DEFAULT_CP_PATH = ">sss>default_cp"

    def __init__(self, supervisor, command_processor):
        super(AnsweringService, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        self.user_control = command_processor
        self.user_control.setParent(self)
        self.process_overseer = ProcessOverseer(supervisor)
        self.__process = None
        self.__person_name_table = None
        self.__project_definition_tables = {}
        self.__whotab = None
        self.exit_code = 0
        
    def start(self, owning_process):
        self.__process = owning_process
        return self._main_loop()
        
    def kill(self):
        self._cleanup()
        
    def _main_loop(self):
        self._initialize()
        
        shutting_down = False
        while not (shutting_down and self.process_overseer.running_processes == []):
            #== See if any terminals are trying to log in
            if (not self.supervisor.hardware.io.attached_tty_process() and
                self.supervisor.hardware.io.linefeed_received()):
                try:
                    process = self._user_login()
                    if process:
                        print "Attaching tty to process", process.id(), process.objectName()
                        self.supervisor.hardware.io.attach_tty_process(process.id())
                        print "Starting process", process.objectName()
                        process.start()
                    # end if
                    
                except BreakCondition:
                    self.__system_services.set_input_mode(QtGui.QLineEdit.Normal)
                    call.hcs_.signal_break()
                
                except DisconnectCondition:
                    shutting_down = True
                # end try
                
            elif self.supervisor.hardware.io.terminal_closed():
                shutting_down = True
            # end if
            
            #== See if any processes have terminated with LOGOUT or NEW_PROC exit codes
            for process in self.process_overseer.running_processes:
                user_id = process.uid()
                if process.exit_code != 0:
                    self.process_overseer.destroy_process(process)
                    
                    if process.exit_code == System.LOGOUT or process.exit_code == System.SHUTDOWN:
                        self.supervisor.llout("%s logged out on %s\n" % (user_id, datetime.datetime.now().ctime()))
                        print "%s logged out on %s" % (user_id, datetime.datetime.now().ctime())
                        #== Remove the session block in the LOGIN DB corresponding to this session
                        with self.__whotab:
                            del self.__whotab.entries[user_id]
                        # end with
                        pprint(self.__whotab)
                        self.supervisor.hardware.io.detach_tty_process(process.id())
                        
                    elif process.exit_code == System.NEW_PROCESS:
                        person_id, _, project_id = user_id
                        pdt = self.__project_definition_tables.get(project_id)
                        process = self._new_process(person_id, pdt)
                        if process:
                            process.start()
                        else:
                            self.supervisor.llout("Error creating process!")
                        # end if
                        
                    if process.exit_code == System.SHUTDOWN:
                        self.supervisor.shutdown()
                        shutting_down = True
                    # end if
                    
                # end if
            # end for
        # end while
        
        # do any cleanup necessary at the CommandShell level
        self._cleanup()
        
        # self.supervisor.shutdown()
        
        return 0
        
    def _default_home_dir(self, person_id, project_id):
        return ">".join([self.supervisor.hardware.filesystem.user_dir_dir, project_id, person_id])
        
    def _new_process(self, person_id, pdt):
        login_info.person_id = person_id
        login_info.project_id = pdt.project_id
        login_info.process_type = pit_process_type_interactive
        login_info.homedir = pdt.users[person_id].home_dir or self._default_home_dir(person_id, pdt.project_id)
        login_info.cp_path = pdt.users[person_id].cp_path or self.DEFAULT_CP_PATH
        from listener import Listener
        return self.process_overseer.create_process(login_info, Listener)
    
    def _user_login(self):
        user_lookup = self.user_control.do_login(self.supervisor,
                                                 self.__person_name_table,
                                                 self.__project_definition_tables,
                                                 self.__whotab)
        
        login_info.time_login = datetime.datetime.now()
        
        person_id, pdt = user_lookup
        process = self._new_process(person_id, pdt)
        
        if process:
            #== Add the user to the whotab
            with self.__whotab:
                self.__whotab.entries[login_info.user_id] = WhotabEntry(login_info.time_login, process.id(), process.dir())
            # end with
            
            self.supervisor.llout("\n%s logged in on %s\n" % (login_info.user_id, login_info.time_login.ctime()))
        # end if
        
        return process
        
    def _on_condition__break(self):
        pass
        
    def _initialize(self):
        self.__person_name_table = self.supervisor.pnt
        self.__project_definition_tables = self.supervisor.pdt
        self.__whotab = self.supervisor.whotab
        
    def _cleanup(self):
        pass
        
