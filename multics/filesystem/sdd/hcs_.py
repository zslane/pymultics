
from multics.globals import *

class hcs_(SystemExecutable):
    def __init__(self, system_services):
        super(hcs_, self).__init__(self.__class__.__name__, system_services)
        
        self.__filesystem = system_services.hardware.filesystem
    
    def signal_break(self):
        self.system.signal_break()
        
    def clear_kst(self):
        self.system.dynamic_linker.clear_kst()
        
    def get_entry_point(self, segment_name):
        return self.system.dynamic_linker.link(segment_name)
        
    #== DATA FILE I/O ==#
    
    def create_process_dir(self, process_id):
        unique_process_dir_name = call.unique_name_(process_id)
        multics_path, code = self.create_branch_(call.get_pdir_(), unique_process_dir_name)
        if code == 0:
            return multics_path
        else:
            return None
    
    def initiate(self, dirname, segment_name):
        multics_path = dirname + ">" + segment_name
        native_path = self.__filesystem.path2path(multics_path)
        try:
            return self.__filesystem.segment_data_ptr(native_path)
        except:
            return None
            
    def make_seg(self, dirname, segment_name, ClassType):
        if dirname == "":
            dirname = call.get_pdir_()
        # end if
        
        if segment_name == "":
            segment_name = call.unique_name_()
        # end if
            
        multics_path = dirname + ">" + segment_name
        native_path = self.__filesystem.path2path(multics_path)
        
        if self.__filesystem.file_exists(native_path):
            return (None, error_table_.namedup)
        # end if
        
        try:
            return (self.__filesystem.segment_data_ptr(native_path, ClassType()), 0)
        except:
            import traceback
            traceback.print_exc()
            return (None, error_table_.fileioerr)
            
    def delentry_seg(self, segment_data_ptr):
        return segment_data_ptr.remove()

    def create_branch_(self, dir_name, entryname):
        multics_path = dir_name + ">" + entryname
        native_path = self.__filesystem.path2path(multics_path)
        code = self.__filesystem.mkdir(native_path)
        if code == 0:
            return (multics_path, 0)
        else:
            return (None, code)
            
    def delete_branch_(self, dir_name):
        native_path = self.__filesystem.path2path(dir_name)
        code = self.__filesystem.rmdir(native_path)
        return code
        
    def get_directory_contents(self, dir_name):
        native_path = self.__filesystem.path2path(dir_name)
        branch_list, segment_list, code = self.__filesystem.get_directory_contents(native_path)
        return (branch_list, segment_list, code)
        