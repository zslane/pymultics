
from ..globals import *

include.query_info

class Listener(SystemExecutable):

    def __init__(self, supervisor, command_processor):
        super(Listener, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        self.__default_command_processor = command_processor
        self.__process = None
        self.__command_prompt = "! "
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
            call.ioa_.nnl(self.__command_prompt)
    
    def _run_start_up_script(self, homedir):
        declare (code = parm)
        
        native_path = self.supervisor.hardware.filesystem.path2path(homedir, "start_up.py")
        if self.supervisor.hardware.filesystem.file_exists(native_path):
            print "Running user start_up.py script"
            execfile(native_path, globals())
        # end if
        native_path = self.supervisor.hardware.filesystem.path2path(homedir, "start_up.ec")
        if self.supervisor.hardware.filesystem.file_exists(native_path):
            print "Running user start_up.ec script"
            with open(native_path, "r") as f:
                for command_line in f:
                    call.cu_.cp(command_line, code)
                    if code.val != 0:
                        return code.val
                    # end if
                # end for
            # end with
        # end if
        return 0
        
    def _main_loop(self):
        declare (command_line = parm,
                 code         = parm)
        query_info.suppress_name_sw = True
        query_info.suppress_spacing = True
        
        self._initialize()
        
        self.exit_code = self._run_start_up_script(self.__homedir)
        
        while self.exit_code == 0:
            try:
                call.cu_.ready_proc()
                call.command_query_(query_info, command_line, "listener")
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
            
    def _on_condition__break(self):
        pass
        
    def _initialize(self):
        declare (homedir = parm)
        call.user_info_.homedir(homedir)
        call.sys_.push_directory(homedir.val)
        call.cu_.set_command_processor(self.__default_command_processor)
        call.cu_.set_ready_procedure(self.ready)
        call.cu_.set_ready_mode(True)
        self.__homedir = homedir.val
        
        msg_handlers = {
            'interactive_message':   self._interactive_message_handler,
            'shutdown_announcement': self._interactive_message_handler,
            'shutdown':              self._shutdown_handler,
        }
        self.__process.register_msg_handlers(msg_handlers)
        
    def _interactive_message_handler(self, message):
        call.sys_.recv_message_(message)
    
    def _shutdown_handler(self, message):
        print get_calling_process_().objectName() + " invoking _shutdown_handler"
        self.exit_code = System.LOGOUT
    
    def _cleanup(self):
        pass
        