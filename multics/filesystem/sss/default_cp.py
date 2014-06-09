
from multics.globals import *

class default_cp(CommandProcessor):

    def __init__(self):
        super(default_cp, self).__init__(self.__class__.__name__)
        
    def execute(self, command_line, code):
        declare (segment = parm,
                 command = parm)
        
        command_line = self._strip_comments(command_line)
        
        if command_line == "logout":
            code.val = System.LOGOUT
        elif command_line == "new_proc":
            code.val = System.NEW_PROCESS
            
        else:
            if command_line != "":
                call.cu_.set_command_string_(command_line)
                call.cu_.get_command_name(command, code)
                call.hcs_.get_entry_point(command.name, segment)
                program_entry_point = segment.ptr
                if program_entry_point:
                    program_entry_point()
                else:
                    call.ioa_("Unrecognized command {0}", command.name)
            # end if
            
            code.val = 0

    def _strip_comments(self, command_string):
        pos = command_string.find(";")
        if pos != -1:
            return command_string[:pos].strip()
        else:
            return command_string.strip()
            