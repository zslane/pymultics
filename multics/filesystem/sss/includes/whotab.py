
class WhoTable(object):

    def __init__(self):
        self.sysid = ""
        self.entries = {}
        
    def __repr__(self):
        return "{0}: {1}".format(self.sysid, self.entries)
        
    def get_process_ids(self):
        return [ whotab_entry.process_id for whotab_entry in self.entries.values() ]
        
class WhotabEntry(object):

    def __init__(self, login_time, process_id, process_dir):
        super(WhotabEntry, self).__init__()
        
        self.login_time = login_time
        self.process_id = process_id
        self.process_dir = process_dir
        
    def __repr__(self):
        return "<%s.%s login_time: %s, process_id: %s, process_dir: %s>" % (__name__, self.__class__.__name__, self.login_time.ctime() if self.login_time else None, self.process_id, self.process_dir)
