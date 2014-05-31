from pprint import pprint

from ..globals import *

from PySide import QtCore, QtGui

class LoginSessionManager(QtCore.QThread):

    def __init__(self, system_services):
        super(LoginSessionManager, self).__init__()
        
        self.__system_services = system_services
        self.__process_id = None
        self.__process_dir = None
        self.__login_db = {}
        self.__session = None
        self.__registered_projects = {
            'SysAdmin':"SysAdmin", 'sa':"SysAdmin",
            'Multics':"Multics", "m":"Multics",
        }
        self.__registered_users = {
            'JRCooper':"JRCooper", 'jrc':"JRCooper",
        }
        self.__user_projects = {
            'JRCooper':["SysAdmin", "Multics"],
        }
        self.__default_project = {
            'JRCooper':"SysAdmin", 'jrc': "SysAdmin",
        }
        
    @property
    def session(self):
        return self.__session
        
    @property
    def login_db(self):
        return self.__login_db
        
    def _add_user_to_login_db(self, user_id, login_time):
        #== Add a session block to the LOGIN DB for this session
        with MemoryMappedData(self.__login_db):
            self.__login_db.session_blocks[user_id] = LoginSessionBlock(login_time)
        # end with
        pprint(self.__login_db)
        
    def _remove_user_from_login_db(self, user_id):
        #== Remove the session block in the LOGIN DB corresponding to this session
        with MemoryMappedData(self.__login_db):
            del self.__login_db.session_blocks[user_id]
        # end with
        pprint(self.__login_db)
        
    def run(self):
        self._initialize()
        self._main_loop()
        
        # do any cleanup necessary at the LoginSessionManager level in response to a clean SHUTDOWN
        call.hcs_.delete_branch_(self.__process_dir)
        self.__session = None
        
        self.__system_services.shutdown()
        
    def kill(self):
        if self.__session:
            self._remove_user_from_login_db(self.__session.user_id)
            self.__session.kill()
        # end if
    
    def register_process(self, user_id, process_id, process_dir):
        with MemoryMappedData(self.__login_db):
            self.__login_db.session_blocks[user_id].process_id = process_id
            self.__login_db.session_blocks[user_id].process_dir = process_dir
        # end with
        pprint(self.__login_db)
    
    def _initialize(self):
        self.__process_id = 0o777777000000
        self.__process_dir = call.hcs_.create_process_dir(self.__process_id)
        
        #== Get a pointer to the LOGIN DB (create it if necessary)
        self.__login_db = call.hcs_.initiate(self.__process_dir, "login_db")
        if not self.__login_db:
            self.__login_db, code = call.hcs_.make_seg(self.__process_dir, "login_db", LoginDatabase)
        pprint(self.__login_db)
    
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
            self._add_user_to_login_db(self.__session.user_id, self.__session.login_time)
            
            code = self.__session.start()
            
            self._remove_user_from_login_db(self.__session.user_id)
            self.__session = None
        else:
            code = System.INVALID_LOGIN
        return code
    
    def _authenticate(self, user_id, password):
        user_id_components = user_id.split(".")
        person_id = self.__registered_users.get(user_id_components[0], "")
        try:
            project_id = self.__registered_projects.get(user_id_components[1], "")
        except:
            project_id = self.__default_project.get(person_id, "")
        # end try
        if person_id and project_id and project_id in self.__user_projects[person_id]:
            #== Check that there is a valid home directory!
            #== This info will be in the user account database
            user_id = person_id + "." + project_id
            from login_session import LoginSession
            return LoginSession(self.__system_services, self, user_id)
        else:
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
        
class LoginSessionBlock(object):

    def __init__(self, login_time):
        super(LoginSessionBlock, self).__init__()
        
        self.login_time = login_time
        self.process_id = None
        self.process_dir = None
        
    def __repr__(self):
        return "<%s.%s login_time: %s, process_id: %s, process_dir: %s>" % (__name__, self.__class__.__name__, self.login_time.ctime() if self.login_time else None, self.process_id, self.process_dir)
        