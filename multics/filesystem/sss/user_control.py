
from multics.globals import *

from PySide import QtCore, QtGui

login_usage_text = (
"""Usage: login|l [person_id] {{project_id}} {{-change_password|-cp}}
"""
)

class site_config(object):

    site_location = "Casa De Vida 156, Los Angeles"
    site_name = "System P"
    
class user_control(CommandProcessor):

    def __init__(self):
        super(user_control, self).__init__(self.__class__.__name__)
        
        self.__person_name_table = None
        self.__project_definition_tables = None
        self.__whotab = None
        
    def do_login(self, supervisor, pnt, pdt, whotab):
    
        declare (command_name = parm,
                 code         = parm)
                 
        self.supervisor = supervisor
        self.__person_name_table = pnt
        self.__project_definition_tables = pdt
        self.__whotab = whotab
        
        self.supervisor.llout("\nVirtual Multics MR0.2: %s, %s\nusers = %d\n" % (site_config.site_location, site_config.site_name, len(whotab.entries)))
        
        user_lookup = None
        while not user_lookup:
            command_line = ""
            while command_line == "":
                command_line = self.supervisor.llin(block=True)
                self.supervisor.llout(command_line + "\n")
                if command_line:
                    call.cu_.set_command_string_(command_line)
                    call.cu_.get_command_name(command_name, code)
                    if command_name.val== "login" or command_name.val == "l":
                        user_lookup = self.login()
                    elif command_name.val == "help" or command_name.val == "?":
                        call.ioa_("Available commands:\n  login,l [person_id] {{project_id}} {{-change_password|-cp}}\n  help,?")
                        command_line = ""
                    # end if
                # end if
            # end while
        # end while
        return user_lookup
        
    def login(self):
        declare (arg_list = parm,
                 code     = parm)
        
        def show_usage():
            call.ioa_(login_usage_text)
        
        call.cu_.arg_list(arg_list)
        if len(arg_list.args) == 0:
            show_usage()
            return
            
        project = ""
        change_password = False
        
        login_name = arg_list.args.pop(0)
        
        i = 0
        while i < len(arg_list.args):
            arg = arg_list.args[i]
            if i == 0 and not arg.startswith("-"):
                project = arg
                i += 1
            elif arg == "-change_password" or arg == "-cp":
                change_password = True
                i += 1
            else:
                call.ioa_("Unrecognized argument {0}", arg)
                return
            # end if
        # end while
        
        self.supervisor.set_input_mode(QtGui.QLineEdit.Password)
        self.supervisor.llout("password:\n")
        password = self.supervisor.llin(block=True)
        self.supervisor.set_input_mode(QtGui.QLineEdit.Normal)
        
        user_lookup = self._authenticate(login_name, project, password)
        
        if user_lookup and change_password:
            person_id, _ = user_lookup
            self._change_user_password(person_id)
        # end if
        
        return user_lookup
        
    def _authenticate(self, login_name, project, password):
        person_id = self.__person_name_table.person_id(login_name)
        try:
            encrypted_password, pubkey = self.__person_name_table.get_password(person_id)
            if (not pubkey) or (rsa.encode(password, pubkey) == encrypted_password):
                project = project or self.__person_name_table.get_default_project_id(person_id)
                pdt = self.__project_definition_tables.get(project)
                if pdt and pdt.recognizes(person_id):
                    user_id = person_id + "." + pdt.project_id
                    if user_id in self.__whotab.entries:
                        self.supervisor.llout("%s is already logged in\n\n" % (user_id))
                        return None
                    # end if
                    return person_id, pdt
                # end if
            # end if
        except:
            # call.dump_traceback_()
            pass
        # end try
        self.supervisor.llout("Unrecognized user id/password\n\n")
        return None
    
    def _change_user_password(self, person_id):
        self.supervisor.set_input_mode(QtGui.QLineEdit.Password)
        
        self.supervisor.llout("new password:\n")
        new_password = self.supervisor.llin(block=True)
        self.supervisor.llout("new password again:\n")
        confirm_password = self.supervisor.llin(block=True)
        
        self.supervisor.set_input_mode(QtGui.QLineEdit.Normal)
        
        if new_password == confirm_password:
            current = self.__person_name_table.name_entries[person_id]
            encrypted_password, pubkey = self.supervisor.encrypt_password(new_password)
            with self.__person_name_table:
                self.__person_name_table.add_person(person_id, current.alias, current.default_project_id, encrypted_password, pubkey)
            # end with
        else:
            self.supervisor.llout("Entries do not match. Password not changed.\n")
            