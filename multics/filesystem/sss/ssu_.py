
from multics.globals import *

class ssu_(Subroutine):
    def __init__(self):
        super(ssu_, self).__init__(self.__class__.__name__)

    def create_invocation(self, subsystem_name, version_string, info_ptr, request_table_ptr, info_directory, sci_ptr, code):
        call. ioa_ ("^a ^a", subsystem_name, version_string)
        call. ioa_ ("^r", info_ptr)
        call. ioa_ ("^r", request_table_ptr)
        call. ioa_ ("^a", info_directory)
        