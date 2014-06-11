import rsa
import datetime
from pprint import pprint

from ..globals import *
from process_overseer import ProcessOverseer

from PySide import QtCore, QtGui

include.pnt
include.pdt
include.whotab
include.login_info

class AnsweringService(SystemExecutable):

    DEFAULT_CP_PATH = ">sss>default_cp"

    def __init__(self, supervisor, command_processor):
        super(AnsweringService, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        self.user_control = command_processor
        self.process_overseer = ProcessOverseer(supervisor)
        self.__person_name_table = None
        self.__project_definition_tables = {}
        self.__whotab = None
        
    def start(self):
        return self._main_loop()
        
    def kill(self):
        self._cleanup()
        
    def _main_loop(self):
        self._initialize()
        
        shutting_down = False
        while not shutting_down:
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
                
            elif self.supervisor.hardware.io.terminal_closed() and self.process_overseer.running_processes == []:
                shutting_down = True
            # end if
            
            #== See if any processes have terminated with LOGOUT or NEW_PROC exit codes
            for process in self.process_overseer.running_processes:
                user_id = process.uid()
                if process.exit_code != 0:
                    self.process_overseer.destroy_process(process)
                    
                    if process.exit_code == System.LOGOUT:
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
                        
                    elif process.exit_code == System.SHUTDOWN:
                        shutting_down = True
                    # end if
                    
                # end if
            # end for
        # end while
        
        # do any cleanup necessary at the CommandShell level
        self._cleanup()
        
        return 0
        
    def _default_home_dir(self, person_id, project_id):
        return ">".join([self.supervisor.hardware.filesystem.user_dir_dir, project_id, person_id])
        
    def _new_process(self, person_id, pdt):
        login_info.person_id = person_id
        login_info.project_id = pdt.project_id
        login_info.homedir = pdt.users[person_id].home_dir or self._default_home_dir(person_id, pdt.project_id)
        login_info.cp_path = pdt.users[person_id].cp_path or self.DEFAULT_CP_PATH
        from listener import Listener
        return self.process_overseer.create_process(login_info, Listener)
    
    def _user_login(self):
        # self.supervisor.llout("\n")
        # user_lookup = None
        # while not user_lookup:
            # user_id = ""
            # while user_id == "":
                # self.supervisor.llout("username: ")
                # user_id = self.supervisor.llin(block=True)
                # self.supervisor.llout(user_id + "\n")
            # # end while
            # self.supervisor.llout("password:\n")
            # self.supervisor.set_input_mode(QtGui.QLineEdit.Password)
            # password = self.supervisor.llin(block=True)
            # self.supervisor.set_input_mode(QtGui.QLineEdit.Normal)
            
            # user_lookup = self._authenticate(user_id, password)
        # # end while
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
        
    def _authenticate(self, user_id, password):
        login_name, _, project = user_id.partition(".")
        person_id = self.__person_name_table.person_id(login_name)
        # print "Logging in as", person_id
        try:
            encrypted_password, pubkey = self.__person_name_table.get_password(person_id)
            if (not pubkey) or (rsa.encode(password, pubkey) == encrypted_password):
                project = project or self.__person_name_table.get_default_project_id(person_id)
                pdt = self.__project_definition_tables.get(project)
                # print "Using PDT", pdt, pdt.recognizes(person_id)
                if pdt and pdt.recognizes(person_id):
                    user_id = person_id + "." + pdt.project_id
                    if user_id in self.__whotab.entries:
                        self.supervisor.llout("%s is already logged in\n\n" % (user_id))
                        return None
                    # end if
                    return (person_id, pdt)
                # end if
            # end if
        except:
            # call.dump_traceback_()
            pass
        # end try
        self.supervisor.llout("Unrecognized user id/password\n\n")
        return None
    
    def _on_condition__break(self):
        pass
        
    def _initialize(self):
        declare (process_dir = parm,
                 branch      = parm,
                 segment     = parm,
                 code        = parm)
        
        #== Get a pointer to the PNT (create it if necessary)
        call.hcs_.initiate(self.supervisor.hardware.filesystem.system_control_dir, "person_name_table", segment, code)
        self.__person_name_table = segment.ptr
        if not self.__person_name_table:
            call.hcs_.make_seg(self.supervisor.hardware.filesystem.system_control_dir, "person_name_table", segment(PersonNameTable()), code)
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
        call.hcs_.get_directory_contents(self.supervisor.hardware.filesystem.system_control_dir, branch, segment, code)
        if code.val == 0:
            segment_list = segment.list
            #== Add SysAdmin as a project with JRCooper as a recognized user
            if not any([ name.endswith(".pdt") for name in segment_list ]):
                for project_id, alias in [("SysAdmin", "sa")]:
                    segment_name = "%s.pdt" % (project_id)
                    pdt = ProjectDefinitionTable(project_id, alias, ["JRCooper"])
                    pdt.add_user("JRCooper")
                    call.hcs_.make_seg(self.supervisor.hardware.filesystem.system_control_dir, segment_name, segment(pdt), code)
                    segment_list.append(segment_name)
            # end if
            for segment_name in segment_list:
                if segment_name.endswith(".pdt"):
                    call.hcs_.initiate(self.supervisor.hardware.filesystem.system_control_dir, segment_name, segment, code)
                    self.__project_definition_tables[segment.ptr.project_id] = segment.ptr
                    self.__project_definition_tables[segment.ptr.alias] = segment.ptr
                # end if
            # end for
        # end if
        print "PROJECT DEFINITION TABLES:"
        print "--------------------------"
        pprint(self.__project_definition_tables)
        
        #== Get a pointer to the WHOTAB (create it if necessary)
        call.hcs_.initiate(self.supervisor.hardware.filesystem.system_control_dir, "whotab", segment, code)
        self.__whotab = segment.ptr
        if not self.__whotab:
            call.hcs_.make_seg(self.supervisor.hardware.filesystem.system_control_dir, "whotab", segment(WhoTable()), code)
            self.__whotab = segment.ptr
        # end if
        print "WHOTAB:"
        print "-------"
        pprint(self.__whotab)
        
    def _cleanup(self):
        pass
        
