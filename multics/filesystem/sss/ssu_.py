
from multics.globals import *

include. query_info
include. ssu_request_table

class ssu_(Subroutine):
    def __init__(self):
        super(ssu_, self).__init__(self.__class__.__name__)

    def create_invocation(self, subsystem_name, version_string, info_ptr, request_table_ptr, info_directory, sci_ptr, code):
        sci_ptr.ptr                = subsystem_control_info()
        sci_ptr.ptr.subsystem_name = subsystem_name
        sci_ptr.ptr.version_string = version_string
        sci_ptr.ptr.prompt_string  = subsystem_name
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
        
        query_info.version = query_info_version_5
        query_info.suppress_spacing = (sci_ptr.ptr.prompt_mode & bitstring(3, b'011') != 0)
        query_info.suppress_name_sw = (sci_ptr.ptr.prompt_mode & bitstring(3, b'011') != 0)
        
        while sci_ptr.ptr.exit_code == -1:
        
            call. ioa_.nnl (sci_ptr.ptr.prompt_string)
            call. command_query_ (query_info, command, sci_ptr.ptr.subsystem_name)
            
            pre_request_proc = sci_ptr.ptr.procedures.get("pre_request_line")
            if pre_request_proc:
                pre_request_proc(sci_ptr)
            # end if
            
            self.execute_string(sci_ptr, command.val, code)
            if code.val == 0:
                if command.val == "*":
                    sci_ptr.ptr.exit_code = 0
                # end if
            # end for
            
            post_request_proc = sci_ptr.ptr.procedures.get("post_request_line")
            if post_request_proc:
                post_request_proc(sci_ptr)
            # end if
        
    def destroy_invocation(self, sci_ptr):
        pass
        
    def get_info_ptr(self, sci_ptr):
        return sci_ptr.info_ptr
        
    def arg_count(self, sci_ptr, arg_count):
        arg_count.val = len(sci_ptr.arg_list)
        
    def arg_ptr(self, sci_ptr, arg_index, arg_ptr):
        try:
            arg_ptr.val = sci_ptr.arg_list[arg_index]
            code.val = 0
        except:
            arg_ptr.val = ""
            code.val = error_table_.noarg
            
    def execute_string(self, sci_ptr, command_string, code):
        command_string = command_string.strip()
        if command_string == "":
            code.val = 0
            return
        # end if
        
        arg_list = command_string.split()
        command_name = arg_list.pop(0)
        sci_ptr.ptr.arg_list = arg_list
        
        for request in sci_ptr.ptr.request_table.table_entries:
            if ((command_name == request.long_name or command_name == request.short_name) and
                (request.request_flags == flags.allow_command)):
                request.request_entry(sci_ptr, sci_ptr.ptr.info_ptr)
                code.val = 1
                break
            # end if
        else:
            code.val = 0
            
    def abort_line(self, sci_ptr, code, format_string, *args):
        call. ioa_ (format_string, *args)
        
    def abort_subsystem(self, sci_ptr, code):
        sci_ptr.ptr.exit_code = code
        
#-- end class ssu_

class subsystem_control_info(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            subsystem_name = "",
            version_string = "",
            info_ptr       = None,
            request_table  = None,
            info_directory = "",
            prompt_mode    = b'0',
            prompt_string  = "",
            procedures     = {},
            arg_list       = [],
            exit_code      = -1,
        )
        