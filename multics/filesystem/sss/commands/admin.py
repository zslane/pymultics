
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
    declare (command  = parm . init (""),
             person   = parm,
             project  = parm,
             acct     = parm,
             arg_list = parm,
             code     = parm)
    
    call.user_info_.whoami(person, project, acct)
    if project.id != "SysAdmin":
        call.ioa_("You are not authorized to use the {0} command", MAIN)
        return
    # end if
    
    while command.string != "quit" and command.string != "q":
        query_info.suppress_name_sw = False
        query_info.yes_or_no_sw = False
        query_info.explanation_ptr = admin_usage_text
        call.command_query_(query_info, command, MAIN)
        if command.line:
            call.cu_.set_command_string_(command.line)
            call.cu_.get_command_name(command, code)
            if command.name == "list_users" or command.name == "lu":
                list_users()
            elif command.name == "add_user" or command.name == "au":
                add_user()
            elif command.name == "delete_user" or command.name == "du":
                delete_user()
            elif command.name == "rename_user" or command.name == "ru":
                rename_user()
            elif command.name == "refresh_sat" or command.name == "rs":
                refresh_sat()
            elif command.name == "list_projects" or command.name == "lp":
                list_projects()
            elif command.name == "list_project_admins" or command.name == "lpa":
                list_project_admins()
            elif command.name == "add_project_admin" or command.name == "apa":
                add_project_admin()
            elif command.name == "delete_project_admin" or command.name == "dpa":
                delete_project_admin()
            elif command.name == "help": # '?' handled by command_query_
                call.ioa_(admin_usage_text)
            elif command.name != "quit" and command.name != "q":
                call.ioa_("Unrecgonized {0} command", MAIN)
                call.ioa_(admin_usage_text)
    
@system_privileged
def list_users():
    declare (arg_list          = parm,
             person_name_table = parm,
             code              = parm)

    call.hcs_.initiate(system.fs.system_control_dir, "person_name_table", person_name_table, code)
    if person_name_table.ptr:
        call.ioa_("Person Id              Alias     D Project Password?")
        call.ioa_("---------------------- --------- --------- ---------")
        for person_id in person_name_table.ptr.name_entries:
            call.ioa_("{0:22} {1:9} {2:9} {3}", person_id,
                person_name_table.ptr.name_entries[person_id].alias,
                person_name_table.ptr.name_entries[person_id].default_project_id,
                "Yes" if person_name_table.ptr.name_entries[person_id].encrypted_password else "No")
        call.ioa_("{0} total entries:", len(person_name_table.ptr.name_entries))
    
@system_privileged
def add_user():
    declare (arg_list          = parm,
             person_name_table = parm,
             project_definition_table = parm,
             code              = parm)
    
    alias = ""
    default_project_id = ""
    encrypted_password = ""
    pubkey = None
    setting_password = False

    def show_usage():
        call.ioa_(au_usage_text)
    
    call.cu_.arg_list(arg_list)
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
            setting_password = True
            i += 1
            if (i < len(arg_list.args)) and (not arg_list.args[i].startswith("-")):
                password = arg_list.args[i]
                i += 1
            else:
                password = ""
            # end if
            encrypted_password, pubkey = system.encrypt_password(password)
        else:
            call.ioa_("Unrecognized argument {0}", arg)
            return
        # end if
    # end while
    
    call.hcs_.initiate(system.fs.system_control_dir, "person_name_table", person_name_table, code)
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
        # end if
        with person_name_table.ptr:
            person_name_table.ptr.add_person(person_id, alias, default_project_id, encrypted_password, pubkey)
        # end with
    # end if
            
@system_privileged
def delete_user():
    declare (arg_list          = parm,
             answer            = parm,
             person_name_table = parm,
             code              = parm)
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        call.ioa_("Usage: du [person_id]")
        return
        
    person_id = arg_list.args.pop(0)
    
    call.hcs_.initiate(system.fs.system_control_dir, "person_name_table", person_name_table, code)
    if person_name_table.ptr:
        if person_id in person_name_table.ptr.alias_list():
            person_id = person_name_table.ptr.resolve_alias(person_id)
        # end if
        if person_id in person_name_table.ptr.person_id_list():
            query_info.suppress_name_sw = True
            query_info.yes_or_no_sw = True
            query_info.explanation_ptr = "You are about to delete {0} as a user from the system. Continue (yes/no)?".format(person_id)
            call.command_query_(query_info, answer, MAIN, query_info.explanation_ptr)
            if answer.string.lower() in ["yes", "y"]:
                with person_name_table.ptr:
                    person_name_table.ptr.del_person(person_id)
                # end with
            # end if
        else:
            call.ioa_("No such user {0}", person_id)
    
