
from multics.globals import *

declare (get_wdir_ = entry . returns (char(168)))

class sys_(Subroutine):
    def __init__(self):
        super(sys_, self).__init__(self.__class__.__name__)
        
    def set_exit_code(self, code):
        process = get_calling_process_()
        process.stack.command_exit_code = code
        
    def get_exit_code(self, code):
        process = get_calling_process_()
        process.stack.assert_create("command_exit_code", int)
        code.val = process.stack.command_exit_code
        
    def get_userid_long(self, short_name, long_name, code):
        short_person_id, _, short_project_id = short_name.partition(".")
        short_project_id = short_project_id or "*"
        long_person_id, long_project_id = short_person_id, short_project_id
        
        if short_person_id != "*":
            long_person_id = GlobalEnvironment.supervisor.pnt.aliases.get(short_person_id) or short_person_id
            if long_person_id not in GlobalEnvironment.supervisor.pnt.name_entries:
                code.val = error_table_.no_such_user
                return
            # end if
        # end if
        
        if short_project_id != "*":
            for pdt in GlobalEnvironment.supervisor.pdt.values():
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
    
    def default_home_dir(self, person_id, project_id):
        return ">".join([GlobalEnvironment.fs.user_dir_dir, project_id, person_id])
    #-- end def default_home_dir
    
    def get_user_homedir_(self, user_id, homedir):
        person_id, project_id = user_id.split(".")
        for pdt in GlobalEnvironment.supervisor.pdt.values():
            if project_id == pdt.project_id:
                for person in pdt.users:
                    if person == person_id:
                        homedir.val = pdt.users[person].home_dir or self.default_home_dir(person_id, project_id)
    
    def get_registered_users(self, user_ids, homedirs, matching="*.*"):
        user_ids.list = []
        homedirs.list = []
        matching = matching.replace(".", r"\.").replace("*", r"(\w+)")
        for project_key in GlobalEnvironment.supervisor.pdt:
            pdt = GlobalEnvironment.supervisor.pdt[project_key]
            #== Skip entries which are just alias copies of the actual project entries
            if project_key == pdt.alias:
                continue
            # end if
            project_id = pdt.project_id
            for person_id in pdt.users:
                user_id = person_id + "." + project_id
                homedir = pdt.users[person_id].home_dir or self.default_home_dir(person_id, project_id)
                if re.match(matching, user_id):
                    user_ids.list.append(user_id)
                    homedirs.list.append(homedir)
    
    def get_current_users(self, users, matching="*.*"):
        matching = matching.replace(".", r"\.").replace("*", r"(\w+)")
        users.list = filter(lambda k: re.match(matching, k), GlobalEnvironment.supervisor.whotab.entries.keys())
        
    def get_daemons(self, daemons):
        daemons.list = [ process.uid() for process in GlobalEnvironment.supervisor.get_daemon_processes() ]
        
    def get_daemon(self, which, daemon):
        for process in GlobalEnvironment.supervisor.get_daemon_processes():
            if process.uid() == which:
                daemon.ptr = process
                return
            # end if
        # end for
        daemon.ptr = null()
        
    def get_process_ids(self, process_ids):
        process_ids.list = GlobalEnvironment.supervisor.whotab.get_process_ids()
        
    def get_rel_directory(self, dir_ref, relative_to, out_dir, code):
        if relative_to == "":
            relative_to = get_wdir_()
        # end if
        if dir_ref.startswith(">"):
            new_dir = dir_ref
        else:
            new_dir = GlobalEnvironment.fs.merge_path(relative_to, dir_ref)
        # end if
        out_dir.name = new_dir
        
        if GlobalEnvironment.fs.file_exists(new_dir):
            code.val = 0
        else:
            code.val = error_table_.no_directory_entry
    
    def get_abs_path(self, name, output):
        if name.startswith(">"):
            output.path = GlobalEnvironment.fs._resolve_path(name)
            return
        # end if
        current_dir = get_wdir_()
        output.path = GlobalEnvironment.fs.merge_path(current_dir, name)
    
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
            new_dir = GlobalEnvironment.fs.merge_path(cur_dir, dir_ref)
        # end if
        if GlobalEnvironment.fs.file_exists(new_dir):
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
        segment = parm()
        try:
            call.sys_.lock_process_ms_(user_id, segment, code)
            if code.val == error_table_.locked_by_this_process:
                print "sys_.add_process_msg: {0} already has process.ms locked".format(get_calling_process_().objectName())
                #== Proceed with adding process message...
                
            elif code.val != 0:
                print "sys_.add_process_msg: Could not lock process.ms for {0}".format(user_id)
                print code.val
                return
            # end if
            
            msg_segment = segment.ptr
            with msg_segment:
                msg_segment.messages.append(message)
            # end with
        
            call.sys_.unlock_process_ms_(segment.ptr, code)
            if code.val != 0:
                print "sys_.add_process_msg: Could not unlock process.ms"
                print code.val
            # end if
            
        except:
            call.dump_traceback_()
        # end try
    
    def lock_process_ms_(self, user_id, process_msg_segment, code):
        daemon = parm()
        try:
            if user_id.endswith("SysDaemon"):
                self.get_daemon(user_id, daemon)
                process_dir = daemon.process.dir()
            else:
                whotab_entry = GlobalEnvironment.supervisor.whotab.entries[user_id]
                process_dir = whotab_entry.process_dir
            # end if
        except:
            code.val = error_table_.no_such_user
            return
        # end try
        
        person_id, _, _ = user_id.partition(".")
        call.hcs_.initiate(process_dir, "process.ms", "", 0, 0, process_msg_segment, code)
        if process_msg_segment.ptr != null():
            call.set_lock_.lock(process_msg_segment.ptr.lock_word(), 5, code)
        else:
            code.val = error_table_.lock_not_locked
            
    def unlock_process_ms_(self, process_msg_segment, code):
        call.set_lock_.unlock(process_msg_segment.lock_word(), code)
    
    def _initiate_user_mbx(self, user_id, homedir, mailbox_segment, code):
        #== If no homedir is provided, then try to figure it out
        if not homedir:
            hd = parm()
            self.get_user_homedir_(user_id, hd)
            if not hd.val:
                code.val = error_table_.no_such_user
                return
            else:
                homedir = hd.val
            # end if
        # end if
        
        person_id, _, _ = user_id.partition(".")
        call.hcs_.initiate(homedir, person_id + ".mbx", "", 0, 0, mailbox_segment, code)
        
    def lock_user_mbx_(self, user_id, homedir, mailbox_segment, code):
        self._initiate_user_mbx(user_id, homedir, mailbox_segment, code)
        if mailbox_segment.ptr != null():
            call.set_lock_.lock(mailbox_segment.ptr.lock_word(), 5, code)
            
    def unlock_user_mbx_(self, mailbox_segment, code):
        call.set_lock_.unlock(mailbox_segment.lock_word(), code)
    
    def accept_messages_(self, flag):
        process = get_calling_process_()
        process.stack.accepting_messages = flag
        
    def messages_accepted_(self, flag):
        process = get_calling_process_()
        process.stack.assert_create("accepting_messages", bool)
        flag.val = process.stack.accepting_messages
        
    def hold_messages_(self, flag):
        process = get_calling_process_()
        process.stack.holding_messages = flag
        
    def messages_held_(self, flag):
        process = get_calling_process_()
        process.stack.assert_create("holding_messages", bool)
        flag.val = process.stack.holding_messages
    
    def recv_message_(self, message_packet):
        process = get_calling_process_()
        process.stack.assert_create("accepting_messages", bool)
        if process.stack.accepting_messages or message_packet['type'] == "shutdown_announcement":
            call.ioa_("From ^a ^a: ^a", message_packet['from'], message_packet['time'].ctime(), message_packet['text'])
        
    def signal_condition(self, signalling_process, condition_instance):
        GlobalEnvironment.supervisor.signal_condition(signalling_process, condition_instance)
        
    def register_condition_handler(self, condition, handler):
        GlobalEnvironment.supervisor.register_condition_handler(condition, handler)
        
    def deregister_condition_handler(self, condition):
        GlobalEnvironment.supervisor.deregister_condition_handler(condition)
        
    def start_shutdown(self, how_long, message):
        GlobalEnvironment.supervisor.start_shutdown(how_long, message)
        
    def cancel_shutdown(self):
        GlobalEnvironment.supervisor.cancel_shutdown()
        