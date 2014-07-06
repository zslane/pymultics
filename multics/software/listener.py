import datetime

from ..globals import *

include.query_info

class Listener(SystemSubroutine):

    def __init__(self, supervisor, command_processor):
        super(Listener, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        self.__default_command_processor = command_processor
        self.__process = None
        self.__prev_command_time = None
        self.__command_history = []
        self.__homedir = ""
        self.exit_code = 0
        
    def start(self, owning_process):
        self.__process = owning_process
        return self._main_loop()
        
    def kill(self):
        self._cleanup()
        
    def ready(self, ready_mode):
        if ready_mode:
            now = datetime.datetime.now()
            delta, self.__prev_command_time = now - self.__prev_command_time, now
            if self.__process.stack_level() > 1:
                command_level_str = ", level %d" % (self.__process.stack_level())
            else:
                command_level_str = ""
            
            ready_message = "r %s %0.3f %d%s" % (now.strftime("%H%M"), delta.seconds + (delta.microseconds / 10.0**6), call.segfault_count, command_level_str)
            call.ioa_(ready_message)
    
    def _main_loop(self):
        command_line = parm()
        code         = parm()
        commands     = []
        
        query_info.suppress_name_sw = True
        query_info.suppress_spacing = True
        
        self._initialize()
        
        if not self.__process.pit().no_start_up:
            call.cu_.cp("exec_com start_up new_proc interactive", code)
        # end if
        
        self.exit_code = 0
        while self.exit_code == 0:
            try:
                #== If there are no more commands queued up from a multi-command line
                #== then get some commands from command_query_
                if commands == []:
                    call.cu_.ready_proc()
                    call.command_query_(query_info, command_line, "listener")
                    #== Semi-colons separate multiple commands--create a command queue
                    commands = command_line.val.split(";")
                # end if
                
                #== Get the next command in the queue and execute it
                command_line.val = commands.pop(0).strip()
                self.__command_history.append(command_line.val)
                call.cu_.cp(command_line.val, code)
                self.exit_code = code.val
                
            except BreakCondition:
                call.hcs_.signal_break()
            except DisconnectCondition:
                self.exit_code = System.LOGOUT
            except ShutdownCondition:
                self.exit_code = System.LOGOUT
            except (SegmentFault, LinkageError, InvalidSegmentFault):
                call.dump_traceback_()
            except:
                #== FOR DEBUGGING THE SIMULATION
                call.dump_traceback_()
            # end try
        # end while
        
        # do any cleanup necessary at the CommandShell level
        self._cleanup()
        
        return self.exit_code
        
    def _initialize(self):
        homedir = parm()
        call.user_info_.homedir(homedir)
        call.sys_.push_directory(homedir.val)
        call.cu_.set_command_processor(self.__default_command_processor)
        call.cu_.set_ready_procedure(self.ready)
        call.cu_.set_ready_mode(True)
        self.__homedir = homedir.val
        self.__prev_command_time = datetime.datetime.now()
        
        msg_handlers = {
            'interactive_message':   self._interactive_message_handler,
            'shutdown_announcement': self._interactive_message_handler,
        }
        self.__process.register_msg_handlers(msg_handlers)
        
        self._print_motd()
        
    def _interactive_message_handler(self, message):
        call.sys_.recv_message_(message)
    
    def _cleanup(self):
        pass
        
    def _print_motd(self):
        #== Only do this if the user does not have a start_up.ec in his
        #== home directory
        if not self.supervisor.fs.file_exists(self.__homedir + ">start_up.ec"):
            #== Open the system motd file if it exists and display its contents
            try:
                f = open(vfile_(self.supervisor.fs.system_control_dir + ">motd"))
                file_text = f.read()
                f.close()
                
                call.ioa_(file_text)
            except:
                pass
                