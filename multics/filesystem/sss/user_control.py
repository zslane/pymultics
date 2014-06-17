import os

from multics.globals import *

from PySide import QtCore, QtGui

login_help_text = (
"""    login, l [person_id] {{project_id}} {{-control_args}}
        -change_password, -cpw
        -home_dir [path], -h [path]
        -no_start_up, -ns
"""
)

help_text = (
"""Available commands:
""" +
login_help_text +
"""
    help, ?
"""
)

class user_control(CommandProcessor):

    def __init__(self):
        super(user_control, self).__init__(self.__class__.__name__)
        
        self.__person_name_table = None
        self.__project_definition_tables = None
        self.__whotab = None
        
    def display_login_banner(self):
        load = len(os.listdir(self.supervisor.hardware.filesystem.path2path(self.supervisor.hardware.filesystem.process_dir_dir)))
        self.supervisor.llout("\nVirtual Multics MR0.2: %s, %s\nLoad = %0.1f out of %0.1f: users = %d\n" % (
            self.supervisor.site_config['site_location'],
            self.supervisor.site_config['site_name'],
            load, self.supervisor.site_config['maximum_load'],
            len(self.__whotab.entries)))
            
    def login_ui(self, supervisor, pnt, pdt, whotab):
    
        declare (command_name = parm,
                 code         = parm)
                 
        self.supervisor = supervisor
        self.__person_name_table = pnt
        self.__project_definition_tables = pdt
        self.__whotab = whotab
        
        self.display_login_banner()
        
        login_options = None
        while not login_options:
            command_line = ""
            while command_line == "":
                try:
                    command_line = self.supervisor.llin(block=True)
                    self.supervisor.llout(command_line + "\n")
                    if command_line:
                        call.cu_.set_command_string_(command_line)
                        call.cu_.get_command_name(command_name, code)
                        if command_name.val== "login" or command_name.val == "l":
                            login_options = self.login_command()
                        elif command_name.val == "help" or command_name.val == "?":
                            call.ioa_(help_text)
                            command_line = ""
                        # end if
                    # end if
                except BreakCondition:
                    self.supervisor.set_input_mode(QtGui.QLineEdit.Normal)
                    self.display_login_banner()
                    command_line = ""
                # end try
            # end while
        # end while
        return login_options
        
    def login_command(self):
        declare (arg_list = parm,
                 password = parm,
                 code     = parm)
        
        def show_usage():
            call.ioa_("Usage:\n" + login_help_text)
        # end if
        
        call.cu_.arg_list(arg_list)
        if len(arg_list.args) == 0:
            show_usage()
            return
        # end if
            
        project = ""
        change_password = False
        login_options = {}
        login_options['project_id'] = ""
        
        login_name = arg_list.args.pop(0)
        
        i = 0
        while i < len(arg_list.args):
            arg = arg_list.args[i]
            i += 1
            
            if i == 1 and not arg.startswith("-"):
                login_options['project_id'] = arg
                
            elif arg == "-change_password" or arg == "-cpw":
                change_password = True
                
            elif arg == "-home_dir" or arg == "-hd":
                if i < len(arg_list.args):
                    login_options['home_dir'] = arg_list.args[i]
                    i += 1
                else:
                    call.ioa_("-home_dir requires a path argument")
                    return
                # end if
                
            elif arg == "-no_start_up" or arg == "-ns":
                login_options['no_start_up'] = True
                
            elif arg.startswith("-"):
                call.ioa_("Unrecognized control argument {0}", arg)
                return
                
            else:
                show_usage()
                return
            # end if
        # end while
        
        call.read_password_("password:", password)
        
        user_lookup = self._authenticate(login_name, login_options['project_id'], password.val, login_options)
        if user_lookup:
            person_id, pdt = user_lookup
            login_options['person_id'] = person_id
            login_options['project_id'] = pdt.project_id
            login_options['pdt'] = pdt
            if change_password:
                self._change_user_password(login_options['person_id'])
            # end if
        else:
            return None
        # end if
        
        return login_options
        
    def _authenticate(self, login_name, project, password, options):
        if password == "*": password = ""
        person_id = self.__person_name_table.person_id(login_name)
        try:
            encrypted_password, pubkey = self.__person_name_table.get_password(person_id)
            if (not pubkey) or (self.supervisor.encrypt_password(password, pubkey) == encrypted_password):
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
        try:
            self.supervisor.set_input_mode(QtGui.QLineEdit.Password)
            
            self.supervisor.llout("new password:\n")
            new_password = self.supervisor.llin(block=True)
            self.supervisor.llout("new password again:\n")
            confirm_password = self.supervisor.llin(block=True)
            
            self.supervisor.set_input_mode(QtGui.QLineEdit.Normal)
            
        except:
            self.supervisor.set_input_mode(QtGui.QLineEdit.Normal)
            raise
        # end try
        
        if new_password == confirm_password:
            current = self.__person_name_table.name_entries[person_id]
            encrypted_password, pubkey = self.supervisor.encrypt_password(new_password)
            with self.__person_name_table:
                self.__person_name_table.add_person(person_id, current.alias, current.default_project_id, encrypted_password, pubkey)
            # end with
        else:
            self.supervisor.llout("Entries do not match. Password not changed.\n")
            