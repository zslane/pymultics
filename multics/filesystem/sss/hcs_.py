
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
        dir_name, entryname = None, segment_name
        if ">" in segment_name:
            if segment_name.startswith(">"):
                path = segment_name
            else:
                try:
                    current_dir = self.system.session_thread.session.process.directory_stack[-1]
                except:
                    current_dir = get_pdir_()
                # end try
                path = self.__filesystem.merge_path(current_dir, segment_name)
            dir_name, entryname = self.__filesystem.split_path(path)
            # print "get_entry_point: dir_name = '%s', entryname = '%s'" % (dir_name, entryname)
        # end if
        segment.ptr = self.system.dynamic_linker.snap(entryname, dir_name)
        
    def terminate_name(self, segment_name, code):
        try:
            self.system.dynamic_linker.unsnap(segment_name)
            code.val = 0
        except SegmentFault:
            code.val = error_table_.fileioerr
        
    def terminate_file(self, filepath, code):
        dir_name, segment_name = self.__filesystem.split_path(filepath)
        self.terminate_name(segment_name, code)
        
    def terminate_ptr(self, segment, code):
        dir_name, segment_name = self.__filesystem.split_path(segment.filepath)
        self.terminate_name(segment_name, code)
        
    #== DATA FILE I/O ==#
    
    def create_process_dir(self, process_id, process_dir, code):
        dir_name = self.__filesystem.process_dir_dir
        entryname = unique_name_(process_id)
        self.create_branch_(dir_name, entryname, None, code)
        if code.val == 0:
            process_dir.name = dir_name + ">" + entryname
        else:
            process_dir.name = None
    
    def initiate(self, dirname, segment_name, segment):
        segment.data_ptr = self.system.dynamic_linker.load(dirname, segment_name)
        # multics_path = dirname + ">" + segment_name
        # native_path = self.__filesystem.path2path(multics_path)
        # try:
            # segment.data_ptr = self.__filesystem.segment_data_ptr(native_path)
        # except:
            # segment.data_ptr = nullptr()
        
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
            # segment.data_ptr = self.__filesystem.segment_data_ptr(native_path)
            segment.data_ptr = self.system.dynamic_linker.load(dirname, segment_name)
            code.val = error_table_.namedup
            return
        # end if
        
        try:
            #== Create the file on disk
            # segment.data_ptr = self.__filesystem.segment_data_ptr(native_path, segment.data_ptr)
            self.__filesystem.segment_data_ptr(native_path, segment.data_ptr)
            #== Make sure the segment gets into the KST
            segment.data_ptr = self.system.dynamic_linker.load(dirname, segment_name)
            code.val = 0
        except:
            import traceback
            traceback.print_exc()
            segment.data_ptr = nullptr()
            code.val = error_table_.fileioerr
            
    def delentry_seg(self, segment_data_ptr, code):
        self.terminate_ptr(segment_data_ptr, code)
        code.val = code.val or segment_data_ptr.delete_file()
    
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
        