
class begin_table(object):
    def __init__(self, request_table=[]):
        self.table_entries = request_table

class request(object):
    def __init__(self, long_name="", request_entry=None, short_name="", description="", request_flags=0):
        self.long_name     = long_name
        self.request_entry = request_entry
        self.short_name    = short_name
        self.description   = description
        self.request_flags = request_flags
        
class flags(object):

    unimplemented = 0
    allow_command = 1
    
