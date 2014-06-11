
from multics.globals import *

class cu_(SystemExecutable):
    def __init__(self, system_services):
        super(cu_, self).__init__(self.__class__.__name__, system_services)
        
        self.__program_name = ""
        self.__argument_string = ""
        self.__command_processor = None
        self.__ready_procedure = None
        self.__ready_mode = True # print ready message flag
        
    def arg_count(self, arg_count, code=None):
        arg_count.val = len(self.__argument_string.split())
        if code:
            code.val = 0
        
    def arg_list(self, arg_list):
        arg_list.args = self.__argument_string.split()
        
    def arg(self, arg_no, arg, code):
        try:
            arg.str = self.__argument_string.split()[arg_no]
            code.val = 0
        except KeyError:
            arg.str = null()
            code.val = error_table_.noarg
        
    def arg_string(self, before, result, starting_with=0):
        s = self.__argument_string
        d = []
        for i in range(starting_with):
            discard, _, s = s.strip().partition(" ")
            d.append(discard)
        # end for
        before.list = d
        result.val = s.strip()
        return
        if d:
            return (d, s.strip())
        else:
            return s.strip()
        
    def get_command_name(self, command, code):
        command.name = self.__program_name
        if not self.__program_name:
            code.val = error_table_.no_command_name_available
        else:
            code.val = 0
        
    def set_command_string_(self, command_string):
        command_name, _, args_string = command_string.strip().partition(" ")
        self.__program_name = command_name
        self.__argument_string = args_string.strip()

    def set_command_processor(self, command_processor):
        self.__command_processor = command_processor
        
    def get_command_processor(self, command_processor):
        command_processor.ptr = self.__command_processor
        
    def cp(self, command_string, code):
        self.__command_processor.execute(command_string, code)
        
    def set_ready_procedure(self, ready_procedure):
        self.__ready_procedure = ready_procedure
        
    def get_ready_procedure(self, ready_procedure):
        ready_procedure.ptr = self.__ready_procedure
        
    def ready_proc(self, mode=None):
        if mode is None:
            self.__ready_procedure(self.__ready_mode)
        else:
            self.__ready_procedure(mode)
        
    def set_ready_mode(self, mode):
        self.__ready_mode = mode
        
    def get_ready_mode(self, mode):
        mode.val = self.__ready_mode
        