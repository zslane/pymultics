
from multics.globals import *

include. ssu_request_macros

class ssu_requests_(Subroutine):
    def __init__(self):
        super(ssu_requests_, self).__init__(self.__class__.__name__)

    def help(self, sci_ptr, info_ptr):
        pass
        
    def list_requests(self, sci_ptr, info_ptr):
        call.ioa_()
        for request in sci_ptr.ptr.request_table.table_entries:
            if ((request.request_flags & flags.allow_command) and
                (request.request_flags & flags.dont_list) == 0):
                call.ioa_("^a ^[(^a)^;^s^] ^25t^a", request.long_name, request.short_name != "", request.short_name, request.description)
        
    def summarize_requests(self, sci_ptr, info_ptr):
        count = 0
        call.ioa_()
        for request in sci_ptr.ptr.request_table.table_entries:
            if ((request.request_flags & flags.allow_command) and
                (request.request_flags & flags.dont_summarize) == 0):
                call.ioa_.nnl("^a ^[(^a)^]^25t", request.long_name, request.short_name != "", request.short_name)
                count += 1
                if count % 3 == 0:
                    call.ioa_()
        
    def execute(self, sci_ptr, info_ptr):
        call.do(sci_ptr.ptr.args_string)
        
#-- end class ssu_requests_
