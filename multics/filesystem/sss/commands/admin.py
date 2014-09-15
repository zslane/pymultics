
from multics.globals import *

include.sat
include.query_info

admin_usage_text = (
"""Available commands are:
    list_users, lu
    add_user, au
    delete_user, du
    rename_user, ru
    refresh_sat, rs
    list_projects, lp
    list_project_admins, lpa
    add_project_admin, apa,
    delete_project_admin, dpa,
    quit, q
    help, ?"""
    )
    
au_usage_text = (
"""Usage: add_user [person_id] {{options}}
    options: -alias|-a [alias]
             -default_project|-dp [project_id]
             -set_password|-sp {{codeword}}"""
             )

MAIN = "admin"

def admin():
    command  = char('*') . parm . init("")
    person   = char(21) . parm . init("")
    project  = char(9) . parm . init("")
    acct     = char(9) . parm . init("")
    arg_list = ptr . init(null())
    code     = fixed.bin(35) . parm . init(0)
    
    call. user_info_.whoami (person, project, acct)
    if project.val != "SysAdmin":
        call. ioa_ ("You are not authorized to use the ^a command", MAIN)
        return
    # end if
    
    while command.val != "quit" and command.val != "q":
        query_info.suppress_name_sw = False
        query_info.yes_or_no_sw = False
        query_info.explanation_ptr = admin_usage_text
        call. command_query_ (query_info, command, MAIN)
        if command.val:
            call. cu_.set_command_string_ (command.val)
            call. cu_.get_command_name (command, code)
            if command.val == "list_users" or command.val == "lu":
                list_users()
            elif command.val == "add_user" or command.val == "au":
                add_user()
            elif command.val == "delete_user" or command.val == "du":
                delete_user()
            elif command.val == "rename_user" or command.val == "ru":
                rename_user()
            elif command.val == "refresh_sat" or command.val == "rs":
                refresh_sat()
            elif command.val == "list_projects" or command.val == "lp":
                list_projects()
            elif command.val == "list_project_admins" or command.val == "lpa":
                list_project_admins()
            elif command.val == "add_project_admin" or command.val == "apa":
                add_project_admin()
            elif command.val == "delete_project_admin" or command.val == "dpa":
                delete_project_admin()
            elif command.val == "help": # '?' handled by command_query_
                call. ioa_ (admin_usage_text)
            elif command.val != "quit" and command.val != "q":
                call. ioa_ ("Unrecgonized ^a command", MAIN)
                call. ioa_ (admin_usage_text)
    
@system_privileged
def list_users():
    person_name_table = ptr . init(null())
    arg_list          = ptr . init(null())
    code              = fixed.bin(35) . parm . init(0)
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "PNT.pnt", "", 0, 0, person_name_table, code)
    if person_name_table.ptr:
        call. ioa_ ("Person Id              Alias     D Project Password?")
        call. ioa_ ("---------------------- --------- --------- ---------")
        for person_id in person_name_table.ptr.name_entries:
            call. ioa_ ("^22a ^9a ^9a ^[Yes^;No^]", person_id,
                person_name_table.ptr.name_entries[person_id].alias,
                person_name_table.ptr.name_entries[person_id].default_project_id,
                person_name_table.ptr.name_entries[person_id].encrypted_password != "")
        call. ioa_ ("^d total entries:", len(person_name_table.ptr.name_entries))
    
