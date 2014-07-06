
from multics.globals import *

class PersonNameTable(object):

    def __init__(self):
        self.name_entries = {}
        self.aliases = {}
        
    def person_id_list(self):
        return self.name_entries.keys()
        
    def alias_list(self):
        return self.aliases.keys()
        
    def add_person(self, person_id, alias="", default_project_id="*", encrypted_password="", pubkey=None):
        person_name_entry = PersonNameEntry(person_id, alias, default_project_id, encrypted_password, pubkey)
        self.name_entries[person_name_entry.person_id] = person_name_entry
        if person_name_entry.alias:
            self.aliases[person_name_entry.alias] = person_name_entry.person_id
        
    def del_person(self, person_id):
        person_name_entry = self.name_entries[person_id]
        if person_name_entry.alias:
            del self.aliases[person_name_entry.alias]
        # end if
        del self.name_entries[person_id]
    
    def person_id(self, name):
        name_entry = self.name_entries.get(name)
        return (name_entry and name_entry.person_id) or self.resolve_alias(name)
        
    def resolve_alias(self, name):
        return self.aliases.get(name, "")
        
    def get_default_project_id(self, name):
        try:
            name = self.resolve_alias(name) or name
            return self.name_entries[name].default_project_id
        except:
            raise MulticsCondition(error_table_.no_such_user)
            
    def set_default_project_id(self, name, default_project_id):
        try:
            name = self.resolve_alias(name) or name
            self.name_entries[name].default_project_id = default_project_id
        except:
            raise MulticsCondition(error_table_.no_such_user)
        
    def get_password(self, name):
        try:
            name = self.resolve_alias(name) or name
            return (self.name_entries[name].encrypted_password, self.name_entries[name].password_pubkey)
        except:
            raise MulticsCondition(error_table_.no_such_user)
            
    def set_password(self, name, encrypted_password):
        try:
            name = self.resolve_alias(name) or name
            self.name_entries[name].encrypted_password = encrypted_password
        except:
            raise MulticsCondition(error_table_.no_such_user)
        
    def __repr__(self):
        return "<%s.%s\n  name_entries: %s\n  aliases:      %s>" % (__name__, self.__class__.__name__, str(self.name_entries), str(self.aliases))
    
class PersonNameEntry(object):

    def __init__(self, person_id, alias="", default_project_id="", encrypted_password="", pubkey=None):
        self.person_id = person_id
        self.alias = alias
        self.default_project_id = default_project_id
        self.encrypted_password = encrypted_password
        self.password_pubkey = pubkey
        
    def __repr__(self):
        person_id = self.person_id
        if self.alias:
            person_id += " (%s)" % (self.alias)
        default_project_id = self.default_project_id or "None"
        return "<%s.%s person_id: %s, default_project_id: %s>" % (__name__, self.__class__.__name__, person_id, default_project_id)
        
