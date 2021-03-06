import datetime

from ..globals import *

from PySide import QtCore, QtGui

login_help_text = (
"""    login, l [person_id] {project_id} {-control_args}
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

include.iox_control
declare (iox_ = entry)

class UserControl(object):

    #== EXTERNAL STATES ==#
    CONTINUE       = 0
    LOGIN_COMPLETE = 1
    DISCONNECTED   = 2
    
    #== INTERNAL STATES ==#
    WAITING_FOR_LINEFEED = 3
    WAITING_FOR_LOGIN_COMMAND = 4
    WAITING_FOR_PASSWORD = 5
    WAITING_FOR_CHANGE_PASSWORD = 6
    WAITING_FOR_CHANGE_PASSWORD_CONFIRM = 7
    CREATING_PROCESS = 8
    
    TIMEOUT_PERIOD = 60 * 1 # 1 minute
    
    def __init__(self, max_attempts, whotab, tty_channel, wait_for_linefeed=True):
        self.__whotab        = whotab
        self.__tty_channel   = tty_channel
        self.__start_time    = None
        self.__state         = None
        self.__max_attempts  = max_attempts
        self.__login_options = {}
        self.__new_password  = ""
        
        if wait_for_linefeed:
            self._set_state(self.WAITING_FOR_LINEFEED)
        else:
            self._go_to_login()
        
    @property
    def tty(self):
        return self.__tty_channel
        
    @property
    def hardware(self):
        return GlobalEnvironment.hardware
    
    def do_state(self):
        try:
            if self._terminal_closed():
                return self._set_state(self.DISCONNECTED)
            elif self.__state == self.WAITING_FOR_LINEFEED:
                return self._wait_for_linefeed()
            elif self.__state == self.WAITING_FOR_LOGIN_COMMAND:
                return self._wait_for_login_command()
            elif self.__state == self.WAITING_FOR_PASSWORD:
                return self._wait_for_password()
            elif self.__state == self.WAITING_FOR_CHANGE_PASSWORD:
                return self._wait_for_password_change()
            elif self.__state == self.WAITING_FOR_CHANGE_PASSWORD_CONFIRM:
                return self._wait_for_password_change_confirm()
            else:
                return self.__state
                
        except DisconnectCondition:
            print "UserControl.do_state(): Terminal DISCONNECT detected."
            return self._set_state(self.DISCONNECTED)
            
    def login_options(self):
        return self.__login_options or {}
        
    def _set_state(self, new_state):
        self.__state = new_state
        if new_state in [self.LOGIN_COMPLETE, self.DISCONNECTED]:
            return new_state
        else:
            self.__start_time = datetime.datetime.now()
            return self.CONTINUE
        
    def _timeout_expired(self):
        #== Only actual terminals can timeout...the mainframe console never times out
        if self.tty and (datetime.datetime.now() - self.__start_time).seconds > self.TIMEOUT_PERIOD:
            self.tty.set_input_mode(QtGui.QLineEdit.Normal)
            self.tty.disconnect()
            return self._set_state(self.DISCONNECTED)
        else:
            return self.CONTINUE
            
    #== User I/O is directly through the hardware's I/O subsystem
    def _terminal_closed(self):
        return iox_.terminal_closed(self.tty)
    def _linefeed_received(self):
        LF = chr(10)
        buffer = parm()
        call.iox_.peek_char(self.tty, buffer)
        if buffer.val == LF:
            self._flush_input()
        return buffer.val == LF
    def _break_received(self):
        return iox_.break_received(self.tty)
    def _has_input(self):
        return iox_.has_input(self.tty)
    def _get_input(self, echo=False):
        iox_control.echo_input_sw = echo
        iox_control.filter_chars = common_ctrl_chars
        buffer = parm()
        call.iox_.wait_get_line(self.tty, iox_control, buffer)
        return buffer.val
    def _flush_input(self):
        call.iox_.flush_input(self.tty)
    def _set_input_mode(self, mode):
        call.iox_.set_input_mode(self.tty, mode)
    def _put_output(self, s):
        call.iox_.write(self.tty, s)
        
    def _display_login_banner(self):
        load = len(os.listdir(GlobalEnvironment.fs.path2path(GlobalEnvironment.fs.process_dir_dir)))
        date_time_string = datetime.datetime.now().strftime("%m/%d/%y %H%M.%S %Z %a")
        self._put_output("Virtual Multics MR%s: %s, %s\nLoad = %0.1f out of %0.1f: users = %d. %s\n" % (
            GlobalEnvironment.supervisor.version,
            GlobalEnvironment.supervisor.site_config['site_location'],
            GlobalEnvironment.supervisor.site_config['site_name'],
            load, GlobalEnvironment.supervisor.site_config['maximum_load'],
            len(self.__whotab.entries),
            datetime.datetime.now().ctime()))
        
    def _go_to_login(self, suppress_banner=False):
        self._set_input_mode(QtGui.QLineEdit.Normal)
        if not suppress_banner:
            self._display_login_banner()
        return self._set_state(self.WAITING_FOR_LOGIN_COMMAND)
    
    def _wait_for_linefeed(self):
        if self._linefeed_received():
            return self._go_to_login()
            
        elif self._break_received() or self._has_input():
            #== Race condition: check for linefeed again
            if self._linefeed_received():
                return self._go_to_login()
            
            #== Ignore BREAK signals and all other keyboard input
            self._flush_input()
            return self._set_state(self.WAITING_FOR_LINEFEED)
            
        else:
            return self._timeout_expired()
        
    def _wait_for_login_command(self):
        command_name = parm()
        code         = parm()
        
        if self._has_input():
            command_line = self._get_input(echo=True)
            if command_line:
                call.cu_.set_command_string_(command_line)
                call.cu_.get_command_name(command_name, code)
                if command_name.val == "login" or command_name.val == "l":
                    self.__login_options = self._verify_login_command()
                    if self.__login_options:
                        self._set_input_mode(QtGui.QLineEdit.Password)
                        self._put_output("Password:\n")
                        return self._set_state(self.WAITING_FOR_PASSWORD)
                    # end if
                elif command_name.val == "help" or command_name.val == "?":
                    self._put_output(help_text)
                else:
                    self._error_msg("Incorrect login word \"%s\"." % (command_name.val))
                # end if
            # end if
            return self._set_state(self.WAITING_FOR_LOGIN_COMMAND) # resets timeout
        else:
            return self._timeout_expired()
        
    def _verify_login_command(self):
        arg_list = parm()
        password = parm()
        code     = parm()
        
        def show_usage():
            self._put_output("Usage:\n" + login_help_text)
        # end if
        
        call.cu_.arg_list(arg_list)
        if len(arg_list.args) == 0:
            show_usage()
            return None
        # end if
        
        project = ""
        login_options = {}
        login_options['change_password'] = False
        login_options['project_id'] = ""
        login_options['login_name'] = arg_list.args.pop(0)
        
        i = 0
        while i < len(arg_list.args):
            arg = arg_list.args[i]
            i += 1
            
            if i == 1 and not arg.startswith("-"):
                login_options['project_id'] = arg
                
            elif arg == "-change_password" or arg == "-cpw":
                login_options['change_password'] = True
                
            elif arg == "-home_dir" or arg == "-hd":
                if i < len(arg_list.args):
                    login_options['home_dir'] = arg_list.args[i]
                    i += 1
                else:
                    self._error_msg("-home_dir requires a path argument")
                    return None
                # end if
                
            elif arg == "-brief" or arg == "-bf":
                login_options['brief'] = True
                
            elif arg == "-no_start_up" or arg == "-ns":
                login_options['no_start_up'] = True
                
            elif arg.startswith("-"):
                self._error_msg("Unrecognized control argument " + arg)
                return None
                
            else:
                show_usage()
                return None
            # end if
        # end while
        
        return login_options
        
    def _wait_for_password(self):
        if self._break_received():
            self._error_msg("QUIT")
            return self._go_to_login(suppress_banner=True)
            
        elif self._has_input():
            self._put_output("\n")
            self._set_input_mode(QtGui.QLineEdit.Normal)
            password = self._get_input()
            user_lookup = self._authenticate(self.__login_options, password) # _authenticate() prints all our error messages for us
            if user_lookup:
                person_id, pdt = user_lookup
                self.__login_options['person_id'] = person_id
                self.__login_options['project_id'] = pdt.project_id
                self.__login_options['pdt'] = pdt
                if self.__login_options.get('change_password'):
                    self._set_input_mode(QtGui.QLineEdit.Password)
                    self._put_output("New password:\n")
                    return self._set_state(self.WAITING_FOR_CHANGE_PASSWORD)
                # end if
                return self._set_state(self.LOGIN_COMPLETE)
                
            elif self.__max_attempts == 0: # too many password failures!
                call.iox_.disconnect_tty(self.tty)
                return self._set_state(self.DISCONNECTED)
                
            else:
                return self._set_state(self.WAITING_FOR_LOGIN_COMMAND)
            # end if
            
        else:
            return self._timeout_expired()
        
    def _authenticate(self, options, password):
        pnt_segment = parm()
        code        = parm()
        
        login_name = options['login_name']
        project = options['project_id']
        if password == "*": password = ""
        
        try:
            call.hcs_.initiate(GlobalEnvironment.fs.system_control_dir, "PNT.pnt", "", 0, 0, pnt_segment, code)
            person_id = pnt_segment.ptr.person_id(login_name)
            project = project or pnt_segment.ptr.get_default_project_id(person_id)
            encrypted_password, pubkey = pnt_segment.ptr.get_password(person_id)
            if (not pubkey) or (GlobalEnvironment.supervisor.encrypt_password(password, pubkey) == encrypted_password):
                pdt = GlobalEnvironment.supervisor.pdt.get(project)
                if pdt and pdt.recognizes(person_id):
                    user_id = person_id + "." + pdt.project_id
                    if user_id in self.__whotab.entries:
                        self._error_msg("%s is already logged in." % (user_id))
                        return None
                    # end if
                    return (person_id, pdt)
                # end if
            else:
                self._put_output("Incorrect password supplied.")
                #== Track password failures for ttys (but not the system console)
                if self.tty:
                    self.__max_attempts -= 1
                # end if
                if self.__max_attempts != 0:
                    self._error_msg("")
                return None
            # end if
        except:
            # call.dump_traceback_()
            pass
        # end try
        self._error_msg("The user name you supplied is not registered.")
        return None
    
    def _wait_for_password_change(self):
        if self._break_received():
            self._error_msg("QUIT")
            return self._go_to_login(suppress_banner=True)
            
        elif self._has_input():
            self.__new_password = self._get_input()
            self._put_output("\n")
            self._put_output("New password again:\n")
            return self._set_state(self.WAITING_FOR_CHANGE_PASSWORD_CONFIRM)
            
        else:
            return self._timeout_expired()
        
    def _wait_for_password_change_confirm(self):
        pnt_segment = parm()
        code        = parm()
        
        if self._break_received():
            self._error_msg("QUIT")
            return self._go_to_login(suppress_banner=True)
            
        elif self._has_input():
            self._put_output("\n")
            self._set_input_mode(QtGui.QLineEdit.Normal)
            confirm_password = self._get_input()
            if self.__new_password == confirm_password:
                person_id = self.__login_options['person_id']
                call.hcs_.initiate(GlobalEnvironment.fs.system_control_dir, "PNT.pnt", "", 0, 0, pnt_segment, code)
                current = pnt_segment.ptr.name_entries[person_id]
                encrypted_password, pubkey = GlobalEnvironment.supervisor.encrypt_password(self.__new_password)
                with pnt_segment.ptr:
                    pnt_segment.ptr.add_person(person_id, current.alias, current.default_project_id, encrypted_password, pubkey)
                # end with
                self._put_output("Password changed.\n")
            else:
                self._put_output("Entries do not match. Password not changed.\n")
            # end if
            return self._set_state(self.LOGIN_COMPLETE)
            
        else:
            return self._timeout_expired()
        
    def _error_msg(self, message):
        self._put_output(message + "\n")
        self._put_output("Please try again or type \"help\" for instructions.\n")
        