@system_privileged
def rename_user():
    declare (arg_list          = parm,
             person_name_table = parm,
             code              = parm)
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) < 2:
        call.ioa_("Usage: ru [old person_id] [new person_id]")
        return
        
    old_person_id = arg_list.args.pop(0)
    new_person_id = arg_list.args.pop(0)
    
    call.hcs_.initiate(system.fs.system_control_dir, "person_name_table", person_name_table, code)
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
            call.ioa_("No such user {0}", old_person_id)
            
@system_privileged
def refresh_sat():
    declare (sys_admin_table = parm,
             branch          = parm,
             segment         = parm,
             code            = parm)
             
    call.hcs_.initiate(system.fs.system_control_dir, "system_administrator_table", sys_admin_table, code)
    if sys_admin_table.ptr != null():
        call.hcs_.delentry_seg(sys_admin_table.ptr, code)
    # end if
    call.hcs_.make_seg(system.fs.system_control_dir, "system_administrator_table", sys_admin_table(SystemAdministratorTable()), code)
    
    tables = {}
    
    call.hcs_.get_directory_contents(system.fs.system_control_dir, branch, segment, code)
    if code.val == 0:
        segment_list = segment.list
        with sys_admin_table.ptr:
            for segment_name in segment_list:
                if segment_name.endswith(".pdt"):
                    call.hcs_.initiate(system.fs.system_control_dir, segment_name, segment, code)
                    sys_admin_table.ptr.add_project(segment.ptr.project_id, segment.ptr.filepath, segment.ptr.alias)
                    sys_admin_table.ptr.add_admin(segment.ptr.project_id, "JRCooper")
                # end if
            # end for
        # end with
        print sys_admin_table.ptr.projects
    # end if

@system_privileged
def list_projects():
    declare (sys_admin_table = parm,
             code            = parm)
             
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 0:
        call.ioa_("list_projects takes no arguments")
        return
    # end if
    
    call.hcs_.initiate(system.fs.system_control_dir, "system_administrator_table", sys_admin_table, code)
    if sys_admin_table.ptr == null():
        call.ioa_("No system_administrator_table found")
        return
    # end if
    
    print sys_admin_table.ptr.projects
    for project_id in sys_admin_table.ptr.projects:
        alias = sys_admin_table.ptr.projects[project_id]['alias']
        call.ioa_("  {0} {1}", project_id, "(%s)" % alias if alias else "")

@system_privileged
def list_project_admins():
    declare (sys_admin_table = parm,
             code            = parm)
             
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 1:
        call.ioa_("Usage: list_project_admins|lpa [project_id]")
        return
    # end if
    
    call.hcs_.initiate(system.fs.system_control_dir, "system_administrator_table", sys_admin_table, code)
    if sys_admin_table.ptr == null():
        call.ioa_("No system_administrator_table found")
        return
    # end if
    
    project_id = arg_list.args.pop(0)
    
    if project_id not in sys_admin_table.ptr.projects:
        call.ioa_("{0} not found in the system_administrator_table", project_id)
        return
    # end if
    
    for admin in sys_admin_table.ptr.get_admins(project_id):
        call.ioa_("  {0}", admin)
    
@system_privileged
def add_project_admin():
    declare (sys_admin_table = parm,
             arg_list        = parm,
             code            = parm)
             
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 2:
        call.ioa_("Usage: add_project_admin|apa [project_id] [person_id]")
        return
    # end if
    
    call.hcs_.initiate(system.fs.system_control_dir, "system_administrator_table", sys_admin_table, code)
    if sys_admin_table.ptr == null():
        call.ioa_("No system_administrator_table found")
        return
    # end if
    
    project_id = arg_list.args.pop(0)
    person_id = arg_list.args.pop(0)
    
    if project_id not in sys_admin_table.ptr.projects:
        call.ioa_("{0} not found in the system_administrator_table", project_id)
        return
    # end if
    
    with sys_admin_table.ptr:
        if person_id not in sys_admin_table.ptr.get_admins(project_id):
            sys_admin_table.ptr.add_admin(project_id, person_id)
    
@system_privileged
def delete_project_admin():
    declare (sys_admin_table = parm,
             arg_list        = parm,
             code            = parm)
             
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) != 2:
        call.ioa_("Usage: delete_project_admin|dpa [project_id] [person_id]")
        return
    # end if
    
    call.hcs_.initiate(system.fs.system_control_dir, "system_administrator_table", sys_admin_table, code)
    if sys_admin_table.ptr == null():
        call.ioa_("No system_administrator_table found")
        return
    # end if
    
    project_id = arg_list.args.pop(0)
    person_id = arg_list.args.pop(0)
    
    if project_id not in sys_admin_table.ptr.projects:
        call.ioa_("{0} not found in the system_administrator_table", project_id)
        return
    # end if
    
    with sys_admin_table.ptr:
        if person_id in sys_admin_table.ptr.get_admins(project_id):
            sys_admin_table.ptr.remove_admin(project_id, person_id)
        else:
            call.ioa_("{0} not a {1} project administrator", person_id, project_id)
                        