@system_privileged
def add_user():
    project_definition_table = parm()
    person_name_table  = ptr . init(null())
    arg_list           = ptr . init(null())
    code               = fixed.bin(35) . parm . init(0)
    
    alias              = char(8) . init("") . local
    default_project_id = char(9) . init("") . local
    encrypted_password = char('*') . init("") . local
    setting_password   = bit(1) . init(b'0') . local
    pubkey             = None
    
    def show_usage():
        call. ioa_ (au_usage_text)
    
    call. cu_.arg_list (arg_list)
    if len(arg_list.args) == 0:
        show_usage()
        return
        
    person_id = arg_list.args.pop(0)
    if not person_id:
        show_usage()
        return
    
    i = 0
    while i < len(arg_list.args):
        arg = arg_list.args[i]
        if arg == "-alias" or arg == "-a":
            i += 1
            if i < len(arg_list.args):
                alias = arg_list.args[i]
                i += 1
            else:
                show_usage()
                return
            # end if
        elif arg == "-default_project" or arg == "-dp":
            i += 1
            if i < len(arg_list.args):
                default_project_id = arg_list.args[i]
                i += 1
            else:
                show_usage()
                return
            # end if
        elif arg == "-set_password" or arg == "-sp":
            setting_password = b'1'
            i += 1
            if (i < len(arg_list.args)) and (not arg_list.args[i].startswith("-")):
                password = arg_list.args[i]
                i += 1
            else:
                password = ""
            # end if
            encrypted_password, pubkey = supervisor.encrypt_password(password)
        else:
            call. com_err_ (error_table_.badarg, MAIN, "^a", arg)
            return
        # end if
    # end while
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "PNT.pnt", "", 0, 0, person_name_table, code)
    if person_name_table.ptr:
        if person_id in person_name_table.ptr.alias_list():
            person_id = person_name_table.ptr.resolve_alias(person_id)
        # end if
        if person_id in person_name_table.ptr.person_id_list():
            name_entry         = person_name_table.ptr.name_entries[person_id]
            alias              = alias or name_entry.alias
            default_project_id = default_project_id or name_entry.default_project_id
            encrypted_password = encrypted_password if setting_password else name_entry.encrypted_password
            pubkey             = pubkey if setting_password else name_entry.password_pubkey
        elif not pubkey:
            #== If we're adding a new user with a blank initial password then generate a pubkey for that
            encrypted_password, pubkey = supervisor.encrypt_password("")
        # end if
        #== Prevent duplicating aliases
        if alias and person_name_table.ptr.resolve_alias(alias) not in [person_id, ""]:
            call. ioa_ ("Alias '^a' already assigned to user ^a", alias, person_name_table.ptr.resolve_alias(alias))
            return
        # end if
        with person_name_table.ptr:
            person_name_table.ptr.add_person(person_id, alias, default_project_id, encrypted_password, pubkey)
        # end with
    # end if
    
@system_privileged
def delete_user():
    person_name_table = ptr . init(null())
    arg_list          = ptr . init(null())
    code              = fixed.bin(35) . parm . init(0)
    answer            = char('*') . parm . init("")
    
    call. cu_.arg_list (arg_list)
    if len(arg_list.args) == 0:
        call.ioa_("Usage: du [person_id]")
        return
        
    person_id = arg_list.args.pop(0)
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "PNT.pnt", "", 0, 0, person_name_table, code)
    if person_name_table.ptr:
        if person_id in person_name_table.ptr.alias_list():
            person_id = person_name_table.ptr.resolve_alias(person_id)
        # end if
        if person_id in person_name_table.ptr.person_id_list():
            query_info.suppress_name_sw = True
            query_info.yes_or_no_sw = True
            query_info.explanation_ptr = "You are about to delete {0} as a user from the system. Continue (yes/no)?".format(person_id)
            call. command_query_ (query_info, answer, MAIN, query_info.explanation_ptr)
            if answer.string.lower() in ["yes", "y"]:
                with person_name_table.ptr:
                    person_name_table.ptr.del_person(person_id)
                # end with
            # end if
        else:
            call. ioa_ ("No such user ^a", person_id)
    
@system_privileged
def rename_user():
    person_name_table = ptr . init(null())
    arg_list          = ptr . init(null())
    code              = fixed.bin(35) . parm . init(0)
    
    call. cu_.arg_list (arg_list)
    if len(arg_list.args) < 2:
        call.ioa_("Usage: ru [old person_id] [new person_id]")
        return
        
    old_person_id = arg_list.args.pop(0)
    new_person_id = arg_list.args.pop(0)
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "PNT.pnt", "", 0, 0, person_name_table, code)
    if person_name_table.ptr:
        if old_person_id in person_name_table.ptr.person_id_list():
            person_name_entry = person_name_table.ptr.name_entries[old_person_id]
            with person_name_table.ptr:
                person_name_table.ptr.add_person(new_person_id,
                                                 person_name_entry.alias,
                                                 person_name_entry.default_project_id,
                                                 person_name_entry.encrypted_password,
                                                 person_name_entry.password_pubkey)
                person_name_table.ptr.del_person(old_person_id)
            # end with
        else:
            call. ioa_ ("No such user ^a", old_person_id)
            
