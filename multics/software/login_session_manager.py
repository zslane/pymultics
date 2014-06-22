import rsa
from pprint import pprint

from ..globals import *

from PySide import QtCore, QtGui

include.pnt
include.pdt
include.pit

class LoginSessionManager(QtCore.QThread):

    DEFAULT_CP_PATH = ">sss>default_cp"
    
    def __init__(self, system_services):
        super(LoginSessionManager, self).__init__()
        self.setObjectName("Initializer.SysDaemon")
        
        self.__system_services = system_services
        self.__process_id = None
        self.__process_dir = None
        self.__whotab = None
        self.__project_definition_tables = {}
        self.__person_name_table = None
        self.__session = None
        self.__known_segment_table = {}
            
    @property
    def session(self):
        return self.__session
        
    @property
    def whotab(self):
        return self.__whotab
        
    @property
    def pdt(self):
        return self.__project_definition_tables
        
    @property
    def stack(self):
        return self.session.process.stack
        
    @property
    def search_paths(self):
        return self.session.process.search_paths
        
    @search_paths.setter
    def search_paths(self, path_list):
        self.session.process.search_paths = path_list
        
    @property
    def directory_stack(self):
        return self.session.process.directory_stack
        
    def id(self):
        return self.session.process.id()
        
    def dir(self):
        return self.session.process.dir()
        
    def pds(self):
        return self.session.process.pds()
        
    def pit(self):
        return self.session.process.pit()
        
    def mbx(self):
        return self.session.process.mbx()
        
    def uid(self):
        return self.session.process.uid()
        
    def gid(self):
        return self.session.process.gid()
        
    #== kst() would be a Process method, and LoginSessionManager becomes the Initializer process.
    #== clear_kst() would not be necessary as the KST would just disappear when the process ends.
    def kst(self):
        return self.__known_segment_table
    def clear_kst(self):
        self.__known_segment_table = {}
        
    def _add_user_to_whotab(self, user_id, login_time):
        #== Add a session block to the LOGIN DB for this session
        with self.__whotab:
            self.__whotab.session_blocks[user_id] = LoginSessionBlock(login_time)
        # end with
        pprint(self.__whotab)
        
    def _remove_user_from_whotab(self, user_id):
        #== Remove the session block in the LOGIN DB corresponding to this session
        with self.__whotab:
            del self.__whotab.session_blocks[user_id]
        # end with
        pprint(self.__whotab)
        
    def _default_home_dir(self, person_id, project_id):
        return ">".join([self.__system_services.hardware.filesystem.user_dir_dir, project_id, person_id])
        
    def start_message_daemon(self):
        self.__message_daemon = MessageDaemon(self.__system_services)
        self.__message_daemon.start()
        
    def kill_message_daemon(self):
        if self.__message_daemon:
            self.__message_daemon.kill()
            while self.__message_daemon.isRunning():
                QtCore.QThread.msleep(1000)
            self.__message_daemon = None
    
    def run(self):
        declare (code = parm)
        
        self._initialize()
        self._main_loop()
        
        # do any cleanup necessary at the LoginSessionManager level in response to a clean SHUTDOWN
        call.hcs_.delete_branch_(self.__process_dir, code)
        
        self.__system_services.shutdown()
        
    def kill(self):
        # self.kill_message_daemon()
        pass
    
    def register_process(self, user_id, process_id, process_dir):
        with self.__whotab:
            self.__whotab.session_blocks[user_id].process_id = process_id
            self.__whotab.session_blocks[user_id].process_dir = process_dir
        # end with
        pprint(self.__whotab)
    
    def _initialize(self):
        declare (process_dir = parm,
                 branch      = parm,
                 segment     = parm,
                 code        = parm)
                
        self.__process_id = 0o777777000000
        call.hcs_.create_process_dir(self.__process_id, process_dir, code)
        self.__process_dir = process_dir.name
        
        #== Get a pointer to the PNT (create it if necessary)
        call.hcs_.initiate(self.__system_services.hardware.filesystem.system_control_dir, "person_name_table", segment, code)
        self.__person_name_table = segment.ptr
        if not self.__person_name_table:
            call.hcs_.make_seg(self.__system_services.hardware.filesystem.system_control_dir, "person_name_table", "", 0, segment(PersonNameTable()), code)
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
        call.hcs_.get_directory_contents(self.__system_services.hardware.filesystem.system_control_dir, branch, segment, code)
        if code.val == 0:
            segment_list = segment.list
            #== Add SysAdmin as a project with JRCooper as a recognized user
            if not any([ name.endswith(".pdt") for name in segment_list ]):
                for project_id, alias in [("SysAdmin", "sa")]:
                    segment_name = "%s.pdt" % (project_id)
                    pdt = ProjectDefinitionTable(project_id, alias, ["JRCooper"])
                    pdt.add_user("JRCooper")
                    call.hcs_.make_seg(self.__system_services.hardware.filesystem.system_control_dir, segment_name, "", 0, segment(pdt), code)
                    segment_list.append(segment_name)
            # end if
            for segment_name in segment_list:
                if segment_name.endswith(".pdt"):
                    call.hcs_.initiate(self.__system_services.hardware.filesystem.system_control_dir, segment_name, segment, code)
                    self.__project_definition_tables[segment.ptr.project_id] = segment.ptr
                    self.__project_definition_tables[segment.ptr.alias] = segment.ptr
                # end if
            # end for
        # end if
        print "PROJECT DEFINITION TABLES:"
        print "--------------------------"
        pprint(self.__project_definition_tables)
        
        #== Get a pointer to the WHOTAB (create it if necessary)
        call.hcs_.initiate(self.__system_services.hardware.filesystem.system_control_dir, "whotab", "", 0, 0, segment, code)
        self.__whotab = segment.ptr
        if not self.__whotab:
            call.hcs_.make_seg(self.__system_services.hardware.filesystem.system_control_dir, "whotab", "", 0, segment(LoginDatabase()), code)
            self.__whotab = segment.ptr
        # end if
        print "WHOTAB:"
        print "-------"
        pprint(self.__whotab)
        
        # self.start_message_daemon()
    
    def _main_loop(self):
        LISTEN = 0
        PROMPT = 1
        state = LISTEN
        while state != System.SHUTDOWN:
            if state == LISTEN:
                self.__system_services.wait_for_linefeed()
                self.__system_services.llout("\n")
                state = PROMPT
            # end if
            
            try:
                state = self._user_login()
                
            except BreakCondition:
                self.__system_services.set_input_mode(QtGui.QLineEdit.Normal)
                call.hcs_.signal_break()
            # end try
            
            if state == System.LOGOUT:
                state = LISTEN
        # end while
        
    def _user_login(self):
        user_id = ""
        while user_id == "":
            self.__system_services.llout("username: ")
            user_id = self.__system_services.llin(block=True)
            self.__system_services.llout(user_id + "\n")
        # end while
        self.__system_services.llout("password:\n")
        self.__system_services.set_input_mode(QtGui.QLineEdit.Password)
        password = self.__system_services.llin(block=True)
        self.__system_services.set_input_mode(QtGui.QLineEdit.Normal)
        
        self.__session = self._authenticate(user_id, password)
        if self.__session:
            # self._add_user_to_whotab(pit.user_id, pit.time_login) # <-- called in LoginSession.start() now
            
            code = self.__session.start()
            
            self._remove_user_from_whotab(pit.user_id)
            self.__session = None
        else:
            code = System.INVALID_LOGIN
        return code
    
    def _authenticate(self, user_id, password):
        pers, _, proj = user_id.partition(".")
        person_id = self.__person_name_table.person_id(pers)
        try:
            encrypted_password, pubkey = self.__person_name_table.get_password(person_id)
            if (not pubkey) or (rsa.encode(password, pubkey) == encrypted_password):
                proj = proj or self.__person_name_table.get_default_project_id(person_id)
                pdt = self.__project_definition_tables.get(proj)
                if pdt and pdt.recognizes(person_id):
                    if (person_id + "." + pdt.project_id) in self.__whotab.session_blocks:
                        self.__system_services.llout("%s is already logged in\n\n" % (person_id + "." + pdt.project_id))
                        return None
                    # end if
                    pit.login_name = person_id
                    pit.project = pdt.project_id
                    pit.homedir = pdt.users[person_id].home_dir or self._default_home_dir(person_id, pdt.project_id)
                    cp_path = pdt.users[person_id].cp_path or self.DEFAULT_CP_PATH
                    from login_session import LoginSession
                    return LoginSession(self.__system_services, self, cp_path, pit)
                # end if
            # end if
        except:
            # call.dump_traceback_()
            pass
        # end try
        self.__system_services.llout("Unrecognized user id/password\n\n")
        return None
    
    def _on_condition__break(self):
        if self.__session:
            self.__session._on_condition__break()
        
