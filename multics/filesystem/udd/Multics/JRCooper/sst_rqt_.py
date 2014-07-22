
from multics.globals import *
        
class subsystem_request_table(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            table_entries = {},
        )

class request(PL1.Structure):
    def __init__(self, long_name, request_entry, short_name, description, request_flags):
        PL1.Structure.__init__(self,
            long_name = long_name,
            request_entry = request_entry,
            short_name = short_name,
            description = description,
            request_flags = request_flags,
        )
        
class flags(object):

    allow_command = 1
    
include. sst_

class sst_rqt_(Subroutine):

    sst_rqt_ = subsystem_request_table()
    
    def __init__(self):
        super(sst_rqt_, self).__init__(self.__class__.__name__)
        
        sst_rqt_.sst_rqt_.table_entries = {
        
            'scanner': request('scanner', sst_.scanner, "sc", "Scanner readout.", flags.allow_command),
            
        }