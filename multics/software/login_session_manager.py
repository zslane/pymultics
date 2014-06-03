import rsa
from pprint import pprint

from ..globals import *

from PySide import QtCore, QtGui

declare (hcs_ = entry . returns (varying))

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
        self._initialize()
        self._main_loop()
        
        # do any cleanup necessary at the LoginSessionManager level in response to a clean SHUTDOWN
        call.hcs_.delete_branch_(self.__process_dir)
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
        pprint(self.__person_name_table)
        
        #== Make a dictionary of PDTs (project definition tables)
        call.hcs_.get_directory_contents(self.__system_services.hardware.filesystem.system_control_dir, branch, segment, code)
        if code.val == 0:
            segment_list = segment.list
            #== Add SysAdmin as a project with JRCooper as a recognized user
            if not any([ name.endswith(".pdt") for name in segment_list ]):
                for project_id, alias in [("SysAdmin", "sa"), ("Multics", "m")]:
                    segment_name = "%s.pdt" % (project_id)
                    pdt = ProjectDefinitionTable(project_id, alias)
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
        pprint(self.__project_definition_tables)
        
        #== Get a pointer to the WHOTAB (create it if necessary)
        call.hcs_.initiate(self.__system_services.hardware.filesystem.system_control_dir, "whotab", segment)
        self.__whotab = segment.ptr
        if not self.__whotab:
            call.hcs_.make_seg(self.__system_services.hardware.filesystem.system_control_dir, "whotab", segment(LoginDatabase()), code)
            self.__whotab = segment.ptr
        # end if
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
            if rsa.encode(password, pubkey) == encrypted_password:
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
        
class PersonNameTable(object):

    def __init__(self):
        self.name_entries = {}
        self.aliases = {}
        
    def person_id_list(self):
        return self.name_entries.keys()
        
    def alias_list(self):
        return self.aliases.keys()
        
    def add_person(self, person_id, alias="", default_project_id="*", encrypted_password="", pubkey=None):
        person_name_entry = PersonNameEntry(person_id, alias, default_project_id, encrypted_password, pubkey)
        self.name_entries[person_name_entry.person_id] = person_name_entry
        if person_name_entry.alias:
            self.aliases[person_name_entry.alias] = person_name_entry.person_id
        
    def person_id(self, name):
        name_entry = self.name_entries.get(name)
        return (name_entry and name_entry.person_id) or self.resolve_alias(name)
        
    def resolve_alias(self, name):
        return self.aliases.get(name, "")
        
    def get_default_project_id(self, name):
        try:
            name = self.resolve_alias(name) or name
            return self.name_entries[name].default_project_id
        except:
            raise MulticsCondition(error_table_no_such_user)
            
    def set_default_project_id(self, name, default_project_id):
        try:
            name = self.resolve_alias(name) or name
            self.name_entries[name].default_project_id = default_project_id
        except:
            raise MulticsCondition(error_table_no_such_user)
        
    def get_password(self, name):
        try:
            name = self.resolve_alias(name) or name
            return (self.name_entries[name].encrypted_password, self.name_entries[name].password_pubkey)
        except:
            raise MulticsCondition(error_table_.no_such_user)
            
    def set_password(self, name, encrypted_password):
        try:
            name = self.resolve_alias(name) or name
            self.name_entries[name].encrypted_password = encrypted_password
        except:
            raise MulticsCondition(error_table_no_such_user)
        
    def __repr__(self):
        return str(self.name_entries) + "\n" + str(self.aliases)
    
class PersonNameEntry(object):

    def __init__(self, person_id, alias="", default_project_id="", encrypted_password="", pubkey=None):
        self.person_id = person_id
        self.alias = alias
        self.default_project_id = default_project_id
        self.encrypted_password = encrypted_password
        self.password_pubkey = pubkey or rsa.keygen(2 ** 128)[0]
        
    def __repr__(self):
        person_id = self.person_id
        if self.alias:
            person_id += " (%s)" % (self.alias)
        default_project_id = self.default_project_id or "None"
        return "<%s.%s person_id: %s, default_project_id: %s>" % (__name__, self.__class__.__name__, person_id, default_project_id)
        
class ProjectDefinitionTable(object):

    def __init__(self, project_id, alias=""):
        self.project_id = project_id
        self.alias = alias
        self.users = {}
        
    def recognizes(self, person_id):
        return person_id in self.users
        
    def get_user_quota(self, person_id):
        try:
            return self.users[person_id]
        except:
            raise MulticsCondition(error_table_.no_such_user)
            
    def add_user(self, person_id):
        self.users[person_id] = ProjectUserQuota(person_id)
        
    def remove_user(self, person_id):
        try:
            del self.users[person_id]
        except:
            raise MulticsCondition(error_table_.no_such_user)        
        
    def __repr__(self):
        project_id = self.project_id
        if self.alias:
            project_id += " (%s)" % (self.alias)
        users = str(self.users.keys())
        return "<%s.%s project_id: %s, users = %s>" % (__name__, self.__class__.__name__, project_id, users)
        
class ProjectUserQuota(object):

    def __init__(self, person_id):
        self.person_id = person_id
        