import datetime

from multics.globals import *

class sys_(SystemExecutable):
    def __init__(self, system_services):
        super(sys_, self).__init__(self.__class__.__name__, system_services)
        
    def get_default_search_paths(self):
        path_list = [
            ">sdd",
            ">sdd>commands",
            self.system.session_thread.session.homedir,
        ]
        return path_list
        
    def get_search_paths(self):
        return self.system.session_thread.session.process.search_paths
        
    def set_search_paths(self, path_list):
        self.system.session_thread.session.process.search_paths = path_list

    def get_users(self):
        return self.system.session_thread.login_db.session_blocks.keys()

    def get_current_directory(self):
        return self.system.session_thread.session.process.directory_stack[-1]
    
    def push_directory(self, dir_name):
        self.system.session_thread.session.process.directory_stack.append(dir_name)
        
    def pop_directory(self):
        if len(self.system.session_thread.session.process.directory_stack) > 1:
            return self.system.session_thread.session.process.directory_stack.pop()
        else:
            return None
        
    def accept_messages_(self, flag):
        self.system.session_thread.session.process.stack.accepting_messages = flag
        
    def send_message_(self, recipient, message):
        try:
            session_block = self.system.session_thread.login_db.session_blocks[recipient]
            process_mbx = call.hcs_.initiate(session_block.process_dir, "process_mbx")
            with MemoryMappedData(process_mbx):
                process_mbx.messages.append({'type':"user_message", 'from':self.system.session_thread.session.user_id, 'time':datetime.datetime.now(), 'text':message})
            # end with
            return 0
        except:
            return -1
            
    def recv_message_(self, message_packet):
        if self.system.session_thread.session.process.stack.accepting_messages:
            call.ioa_("Message from {0} on {1}: {2}", message_packet['from'], message_packet['time'].ctime(), message_packet['text'])
            