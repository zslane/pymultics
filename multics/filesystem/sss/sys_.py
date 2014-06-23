
from multics.globals import *

declare (get_wdir_ = entry . returns (char(168)))

class sys_(SystemExecutable):
    def __init__(self, system_services):
        super(sys_, self).__init__(self.__class__.__name__, system_services)
        
        self.__command_exit_code = 0
        
    def set_exit_code(self, code):
        self.__command_exit_code = code
        
    def get_exit_code(self, code):
        code.val = self.__command_exit_code
        
    def get_userid_long(self, short_name, long_name, code):
        short_person_id, _, short_project_id = short_name.partition(".")
        short_project_id = short_project_id or "*"
        long_person_id, long_project_id = short_person_id, short_project_id
        
        if short_person_id != "*":
            long_person_id = self.system.pnt.aliases.get(short_person_id) or short_person_id
            
            if not short_project_id:
                long_name.val = long_person_id
                code.val = 0
                return
            # end if
        # end if
        
        if short_project_id != "*":
            for pdt in self.system.pdt.values():
                if short_project_id == pdt.project_id or short_project_id == pdt.alias:
                        long_project_id = pdt.project_id
                        break
                    # end if
                # end if
            else:
                code.val = error_table_.no_such_user
                return
            # end for
        # end if
        
        long_name.val = long_person_id + "." + long_project_id
        code.val = 0
    
    def get_users(self, users, matching="*.*"):
        matching = matching.replace(".", r"\.").replace("*", r"(\w+)")
        users.list = filter(lambda k: re.match(matching, k), self.system.whotab.entries.keys())
        
    def get_daemons(self, daemons):
        daemons.list = [ process.uid() for process in self.system.get_daemon_processes() ]
        
    def get_daemon(self, which, daemon):
        for process in self.system.get_daemon_processes():
            if process.uid() == which:
                daemon.ptr = process
                return
            # end if
        # end for
        daemon.ptr = null()
        
    def get_process_ids(self, process_ids):
        process_ids.list = self.system.whotab.get_process_ids()
        
    def get_rel_directory(self, dir_ref, relative_to, out_dir, code):
        if relative_to == "":
            relative_to = get_wdir_()
        # end if
        if dir_ref.startswith(">"):
            new_dir = dir_ref
        else:
            new_dir = self.system.fs.merge_path(relative_to, dir_ref)
        # end if
        out_dir.name = new_dir
        
        if self.system.fs.file_exists(new_dir):
            code.val = 0
        else:
            code.val = error_table_.no_directory_entry
    
    def get_abs_path(self, name, output):
        if name.startswith(">"):
            output.path = self.system.fs._resolve_path(name)
            return
        # end if
        current_dir = get_wdir_()
        output.path = self.system.fs.merge_path(current_dir, name)
    
    def split_path_(self, full_path, dir_name, entryname):
        rev_full_path = full_path[::-1]
        e, _, d = rev_full_path.partition(">")
        dir_name.val = d[::-1]
        entryname.val = e[::-1]
        
    def change_current_directory(self, dir_ref, code):
        if dir_ref.startswith(">"):
            new_dir = dir_ref
        else:
            cur_dir = get_wdir_()
            new_dir = self.system.fs.merge_path(cur_dir, dir_ref)
        # end if
        if self.system.fs.file_exists(new_dir):
            self.push_directory(new_dir)
            code.val = 0
        else:
            code.val = error_table_.no_directory_entry
    
    def push_directory(self, dir_name):
        process = get_calling_process_()
        with process.rnt():
            process.directory_stack.append(dir_name)
        
    def pop_directory(self, directory):
        process = get_calling_process_()
        with process.rnt():
            if len(process.directory_stack) > 1:
                directory.name = process.directory_stack.pop()
            else:
                directory.name = None
    
    def add_process_msg(self, user_id, message, code):
        declare (segment = parm)
        try:
            call.sys_.lock_process_ms_(user_id, segment, code)
            if code.val == error_table_.locked_by_this_process:
                print "sys_.add_process_msg: {0} already has process.ms locked".format(get_calling_process_().objectName())
                #== Proceed with adding process message...
                
            elif code.val != 0:
                print "sys_.add_process_msg: Could not lock process.ms"
                print code.val
                return
            # end if
            
            msg_segment = segment.ptr
            with msg_segment:
                msg_segment.messages.append(message)
            # end with
        
        except:
            call.dump_traceback_()
            
        finally:
            call.sys_.unlock_process_ms_(segment.ptr, code)
            if code.val != 0:
                print "sys_.add_process_msg: Could not unlock process.ms"
                print code.val
            # end if
        # end try
    
    def lock_process_ms_(self, user_id, process_msg_segment, code):
        declare (daemon = parm)
        try:
            if user_id.endswith("SysDaemon"):
                self.get_daemon(user_id, daemon)
                process_dir = daemon.process.dir()
            else:
                whotab_entry = self.system.whotab.entries[user_id]
                process_dir = whotab_entry.process_dir
            # end if
        except:
            code.val = error_table_.no_such_user
            return
        # end try
        
        person_id, _, _ = user_id.partition(".")
        call.hcs_.initiate(process_dir, "process.ms", "", 0, 0, process_msg_segment, code)
        if process_msg_segment.ptr != null():
            call.set_lock_.lock(process_msg_segment.ptr, 5, code)
        else:
            code.val = error_table_.lock_not_locked
            
    def unlock_process_ms_(self, process_msg_segment, code):
        call.set_lock_.unlock(process_msg_segment, code)
    
    def lock_user_mbx_(self, user_id, mailbox_segment, code):
        declare (pit = parm)
        try:
            whotab_entry = self.system.whotab.entries[user_id]
            call.hcs_.initiate(whotab_entry.process_dir, "pit", "", 0, 0, pit, code)
            if code.val != 0:
                return
            # end if
            homedir = pit.data.homedir
        except:
            code.val = error_table_.no_such_user
            return
        # end try
        
        person_id, _, _ = user_id.partition(".")
        call.hcs_.initiate(homedir, person_id + ".mbx", "", 0, 0, mailbox_segment, code)
        if mailbox_segment.ptr != null():
            call.set_lock_.lock(mailbox_segment.ptr, 5, code)
        else:
            code.val = error_table_.lock_not_locked
            
    def unlock_user_mbx_(self, mailbox_segment, code):
        call.set_lock_.unlock(mailbox_segment, code)
    
    def accept_messages_(self, flag):
        process = get_calling_process_()
        process.stack.accepting_messages = flag
        
    def recv_message_(self, message_packet):
        process = get_calling_process_()
        process.stack.assert_create("accepting_messages", bool)
        if process.stack.accepting_messages or message_packet['type'] == "shutdown_announcement":
            call.ioa_("Message from {0} on {1}: {2}", message_packet['from'], message_packet['time'].ctime(), message_packet['text'])
        else:
            # STORE IN MAILBOX SOME DAY
            pass
            
    def signal_condition(self, signalling_process, condition_instance):
        self.system.signal_condition(signalling_process, condition_instance)
        
    def signal_shutdown(self):
        if not self.system.shutting_down():
            self.system.shutdown()
        
    def start_shutdown(self, how_long, message):
        self.system.start_shutdown(how_long, message)
        
    def cancel_shutdown(self):
        self.system.cancel_shutdown()
        