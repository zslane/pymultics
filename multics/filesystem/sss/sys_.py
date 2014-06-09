
from multics.globals import *

class sys_(SystemExecutable):
    def __init__(self, system_services):
        super(sys_, self).__init__(self.__class__.__name__, system_services)
        
    def get_search_paths(self, search_paths):
        search_paths.list = self.system.session_thread.session.process.search_paths
        
    def set_search_paths(self, path_list):
        self.system.session_thread.session.process.search_paths = path_list

    def get_users(self, users):
        users.list = self.system.session_thread.whotab.session_blocks.keys()

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
        out_dir.name = new_dir
        
        if self.system.hardware.filesystem.file_exists(new_dir):
            code.val = 0
        else:
            code.val = error_table_.no_directory_entry
    
    def get_abs_path(self, name, output):
        if name.startswith(">"):
            output.path = self.system.hardware.filesystem._resolve_path(name)
            return
        # end if
        current_dir = self.system.session_thread.session.process.directory_stack[-1]
        output.path = self.system.hardware.filesystem.merge_path(current_dir, name)
    
    def split_path_(self, full_path, dir_name, entryname):
        rev_full_path = full_path[::-1]
        e, _, d = rev_full_path.partition(">")
        dir_name.val = d[::-1]
        entryname.val = e[::-1]
        
    def change_current_directory(self, dir_ref, code):
        if dir_ref.startswith(">"):
            self.push_directory(dir_ref)
            code.val = 0
        else:
            cur_dir = self.system.session_thread.session.process.directory_stack[-1]
            new_dir = self.system.hardware.filesystem.merge_path(cur_dir, dir_ref)
            if self.system.hardware.filesystem.file_exists(new_dir):
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

    def lock_process_mbx_(self, user_id, process_mbx_segment, code):
        try:
            session_block = self.system.session_thread.whotab.session_blocks[user_id]
        except KeyError:
            code.val = error_table_.no_such_user
            return
        # end try
        person_id, _, _ = user_id.partition(".")
        call.hcs_.initiate(session_block.process_dir, person_id + ".mbx", process_mbx_segment, code)
        if process_mbx_segment.ptr != null():
            call.set_lock_.lock(process_mbx_segment.ptr, 5, code)
        else:
            code.val = error_table_.lock_not_locked
            
    def unlock_process_mbx_(self, process_mbx_segment, code):
        call.set_lock_.unlock(process_mbx_segment, code)
    
    def accept_messages_(self, flag):
        self.system.session_thread.session.process.stack.accepting_messages = flag
        
    def recv_message_(self, message_packet):
        if self.system.session_thread.session.process.stack.accepting_messages:
            call.ioa_("Message from {0} on {1}: {2}", message_packet['from'], message_packet['time'].ctime(), message_packet['text'])
            