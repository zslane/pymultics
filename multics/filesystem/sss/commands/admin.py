
from multics.globals import *

include.query_info

admin_usage_text = (
"""Available commands are:
    list_users, lu
    add_user, au
    remove_user, ru
    quit, q
    help, ?"""
    )
    
au_usage_text = (
"""Usage: add_user [person_id].[project_id] {{options}}
    options: -alias|-a [alias]
             -default_project|-dp [project_id]
             -set_password|-sp {{codeword}}"""
             )

MAIN = "admin"
    
def admin():
    declare (command  = parm . init (""),
             person   = parm,
             project  = parm,
             arg_list = parm)
    
    call.user_info_.whoami(person, project)
    if project.id != "SysAdmin":
        call.ioa_("You are not authorized to use the {0} command", MAIN)
        return
        
    while command.string != "quit" and command.string != "q":
        query_info.suppress_name_sw = False
        query_info.yes_or_no_sw = False
        query_info.explanation_ptr = admin_usage_text
        call.command_query_(query_info, command, MAIN)
        cmd, _, argument_string = command.string.partition(" ")
        if cmd:
            call.cu_.set_command_line_(cmd, argument_string)
            if cmd == "list_users" or cmd == "lu":
                list_users()
            elif cmd == "add_user" or cmd == "au":
                add_user()
            elif cmd == "remove_user" or cmd == "ru":
                remove_user()
            elif cmd == "help":
                call.ioa_(admin_usage_text)
            elif cmd != "quit" and cmd != "q":
                call.ioa_("Unrecgonized {0} command", MAIN)
                call.ioa_(admin_usage_text)
    
@system_privileged
def list_users():
    declare (arg_list          = parm,
             person_name_table = parm,
            )

    call.hcs_.initiate(system.hardware.filesystem.system_control_dir, "person_name_table", person_name_table)
    if person_name_table.ptr:
        call.ioa_("Person Id Alias     Dflt Proj Password?")
        call.ioa_("--------- --------- --------- ---------")
        for person_id in person_name_table.ptr.name_entries:
            call.ioa_("{0:9} {1:9} {2:9} {3}", person_id,
                person_name_table.ptr.name_entries[person_id].alias,
                person_name_table.ptr.name_entries[person_id].default_project_id,
                "Yes" if person_name_table.ptr.name_entries[person_id].encrypted_password else "No")
        call.ioa_("{0} total entries:", len(person_name_table.ptr.name_entries))
    
@system_privileged
def add_user():
    declare (arg_list          = parm,
             person_name_table = parm,
             project_definition_table = parm)
    
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
        
    user_id = arg_list.args.pop(0)
    person_id, _, project_id = user_id.partition(".")
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
                project_id = project_id or default_project_id
                i += 1
            else:
                show_usage()
                return
            # end if
        elif arg == "-set_password" or arg == "-sp":
            setting_password = True
            i += 1
            if i < len(arg_list.args):
                password = arg_list.args[i]
                i += 1
            else:
                password = ""
            # end if
            encrypted_password, pubkey = system.encrypt_password(password)
        # end if
    # end while
    
    call.hcs_.initiate(system.hardware.filesystem.system_control_dir, "person_name_table", person_name_table)
    if person_name_table.ptr:
        if person_id in person_name_table.ptr.alias_list():
            person_id = person_name_table.ptr.resolve_alias(person_id)
        # end if
        if person_id in person_name_table.ptr.person_id_list():
            name_entry = person_name_table.ptr.name_entries[person_id]
            alias = alias or name_entry.alias
            default_project_id = default_project_id or name_entry.default_project_id
            encrypted_password = encrypted_password if setting_password else name_entry.encrypted_password
            pubkey = pubkey or name_entry.password_pubkey
        elif project_id == "":
            call.ioa_("Warning: A new user is being added without a project id")
        # end if
        with person_name_table.ptr:
            person_name_table.ptr.add_person(person_id, alias, default_project_id, encrypted_password, pubkey)
        # end with
    # end if
    
    # if project_id:
        # pdt_filename = project_id + ".pdt"
        # call.hcs_.initiate(system.hardware.filesystem.system_control_dir, pdt_filename, project_definition_table)
        # if project_definition_table.ptr:
            # with project_definition_table.ptr:
                # project_definition_table.ptr.add_user(person_id)
        
@system_privileged
def remove_user():
    declare (arg_list          = parm,
             answer            = parm,
             person_name_table = parm)
    
    call.cu_.arg_list(arg_list)
    if len(arg_list.args) == 0:
        call.ioa_("Usage: ru [person_id]")
        return
        
    person_id = arg_list.args.pop(0)
    
    call.hcs_.initiate(system.hardware.filesystem.system_control_dir, "person_name_table", person_name_table)
    if person_name_table.ptr:
        if person_id in person_name_table.ptr.alias_list():
            person_id = person_name_table.ptr.resolve_alias(person_id)
        # end if
        if person_id in person_name_table.ptr.person_id_list():
            query_info.suppress_name_sw = True
            query_info.yes_or_no_sw = True
            query_info.explanation_ptr = "You are about to remove {0} as a user from the system. Continue (yes/no)?".format(person_id)
            call.command_query_(query_info, answer, MAIN, query_info.explanation_ptr)
            if answer.string.lower() in ["yes", "y"]:
                with person_name_table.ptr:
                    del person_name_table.ptr.name_entries[person_id]
                    for alias, pers in person_name_table.ptr.aliases.items():
                        if pers == person_id:
                            del person_name_table.ptr.aliases[alias]
                            break
                        # end if
                    # end for
                # end with
            # end if
        else:
            call.ioa_("No such user {0}", person_id)
    