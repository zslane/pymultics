import re

from multics.globals import *

include. query_info
include. ssu_request_macros

class ssu_abort_line(Exception): pass

class ssu_(Subroutine):
    def __init__(self):
        super(ssu_, self).__init__(self.__class__.__name__)

    def create_invocation(self, subsystem_name, version_string, info_ptr, request_table_ptr, info_directory, sci_ptr, code):
        sci_ptr.ptr                = subsystem_control_info()
        sci_ptr.ptr.subsystem_name = subsystem_name
        sci_ptr.ptr.version_string = version_string
        sci_ptr.ptr.prompt_string  = "^/%s:  " % (subsystem_name)
        sci_ptr.ptr.info_ptr       = info_ptr
        sci_ptr.ptr.request_table  = request_table_ptr
        sci_ptr.ptr.info_directory = info_directory
        
        code.val = 0
        
    def set_prompt_mode(self, sci_ptr, prompt_mode):
        sci_ptr.ptr.prompt_mode = prompt_mode
        
    def set_prompt(self, sci_ptr, prompt_string):
        sci_ptr.ptr.prompt_string = prompt_string
        
    def set_procedure(self, sci_ptr, procedure_name, procedure_value, code):
        sci_ptr.ptr.procedures[procedure_name] = procedure_value
        code.val = 0
        
    def set_info_prefix(self, sci_ptr, info_prefix):
        pass
        
    def listen(self, sci_ptr, iocb_ptr, code):
        command = char ('*') . parm . init ("")
        code    = fixed.bin (35) . parm . init (0)
        commands = []
        
        query_info.version = query_info_version_5
        query_info.suppress_spacing = True
        query_info.suppress_name_sw = True
        
        while sci_ptr.ptr.exit_code == -1:
        
            #== If there are no more commands queued up from a multi-command line
            #== then get some commands from command_query_
            if commands == []:
                pre_request_proc = sci_ptr.ptr.procedures.get("pre_request_line")
                if pre_request_proc:
                    pre_request_proc(sci_ptr)
                # end if
                
                if sci_ptr.ptr.prompt_mode & bitstring(3, b'010'):
                    call. ioa_.nnl (sci_ptr.ptr.prompt_string)
                # end if
                
                call. command_query_ (query_info, command, sci_ptr.ptr.subsystem_name)
                #== Semi-colons separate multiple commands--create a command queue
                commands = command.val.split(";")
            # end if
            
            #== Get the next command in the queue and execute it
            command.val = commands.pop(0).strip()
            
            self.execute_string(sci_ptr, command.val, code)
            if code.val == 0:
                if command.val == "*":
                    sci_ptr.ptr.exit_code = 0
                # end if
            # end for
        
    def destroy_invocation(self, sci_ptr):
        pass
        
    def get_info_ptr(self, sci_ptr):
        return sci_ptr.info_ptr
        
    def arg_count(self, sci_ptr, arg_count):
        arg_count.val = len(self._split(sci_ptr.ptr.args_string))
        
    def arg_ptr(self, sci_ptr, arg_index, arg_ptr):
        try:
            arg_ptr.val = self._split(sci_ptr.ptr.args_string)[arg_index]
        except:
            arg_ptr.val = null()
            self.abort_line(sci_ptr, error_table_.noarg)
            
    def _split(self, s, maxsplit=0):
        return [p for p in re.split(r'(\s)|"(.*?)"', s, maxsplit=maxsplit) if p and p.strip()]
    
    def execute_string(self, sci_ptr, command_string, code):
        command_string = command_string.strip()
        if command_string == "":
            code.val = 0
            return
        # end if
        
        request_name, _, args_string = command_string.partition(" ")
        
        for request in sci_ptr.ptr.request_table.table_entries:
            if ((request_name == request.long_name or request_name == request.short_name) and
                (request.request_flags == flags.allow_command)):
                try:
                
                    sci_ptr.ptr.request_name = request.long_name
                    sci_ptr.ptr.args_string = args_string.strip()
                    request.rq_procedure(sci_ptr, sci_ptr.ptr.info_ptr)
            
                    post_request_proc = sci_ptr.ptr.procedures.get("post_request_line")
                    if post_request_proc:
                        post_request_proc(sci_ptr)
                    # end if
                    
                except ssu_abort_line:
                    pass
                # end try
                code.val = 1
                break
            # end if
        else:
            call. ioa_ ("Unrecognized request ^a", request_name)
            code.val = 0
            
    def print_message(self, sci_ptr, code, format_string="", *args):
        user_message = parm("")
        if format_string:
            call. ioa_.rsnnl (format_string, user_message, *args)
        call. ioa_ ("^/^a^[ (^a)^;^s^]: ^[^r ^;^s^]^a", sci_ptr.ptr.subsystem_name, sci_ptr.ptr.request_name != "", sci_ptr.ptr.request_name, code != 0, code, user_message.val)
    
    def abort_line(self, sci_ptr, code, format_string="", *args):
        self.print_message(sci_ptr, code, format_string, *args)
        raise ssu_abort_line
        
    def abort_subsystem(self, sci_ptr, code, format_string="", *args):
        if code != 0:
            self.print_message(sci_ptr, code, format_string, *args)
        sci_ptr.ptr.exit_code = code
        raise ssu_abort_line
        
#-- end class ssu_

class subsystem_control_info(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            subsystem_name = "",
            version_string = "",
            info_ptr       = None,
            request_table  = None,
            info_directory = "",
            prompt_mode    = bitstring(3, b'010'),
            prompt_string  = "",
            procedures     = {},
            request_name   = "",
            args_string    = "",
            exit_code      = -1,
        )
        