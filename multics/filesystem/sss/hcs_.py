
from multics.globals import *

declare (unique_name_ = entry . returns (fixed.bin(32)),
         get_pdir_    = entry . returns (char('*')))

class hcs_(SystemExecutable):
    def __init__(self, system_services):
        super(hcs_, self).__init__(self.__class__.__name__, system_services)
        
        self.__filesystem = system_services.hardware.filesystem
    
    def signal_break(self):
        self.system.signal_break()
        
    def clear_kst(self):
        self.system.dynamic_linker.clear_kst()
        
    def get_entry_point(self, segment_name, segment):
        segment.ptr = self.system.dynamic_linker.link(segment_name)
        
    def del_entry_point(self, segment_name):
        self.system.dynamic_linker.unlink(segment_name)
        
    #== DATA FILE I/O ==#
    
    def create_process_dir(self, process_id, process_dir, code):
        dir_name = get_pdir_()
        entryname = unique_name_(process_id)
        self.create_branch_(dir_name, entryname, None, code)
        if code.val == 0:
            process_dir.name = dir_name + ">" + entryname
        else:
            process_dir.name = None
    
    def initiate(self, dirname, segment_name, segment):
        multics_path = dirname + ">" + segment_name
        native_path = self.__filesystem.path2path(multics_path)
        try:
            segment.ptr = self.__filesystem.segment_data_ptr(native_path)
        except:
            segment.ptr = nullptr()
                
    def make_seg(self, dirname, segment_name, segment, code):
        if dirname == "":
            dirname = get_pdir_()
        # end if
        
        if segment_name == "":
            segment_name = unique_name_()
        # end if
        
        multics_path = dirname + ">" + segment_name
        native_path = self.__filesystem.path2path(multics_path)
        
        if self.__filesystem.file_exists(native_path):
            segment.data_ptr = self.__filesystem.segment_data_ptr(native_path)
            code.val = error_table_.namedup
        # end if
        
        try:
            segment.data_ptr = self.__filesystem.segment_data_ptr(native_path, segment.data_ptr)
            code.val = 0
        except:
            import traceback
            traceback.print_exc()
            segment.data_ptr = nullptr()
            code.val = error_table_.fileioerr
            
    def delentry_seg(self, segment_data_ptr, code):
        code.val = segment_data_ptr.remove()

    def create_branch_(self, dir_name, entryname, info_ptr, code):
        multics_path = dir_name + ">" + entryname
        native_path = self.__filesystem.path2path(multics_path)
        if self.__filesystem.file_exists(native_path):
            code.val = error_table_.namedup
        else:
            code.val = self.__filesystem.mkdir(native_path)
        
    def delete_branch_(self, dir_name, code):
        native_path = self.__filesystem.path2path(dir_name)
        code.val = self.__filesystem.rmdir(native_path)
        
    def get_directory_contents(self, dir_name, branch, segment, code):
        native_path = self.__filesystem.path2path(dir_name)
        branch.list, segment.list, code.val = self.__filesystem.get_directory_contents(native_path)
        
    def make_path(self, dir_name, entryname, output):
        output.path = self.__filesystem.path2path(dir_name, entryname)
        