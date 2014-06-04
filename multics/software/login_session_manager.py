import rsa
from pprint import pprint

from ..globals import *

from PySide import QtCore, QtGui

include.pnt
include.pdt

class LoginSessionManager(QtCore.QThread):

    def __init__(self, system_services):
        super(LoginSessionManager, self).__init__()
        
        self.__system_services = system_services
        self.__process_id = None
        self.__process_dir = None
        self.__whotab = None
        self.__project_definition_tables = {}
        self.__person_name_table = None
        self.__session = None
        
    @property
    def session(self):
        return self.__session
        
    @property
    def whotab(self):
        return self.__whotab
        
    @property
    def pdt(self):
        return self.__project_definition_tables
        
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
        
    def run(self):
        declare (code = parm)
        
        self._initialize()
        self._main_loop()
        
        # do any cleanup necessary at the LoginSessionManager level in response to a clean SHUTDOWN
        call.hcs_.delete_branch_(self.__process_dir, code)
        self.__session = None
        
        self.__system_services.shutdown()
        
    def kill(self):
        if self.__session:
            self._remove_user_from_whotab(self.__session.user_id)
            self.__session.kill()
        # end if
    
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
        call.hcs_.initiate(self.__system_services.hardware.filesystem.system_control_dir, "person_name_table", segment)
        self.__person_name_table = segment.ptr
        if not self.__person_name_table:
            call.hcs_.make_seg(self.__system_services.hardware.filesystem.system_control_dir, "person_name_table", segment(PersonNameTable()), code)
            self.__person_name_table = segment.ptr
            #== Add JRCooper/jrc as a valid user to start with
            with self.__person_name_table:
                self.__person_name_table.add_person("JRCooper", alias="jrc", default_project_id="SysAdmin")
            # end with
        # end if
        print "PERSON NAME TABLE:"
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
                    call.hcs_.make_seg(self.__system_services.hardware.filesystem.system_control_dir, segment_name, segment(pdt), code)
                    segment_list.append(segment_name)
            # end if
            for segment_name in segment_list:
                if segment_name.endswith(".pdt"):
                    call.hcs_.initiate(self.__system_services.hardware.filesystem.system_control_dir, segment_name, segment)
                    self.__project_definition_tables[segment.ptr.project_id] = segment.ptr
                    self.__project_definition_tables[segment.ptr.alias] = segment.ptr
                # end if
            # end for
        # end if
        print "PROJECT DEFINITION TABLES:"
        pprint(self.__project_definition_tables)
        
        #== Get a pointer to the WHOTAB (create it if necessary)
        call.hcs_.initiate(self.__system_services.hardware.filesystem.system_control_dir, "whotab", segment)
        self.__whotab = segment.ptr
        if not self.__whotab:
            call.hcs_.make_seg(self.__system_services.hardware.filesystem.system_control_dir, "whotab", segment(LoginDatabase()), code)
            self.__whotab = segment.ptr
        # end if
        print "WHOTAB:"
        pprint(self.__whotab)
    
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
            self._add_user_to_whotab(self.__session.user_id, self.__session.login_time)
            
            code = self.__session.start()
            
            self._remove_user_from_whotab(self.__session.user_id)
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
                    user_id = person_id + "." + pdt.project_id
                    from login_session import LoginSession
                    return LoginSession(self.__system_services, self, user_id)
                # end if
            # end if
        except:
            # traceback_print_exc()
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

    def __init__(self, login_time):
        super(LoginSessionBlock, self).__init__()
        
        self.login_time = login_time
        self.process_id = None
        self.process_dir = None
        
    def __repr__(self):
        return "<%s.%s login_time: %s, process_id: %s, process_dir: %s>" % (__name__, self.__class__.__name__, self.login_time.ctime() if self.login_time else None, self.process_id, self.process_dir)
