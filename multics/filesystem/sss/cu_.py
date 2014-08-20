import re

from multics.globals import *
    
class cu_(Subroutine):

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
        
    class arglist(object):
        def __init__(self, arg_list_ptr=None):
            self.argc = len(arg_list_ptr or [])
            self.type = 1
            self.desc = 0
            self.aptr = arg_list_ptr
        def __repr__(self):
            return "<arglist (%d): %r>" % (self.argc, self.aptr)
            
    def __init__(self):
        super(cu_, self).__init__(self.__class__.__name__)
        
    @property
    def _current_context(self):
        process = get_calling_process_()
        try:
            return process.stack.cp_contexts[-1]
        except:
            process.stack.cp_contexts = [cu_.context()]
            return process.stack.cp_contexts[-1]
        
    def _push_context(self):
        process = get_calling_process_()
        process.stack.cp_contexts.append(self._current_context.copy())
        
    def _pop_context(self):
        process = get_calling_process_()
        return process.stack.cp_contexts.pop()
    
    def split_(self, s, result):
        result.val = self._split(s)
        
    def _split(self, s, maxsplit=0):
        return [p for p in re.split(r'(\s)|"(.*?)"', s, maxsplit=maxsplit) if p and p.strip()]
    
    def arg_count(self, arg_count, code=None):
        arg_count.val = len(self._split(self._current_context.argument_string))
        if code is not None:
            code.val = 0
        else:
            return 0
        
    def arg_list(self, arg_list):
        arg_list.args = self._split(self._current_context.argument_string)
        
    def arg_list_ptr(self, arg_list=None):
        """
        cu_.arg_list_ptr can be called two different ways:
        
            call.cu_.arg_list_ptr (arg_list)
        or
            arg_list = cu_.arg_list_ptr()
        """
        arg_list_ptr = self._split(self._current_context.argument_string)
        if arg_list is not None:
            # arg_list.ptr = arg_list_ptr
            arg_list.ptr = cu_.arglist(arg_list_ptr)
        else:
            return arg_list_ptr
        
    def arg_ptr(self, arg_no, arg, code=None):
        try:
            arg.str = self._split(self._current_context.argument_string)[arg_no]
            if code is not None:
                code.val = 0
            else:
                return 0
        except KeyError:
            arg.str = null()
            if code is not None:
                code.val = error_table_.noarg
            else:
                return error_table_.noarg
        
    def arg_string(self, before, result, starting_with=0):
        s = self._current_context.argument_string
        d = self._split(s, starting_with or -1)
        before.list = d[:starting_with]
        result.val = d[-1]
        
    def get_command_name(self, command, code):
        command.name = self._current_context.program_name
        if not self._current_context.program_name:
            code.val = error_table_.no_command_name_available
        else:
            code.val = 0
        
    def set_command_string_(self, command_string):
        command_name, _, args_string = command_string.strip().partition(" ")
        self._current_context.program_name = command_name
        self._current_context.argument_string = args_string.strip()
    
    def set_command_processor(self, command_processor):
        self._current_context.command_processor = command_processor
        
    def get_command_processor(self, command_processor):
        command_processor.ptr = self._current_context.command_processor
        
    def cp(self, command_string, code):
        self._push_context()
        self._current_context.command_processor.execute(command_string, code)
        self._pop_context()
        
    def set_ready_procedure(self, ready_procedure):
        self._current_context.ready_procedure = ready_procedure
        
    def get_ready_procedure(self, ready_procedure):
        ready_procedure.ptr = self._current_context.ready_procedure
        
    def ready_proc(self, mode=None):
        if mode is None:
            self._current_context.ready_procedure(self._current_context.ready_mode)
        else:
            self._current_context.ready_procedure(mode)
        
    def set_ready_mode(self, mode):
        self._current_context.ready_mode = mode
        
    def get_ready_mode(self, mode):
        mode.val = self._current_context.ready_mode
        