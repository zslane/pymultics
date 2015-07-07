
from multics.globals import *

class command_processor_(CommandProcessor):

    def __init__(self):
        super(command_processor_, self).__init__(self.__class__.__name__)
        
    def execute(self, command_line, code):
        segment = parm()
        command = parm()
        
        command_line = self._strip_comments(command_line)
        if command_line != "":
            call.cu_.set_command_string_(command_line)
            call.cu_.get_command_name(command, code)
            call.hcs_.get_entry_point(command.name, segment)
            program_entry_point = segment.ptr
            if program_entry_point:
                program_entry_point()
            else:
                directory = parm()
                code      = parm()
                call.sys_.get_abs_path(command.name, segment)
                call.sys_.split_path_(segment.path, directory, segment)
                call.hcs_.fs_file_exists(directory.val, segment.name + ".py", code)
                if code.val == 0:
                    call.ioa_("No entry point ^a in segment ^a.", command.name, command.name)
                else:
                    call.ioa_("Segment ^a not found.", command.name)
                # end if
            # end if
        # end if
        
        call.sys_.get_exit_code(code)
    
    def _strip_comments(self, command_string):
        pos = command_string.find(";")
        if pos != -1:
            return command_string[:pos].strip()
        else:
            return command_string.strip()
            