
from multics.globals import *

# call. ssu_.set_prompt_mode (scip, PROMPT_MODE)
# call. ssu_.set_prompt (scip, prompt_string)
# call. ssu_.set_procedure (scip, PRE_REQUEST_LINE, sst_.daemon, code)
# call. ssu_.set_procedure (scip, POST_REQUEST_LINE, sst_.daemon, code)
# call. ssu_.set_info_prefix (scip, INFO_PREFIX)
# call. ssu_.listen (scip, USER_INPUT_IOCB, code)
# call. ssu_.destroy_invocation (scip)

class ssu_(Subroutine):
    def __init__(self):
        super(ssu_, self).__init__(self.__class__.__name__)

    def create_invocation(self, subsystem_name, version_string, info_ptr, request_table_ptr, info_directory, sci_ptr, code):
        sci_ptr.ptr = subsystem_control()
        sci_ptr.ptr.subsystem_name = subsystem_name
        sci_ptr.ptr.version_string = version_string
        sci_ptr.ptr.info_ptr = info_ptr
        sci_ptr.ptr.request_table = request_table_ptr
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
        pass
        
    def destroy_invocation(self, sci_ptr):
        pass
        
    def arg_count(self, sci_ptr, arg_count):
        arg_count.val = len(sci_ptr.arg_list)
        
    def arg_ptr(self, sci_ptr, arg_index, arg_ptr):
        try:
            arg_ptr.val = sci_ptr.arg_list[arg_index]
            code.val = 0
        except:
            arg_ptr.val = ""
            code.val = error_table_.noarg
        
#-- end class ssu_

class subsystem_control(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            subsystem_name = "",
            version_string = "",
            info_ptr = None,
            request_table = None,
            info_directory = "",
            prompt_mode = b'0',
            prompt_string = "",
            procedures = {},
            arg_list = []
        )
        