
from multics.globals import *

class cu_(SystemExecutable):

    class context(object):
        def __init__(self):
            self.program_name = ""
            self.argument_string = ""
            self.command_processor = None
            self.ready_procedure = None
            self.ready_mode = True # print ready message flag
        def copy(self):
            new_context = cu_.context()
            new_context.program_name = self.program_name
            new_context.argument_string = self.argument_string
            new_context.command_processor = self.command_processor
            new_context.ready_procedure = self.ready_procedure
            new_context.ready_mode = self.ready_mode
            return new_context
        def __repr__(self):
            return "<context: '%s', '%s', %s>" % (self.program_name, self.argument_string, self.command_processor)
        
    def __init__(self, system_services):
        super(cu_, self).__init__(self.__class__.__name__, system_services)
        
        self.__contexts = []
        self.__contexts.append(cu_.context())
        
    def _push_context(self):
        current_context = self.__contexts[-1]
        self.__contexts.append(current_context.copy())
        
    def _pop_context(self):
        self.__contexts.pop()
        
    def arg_count(self, arg_count, code=None):
        arg_count.val = len(self.__contexts[-1].argument_string.split())
        if code:
            code.val = 0
        
    def arg_list(self, arg_list):
        arg_list.args = self.__contexts[-1].argument_string.split()
        
    def arg_ptr(self, arg_no, arg, code):
        try:
            arg.str = self.__contexts[-1].argument_string.split()[arg_no]
            code.val = 0
        except KeyError:
            arg.str = null()
            code.val = error_table_.noarg
        
    def arg_string(self, before, result, starting_with=0):
        s = self.__contexts[-1].argument_string
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
        command.name = self.__contexts[-1].program_name
        if not self.__contexts[-1].program_name:
            code.val = error_table_.no_command_name_available
        else:
            code.val = 0
        
    def set_command_string_(self, command_string):
        command_name, _, args_string = command_string.strip().partition(" ")
        self.__contexts[-1].program_name = command_name
        self.__contexts[-1].argument_string = args_string.strip()

    def set_command_processor(self, command_processor):
        self.__contexts[-1].command_processor = command_processor
        
    def get_command_processor(self, command_processor):
        command_processor.ptr = self.__contexts[-1].command_processor
        
    def cp(self, command_string, code):
        self._push_context()
        self.__contexts[-1].command_processor.execute(command_string, code)
        self._pop_context()
        
    def set_ready_procedure(self, ready_procedure):
        self.__contexts[-1].ready_procedure = ready_procedure
        
    def get_ready_procedure(self, ready_procedure):
        ready_procedure.ptr = self.__contexts[-1].ready_procedure
        
    def ready_proc(self, mode=None):
        if mode is None:
            self.__contexts[-1].ready_procedure(self.__contexts[-1].ready_mode)
        else:
            self.__contexts[-1].ready_procedure(mode)
        
    def set_ready_mode(self, mode):
        self.__contexts[-1].ready_mode = mode
        
    def get_ready_mode(self, mode):
        mode.val = self.__contexts[-1].ready_mode
        