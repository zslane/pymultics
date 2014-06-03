
from ..globals import *
from query_info import *

from PySide import QtCore, QtGui

class CommandShell(QtCore.QObject):

    def __init__(self, system_services):
        super(CommandShell, self).__init__()
        
        self.__system_services = system_services
        self.__command_prompt = "! "
        self.__command_history = []
        
    def start(self):
        declare (homedir = parm)
        call.user_info_.homedir(homedir)
        call.sys_.push_directory(homedir.name)
        return self._main_loop()
        
    def kill(self):
        self._cleanup()
        
    def _main_loop(self):
        declare (command_line = parm)
        query_info = query_info_structure()
        query_info.suppress_name_sw = True
        query_info.suppress_spacing = True
        
        code = 0
        while code == 0:
            try:
                call.ioa_.nnl(self.__command_prompt)
                call.command_query_(query_info, command_line, "command shell")
                self.__command_history.append(command_line.val)
                code = self._parse_and_execute(command_line.val)
            except BreakCondition:
                call.hcs_.signal_break()
            except (SegmentFault, LinkageError, InvalidSegmentFault):
                call.dump_traceback_()
            except:
                #== FOR DEBUGGING THE SIMULATION
                call.dump_traceback_()
            # end try
        # end while
        
        # do any cleanup necessary at the CommandShell level
        self._cleanup()
        
        return code
        
    def _parse_and_execute(self, command_line):
        declare (segment = parm)
        
        if command_line == "logout":
            return System.LOGOUT
        elif command_line == "new_proc":
            return System.NEW_PROCESS
            
        else:
            if command_line == "":
                #== Empty command strings are okay; just ignore them
                return 0
            # end if
            
            program_name, _, argument_string = command_line.partition(" ")
            call.cu_.set_command_line_(program_name, argument_string)
            call.hcs_.get_entry_point(program_name, segment)
            program_entry_point = segment.ptr
            if program_entry_point:
                # code = program_entry_point() or 0
                program_entry_point()
                code = 0
            else:
                call.ioa_("Unrecognized command {0}", program_name)
                code = 0
            # end if
            
            return code
    
    def _on_condition__break(self):
        pass

    def _cleanup(self):
        pass
        