class LoginDatabase(object):

    def __init__(self):
        self.session_blocks = {}
        
    def __repr__(self):
        return str(self.session_blocks)
        
    def get_process_ids(self):
        return [ session_block.process_id for session_block in self.session_blocks.values() ]
        
class LoginSessionBlock(object):

    def __init__(self, login_time, process_id=None, process_dir=None):
        super(LoginSessionBlock, self).__init__()
        
        self.login_time = login_time
        self.process_id = process_id
        self.process_dir = process_dir
        
    def __repr__(self):
        return "<%s.%s login_time: %s, process_id: %s, process_dir: %s>" % (__name__, self.__class__.__name__, self.login_time.ctime() if self.login_time else None, self.process_id, self.process_dir)

class MessageDaemon(QtCore.QThread):

    def __init__(self, system_services):
        super(MessageDaemon, self).__init__()
        self.setObjectName("Message.SysDaemon")
        
        self.__system_services = system_services
        
    def kill(self):
        self.__process_id = 0
        
    def run(self):
        declare (process_dir  = parm,
                 clock_       = entry . returns (fixed.bin(32)),
                 code         = parm)
        
        self.__process_id = clock_()
        call.hcs_.create_process_dir(self.__process_id, process_dir, code)
        if code.val != 0:
            self.__system_services.llout("Failed to create message daemon process directory.\n")
            self.__process_id = 0
        else:
            self.__process_dir = process_dir.name
        
        count = 0
        while self.__process_id:
            QtCore.QThread.msleep(2000)
            self.__system_services.llout("Message.SysDaemon.z alive\n")
            # count += 1
            if count == 10:
                break
            # end if
        # end while
        call.hcs_.delete_branch_(self.__process_dir, code)
