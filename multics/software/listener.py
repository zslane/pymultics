
from multics.globals import *

include.query_info

class Listener(SystemExecutable):

    def __init__(self, system_services, command_processor):
        super(Listener, self).__init__(self.__class__.__name__, system_services)
        
        self.__system_services = system_services
        self.__default_command_processor = command_processor
        self.__command_prompt = "! "
        self.__command_history = []
        
    def start(self):
        declare (homedir = parm)
        call.user_info_.homedir(homedir)
        call.sys_.push_directory(homedir.name)
        call.cu_.set_command_processor(self.__default_command_processor)
        call.cu_.set_ready_procedure(self.ready)
        call.cu_.set_ready_mode(True)
        code = self._run_start_up_script(homedir.name)
        return code or self._main_loop()
        
    def kill(self):
        self._cleanup()
        
    def ready(self, ready_mode):
        if ready_mode:
            call.ioa_.nnl(self.__command_prompt)
    
    def _run_start_up_script(self, homedir):
        declare (code = parm)
        
        native_path = self.__system_services.hardware.filesystem.path2path(homedir, "start_up.py")
        if self.__system_services.hardware.filesystem.file_exists(native_path):
            print "Running user start_up.py script"
            execfile(native_path, globals())
        # end if
        native_path = self.__system_services.hardware.filesystem.path2path(homedir, "start_up.ec")
        if self.__system_services.hardware.filesystem.file_exists(native_path):
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
        
        code.val = 0
        while code.val == 0:
            try:
                call.cu_.ready_proc()
                call.command_query_(query_info, command_line, "listener")
                self.__command_history.append(command_line.val)
                call.cu_.cp(command_line.val, code)
                
            except BreakCondition:
                call.hcs_.signal_break()
            except DisconnectCondition:
                code.val = System.LOGOUT
            except ShutdownCondition:
                code.val = System.SHUTDOWN
            except (SegmentFault, LinkageError, InvalidSegmentFault):
                call.dump_traceback_()
            except:
                #== FOR DEBUGGING THE SIMULATION
                call.dump_traceback_()
            # end try
        # end while
        
        # do any cleanup necessary at the CommandShell level
        self._cleanup()
        
        return code.val
            
    def _on_condition__break(self):
        pass
        
    def _cleanup(self):
        pass
        