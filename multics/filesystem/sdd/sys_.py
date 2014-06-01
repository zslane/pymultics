import datetime

from multics.globals import *

class sys_(SystemExecutable):
    def __init__(self, system_services):
        super(sys_, self).__init__(self.__class__.__name__, system_services)
        
    def get_default_search_paths(self, search_paths):
        path_list = [
            ">sdd",
            ">sdd>commands",
            self.system.session_thread.session.homedir,
        ]
        search_paths.list = path_list
        
    def get_search_paths(self, search_paths):
        search_paths.list = self.system.session_thread.session.process.search_paths
        
    def set_search_paths(self, path_list):
        self.system.session_thread.session.process.search_paths = path_list

    def get_users(self, users):
        users.list = self.system.session_thread.login_db.session_blocks.keys()

    def get_home_directory(self, home_dir):
        home_dir.name = self.system.session_thread.session.homedir
        
    def get_current_directory(self, current_dir):
        current_dir.name = self.system.session_thread.session.process.directory_stack[-1]
        
    def get_rel_directory(self, dir_ref, relative_to, out_dir, code):
        if relative_to == "":
            relative_to = self.system.session_thread.session.process.directory_stack[-1]
        # end if
        if dir_ref.startswith(">"):
            new_dir = dir_ref
        else:
            new_dir = self.system.hardware.filesystem.merge_path(relative_to, dir_ref)
        # end if
        native_path = self.system.hardware.filesystem.path2path(new_dir)
        if self.system.hardware.filesystem.file_exists(native_path):
            out_dir.name = new_dir
            code.val = 0
        else:
            code.val = error_table_.no_directory_entry
    
    def change_current_directory(self, dir_ref, code):
        if dir_ref.startswith(">"):
            self.push_directory(dir_ref)
            code.val = 0
        else:
            cur_dir = self.system.session_thread.session.process.directory_stack[-1]
            new_dir = self.system.hardware.filesystem.merge_path(cur_dir, dir_ref)
            native_path = self.system.hardware.filesystem.path2path(new_dir)
            if self.system.hardware.filesystem.file_exists(native_path):
                self.push_directory(new_dir)
                code.val = 0
            else:
                code.val = error_table_.no_directory_entry
    
    def push_directory(self, dir_name):
        self.system.session_thread.session.process.directory_stack.append(dir_name)
        
    def pop_directory(self, directory):
        if len(self.system.session_thread.session.process.directory_stack) > 1:
            directory.name = self.system.session_thread.session.process.directory_stack.pop()
        else:
            directory.name = None
        
    def accept_messages_(self, flag):
        self.system.session_thread.session.process.stack.accepting_messages = flag
        
    def send_message_(self, recipient, message, code):
        declare (segment = parm)
        try:
            session_block = self.system.session_thread.login_db.session_blocks[recipient]
            call.hcs_.initiate(session_block.process_dir, "process_mbx", segment)
            process_mbx = segment.ptr
            with process_mbx:
                process_mbx.messages.append({'type':"user_message", 'from':self.system.session_thread.session.user_id, 'time':datetime.datetime.now(), 'text':message})
            # end with
            code.val = 0
        except:
            code.val = -1
            
    def recv_message_(self, message_packet):
        if self.system.session_thread.session.process.stack.accepting_messages:
            call.ioa_("Message from {0} on {1}: {2}", message_packet['from'], message_packet['time'].ctime(), message_packet['text'])
            