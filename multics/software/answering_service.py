import shutil
import datetime
from pprint import pprint

from ..globals import *

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
        from process_overseer import ProcessOverseer
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
            try:
                #== See if any terminals are trying to log in
                if (not self.supervisor.hardware.io.attached_tty_process() and
                    self.supervisor.hardware.io.linefeed_received()):
                    self.supervisor.hardware.io.flush_input()
                    process = self._user_login()
                    if process:
                        print "Attaching tty to process", process.id(), process.objectName()
                        self.supervisor.hardware.io.attach_tty_process(process.id())
                        print "Starting process", process.objectName()
                        process.start()
                    # end if
                    
                # elif self.supervisor.hardware.io.terminal_closed():
                    # shutting_down = True
                    
                # elif self.supervisor.shutting_down():
                    # shutting_down = True
                    
                else:
                    # QtCore.QCoreApplication.processEvents()
                    check_conditions_(ignore_break_signal=True)
                # end if
            
            except DisconnectCondition:
                shutting_down = True
            # end try
            
            except ShutdownCondition:
                shutting_down = True
            # end try
            
            #== See if any processes have terminated with LOGOUT or NEW_PROC exit codes
            for process in self.process_overseer.running_processes:
                if process.exit_code != 0:
                    if process.exit_code == System.LOGOUT:
                        self._user_logout(process)
                        
                    elif process.exit_code == System.NEW_PROCESS:
                        self._user_new_proc(process)
                    # end if
                # end if
            # end for
            
        # end while
        
        self._cleanup()
        
        return 0
        
    def _default_home_dir(self, person_id, project_id):
        return ">".join([self.supervisor.hardware.filesystem.user_dir_dir, project_id, person_id])
        
    def _new_process(self, person_id, pdt, login_options={}):
        # pprint(login_options)
        login_info.person_id    = person_id
        login_info.project_id   = pdt.project_id
        login_info.process_type = pit_process_type_interactive
        login_info.homedir      = login_options.get('home_dir') or pdt.users[person_id].home_dir or self._default_home_dir(person_id, pdt.project_id)
        login_info.cp_path      = pdt.users[person_id].cp_path or self.DEFAULT_CP_PATH
        login_info.no_start_up  = login_options.get('no_start_up', False)
        from listener import Listener
        return self.process_overseer.create_process(login_info, Listener)
    
    def _user_login(self):
        login_options = self.user_control.login_ui(self.supervisor,
                                                   self.__person_name_table,
                                                   self.__project_definition_tables,
                                                   self.__whotab)
        
        login_info.time_login = datetime.datetime.now()
        
        process = self._new_process(login_options['person_id'], login_options['pdt'], login_options)
        if process:
            #== Add the user to the whotab
            with self.__whotab:
                self.__whotab.entries[login_info.user_id] = WhotabEntry(login_info.time_login, process.id(), process.dir())
            # end with
            
            self.supervisor.llout("\n%s logged in on %s\n" % (login_info.user_id, login_info.time_login.ctime()))
        # end if
        
        return process
        
    def _user_logout(self, process):
        user_id = process.uid()
        self.supervisor.hardware.io.detach_tty_process(process.id())
        self.process_overseer.destroy_process(process)
        
        self.supervisor.llout("%s logged out on %s\n" % (user_id, datetime.datetime.now().ctime()))
        print "%s logged out on %s" % (user_id, datetime.datetime.now().ctime())
        
        #== Remove the entry in the whotab corresponding to this user
        with self.__whotab:
            del self.__whotab.entries[user_id]
        # end with
        pprint(self.__whotab)
        
    def _user_new_proc(self, process):
        user_id = process.uid()
        pit = process.pit()
        person_id, _, project_id = user_id.partition(".")
        pdt = self.__project_definition_tables.get(project_id)
        login_options = {
            'person_id': person_id,
            'project_id': project_id,
            'pdt': pdt,
            'home_dir': pit.homedir,
            'no_start_up': pit.no_start_up,
        }
        login_options.update(process.stack.new_proc_options)
        
        self.supervisor.hardware.io.detach_tty_process(process.id())
        self.process_overseer.destroy_process(process)
        
        process = self._new_process(person_id, pdt, login_options)
        if process:
            print "Starting new process", process.objectName()
            process.start()
            #== Update the entry in the whotab corresponding to this user
            with self.__whotab:
                self.__whotab.entries[user_id].process_id = process.id()
                self.__whotab.entries[user_id].process_dir = process.dir()
            # end with
            pprint(self.__whotab)
            print "Attaching tty to process", process.id(), process.objectName()
            self.supervisor.hardware.io.attach_tty_process(process.id())
        else:
            self.supervisor.llout("Error creating process!")
        # end if
    
    def _on_condition__break(self):
        pass
        
    def _initialize(self):
        self.__person_name_table = self.supervisor.pnt
        self.__project_definition_tables = self.supervisor.pdt
        self.__whotab = self.supervisor.whotab
        msg_handlers = {
            'upload_pmf_request': self._upload_pmf_request_handler,
        }
        self.__process.register_msg_handlers(msg_handlers)
        
    def _cleanup(self):
        pass
        
    def _upload_pmf_request_handler(self, message):
        declare (pdt  = parm,
                 code = parm)
                 
        pdt_file = message['src_file']
        src_dir = message['src_dir']
        dst_dir = self.supervisor.fs.system_control_dir
        src_pdt_path = system.fs.path2path(src_dir, pdt_file)
        dst_pdt_path = system.fs.path2path(dst_dir, pdt_file)
        shutil.move(src_pdt_path, dst_pdt_path)
        
        #== Create user home directories if necessary
        call.hcs_.initiate(dst_dir, pdt_file, pdt, code)
        if pdt.ptr != null():
            for user_config in pdt.ptr.users.values():
                homedir = user_config.home_dir or self._default_home_dir(user_config.person_id, pdt.ptr.project_id)
                if not self.supervisor.fs.file_exists(homedir):
                    self._create_new_home_dir(user_config.person_id, pdt.ptr.project_id, homedir)
                    
    def _create_new_home_dir(self, person_id, project_id, homedir):
        declare (segment = parm,
                 code    = parm)
        
        code.val = self.supervisor.fs.mkdir(homedir)
        if code.val == 0:
            call.hcs_.make_seg(homedir, person_id + ".mbx", segment(dict), code)
            