
from multics.globals import *

include.query_info

admin_usage_text = (
"""Available commands are:
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

def admin():
    declare (command  = parm . init (""),
             arg_list = parm)
    
    MAIN = "admin"
    
    query_info.explanation_ptr = admin_usage_text
    while command.string != "quit" and command.string != "q":
        call.command_query_(query_info, command, MAIN, "command:")
        cmd, _, argument_string = command.string.partition(" ")
        if cmd:
            call.cu_.set_command_line_(cmd, argument_string)
            if cmd == "add_user" or cmd == "au":
                add_user()
            elif cmd == "remove_user" or cmd == "ru":
                remove_user()
            elif cmd == "help":
                call.ioa_(admin_usage_text)
            elif cmd != "quit" and cmd != "q":
                call.ioa_("Unrecgonized {0} command", MAIN)
                call.ioa_(admin_usage_text)
    
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
    
    print ",".join([person_id, project_id, alias, default_project_id])
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
    
    if project_id:
        pdt_filename = project_id + ".pdt"
        call.hcs_.initiate(system.hardware.filesystem.system_control_dir, pdt_filename, project_definition_table)
        if project_definition_table.ptr:
            with project_definition_table.ptr:
                project_definition_table.ptr.add_user(person_id)
        
@system_privileged
def remove_user():
    call.ioa_("remove_user not implemented yet")
    