@system_privileged
def refresh_sat():
    sys_admin_table = ptr . init(null()) # structure
    arg_list        = ptr . init(null()) # list
    branch          = ptr . init(null()) # list
    segment         = ptr . init(null()) # list
    code            = fixed.bin(35) . parm . init(0)
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "system_administrator_table", "", 0, 0, sys_admin_table, code)
    if sys_admin_table.ptr != null():
        call. hcs_.delentry_seg (sys_admin_table.ptr, code)
    # end if
    call. hcs_.make_seg (supervisor.fs.system_control_dir, "system_administrator_table", "", 0, sys_admin_table(SystemAdministratorTable()), code)
    
    call. hcs_.get_directory_contents (supervisor.fs.system_control_dir, branch, segment, code)
    if code.val == 0:
        segment_list = segment.list
        with sys_admin_table.ptr:
            for segment_name in segment_list:
                if segment_name.endswith(".pdt"):
                    call. hcs_.initiate (supervisor.fs.system_control_dir, segment_name, "", 0, 0, segment, code)
                    sys_admin_table.ptr.add_project(segment.ptr.project_id, segment.ptr._filepath(), segment.ptr.alias)
                    sys_admin_table.ptr.add_admin(segment.ptr.project_id, "JRCooper")
                # end if
            # end for
        # end with
        print sys_admin_table.ptr.projects
    # end if

@system_privileged
def list_projects():
    sys_admin_table = ptr . init(null())
    arg_list        = ptr . init(null())
    code            = fixed.bin(35) . parm . init(0)
    
    call. cu_.arg_list (arg_list)
    if len(arg_list.args) != 0:
        call. ioa_ ("list_projects takes no arguments")
        return
    # end if
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "system_administrator_table", "", 0, 0, sys_admin_table, code)
    if sys_admin_table.ptr == null():
        call. ioa_ ("No system_administrator_table found")
        return
    # end if
    
    # print sys_admin_table.ptr.projects
    for project_id in sys_admin_table.ptr.projects:
        alias = sys_admin_table.ptr.projects[project_id]['alias']
        call. ioa_ ("  ^a ^[(^a)^]", project_id, alias != "", alias)

@system_privileged
def list_project_admins():
    sys_admin_table = ptr . init(null())
    arg_list        = ptr . init(null())
    code            = fixed.bin(35) . parm . init(0)
             
    call. cu_.arg_list (arg_list)
    if len(arg_list.args) != 1:
        call. ioa_ ("Usage: list_project_admins|lpa [project_id]")
        return
    # end if
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "system_administrator_table", "", 0, 0, sys_admin_table, code)
    if sys_admin_table.ptr == null():
        call. ioa_ ("No system_administrator_table found")
        return
    # end if
    
    project_id = arg_list.args.pop(0)
    
    if project_id not in sys_admin_table.ptr.projects:
        call. ioa_ ("^a not found in the system_administrator_table", project_id)
        return
    # end if
    
    for admin in sys_admin_table.ptr.get_admins(project_id):
        call. ioa_ ("  ^a", admin)
    
@system_privileged
def add_project_admin():
    sys_admin_table = ptr . init(null())
    arg_list        = ptr . init(null())
    code            = fixed.bin(35) . parm . init(0)
             
    call. cu_.arg_list (arg_list)
    if len(arg_list.args) != 2:
        call. ioa_ ("Usage: add_project_admin|apa [project_id] [person_id]")
        return
    # end if
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "system_administrator_table", "", 0, 0, sys_admin_table, code)
    if sys_admin_table.ptr == null():
        call. ioa_ ("No system_administrator_table found")
        return
    # end if
    
    project_id = arg_list.args.pop(0)
    person_id = arg_list.args.pop(0)
    
    if project_id not in sys_admin_table.ptr.projects:
        call. ioa_ ("^a not found in the system_administrator_table", project_id)
        return
    # end if
    
    if person_id not in sys_admin_table.ptr.get_admins(project_id):
        with sys_admin_table.ptr:
            sys_admin_table.ptr.add_admin(project_id, person_id)
    
@system_privileged
def delete_project_admin():
    sys_admin_table = ptr . init(null())
    arg_list        = ptr . init(null())
    code            = fixed.bin(35) . parm . init(0)
    
    call. cu_.arg_list (arg_list)
    if len(arg_list.args) != 2:
        call. ioa_ ("Usage: delete_project_admin|dpa [project_id] [person_id]")
        return
    # end if
    
    call. hcs_.initiate (supervisor.fs.system_control_dir, "system_administrator_table", "", 0, 0, sys_admin_table, code)
    if sys_admin_table.ptr == null():
        call. ioa_ ("No system_administrator_table found")
        return
    # end if
    
    project_id = arg_list.args.pop(0)
    person_id = arg_list.args.pop(0)
    
    if project_id not in sys_admin_table.ptr.projects:
        call. ioa_ ("^a not found in the system_administrator_table", project_id)
        return
    # end if
    
    if person_id in sys_admin_table.ptr.get_admins(project_id):
        with sys_admin_table.ptr:
            sys_admin_table.ptr.remove_admin(project_id, person_id)
        # end with
    else:
        call. ioa_ ("^a not a ^a project administrator", person_id, project_id)
    