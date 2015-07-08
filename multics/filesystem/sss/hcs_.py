
from multics.globals import *

declare (unique_name_ = entry . returns (fixed.bin(32)),
         get_pdir_    = entry . returns (char(168)),
         get_wdir_    = entry . returns (char(168)))

class hcs_(Subroutine):
    def __init__(self):
        super(hcs_, self).__init__(self.__class__.__name__)
            
    def signal_break(self):
        GlobalEnvironment.supervisor.signal_break(get_calling_process_())
        
    def get_entry_point(self, segment_name, segment):
        dir_name, entryname = None, segment_name
        if ">" in segment_name:
            if segment_name.startswith(">"):
                path = segment_name
            else:
                try:
                    current_dir = get_wdir_()
                except:
                    current_dir = get_pdir_()
                # end try
                path = GlobalEnvironment.fs.merge_path(current_dir, segment_name)
            dir_name, entryname = GlobalEnvironment.fs.split_path(path)
            #== This is so we don't lose track of the actual name of the command the user typed
            #== in the event it is embedded in a bound archive that is named something else
            if GlobalEnvironment.fs.is_archive(path):
                _, segment_name = GlobalEnvironment.fs.split_path(segment_name)
                entryname = entryname + '$' + segment_name
            # print "get_entry_point: dir_name = '%s', entryname = '%s'" % (dir_name, entryname)
        # end if
        with reference_frame(inspect.currentframe().f_back) as frame_id:
            segment.ptr = GlobalEnvironment.supervisor.dynamic_linker.snap(entryname, dir_name, frame_id=frame_id)
        
    def terminate_name(self, segment_name, code):
        try:
            GlobalEnvironment.supervisor.dynamic_linker.unsnap(segment_name)
            code.val = 0
        except SegmentFault:
            code.val = error_table_.fileioerr
        
    def terminate_file(self, filepath, code):
        # dir_name, segment_name = GlobalEnvironment.fs.split_path(filepath)
        # self.terminate_name(segment_name, code)
        multics_path = GlobalEnvironment.fs.path2path(filepath)
        try:
            GlobalEnvironment.supervisor.dynamic_linker.unsnap(multics_path)
            code.val = 0
        except SegmentFault:
            code.val = error_table_.fileioerr
        
    def terminate_ptr(self, segment, code):
        # dir_name, segment_name = GlobalEnvironment.fs.split_path(segment._filepath())
        # self.terminate_name(segment_name, code)
        self.terminate_file(segment._filepath(), code)
        
    #== DATA FILE I/O ==#
    
    def create_process_dir(self, process_id, process_dir, code):
        dir_name = GlobalEnvironment.fs.process_dir_dir
        entryname = unique_name_(process_id)
        self.create_branch_(dir_name, entryname, None, code)
        if code.val == 0 or code.val == error_table_.namedup:
            process_dir.name = dir_name + ">" + entryname
        else:
            process_dir.name = None
    
    def fs_valid_name(self, filename, code):
        if GlobalEnvironment.fs.valid_name(filename):
            code.val = 0
        else:
            code.val = error_table_.badpath
        
    def fs_file_exists(self, dirname, filename, code):
        native_path = GlobalEnvironment.fs.path2path(dirname, filename)
        if GlobalEnvironment.fs.file_exists(native_path):
            code.val = 0
        elif not GlobalEnvironment.fs.valid_name(dirname + ">" + filename):
            code.val = error_table_.badpath
        else:
            code.val = error_table_.no_directory_entry
        
    def initiate(self, dirname, segment_name, ref_name, seg_sw, copy_ctl_sw, segment, code):
        seg_ptr = GlobalEnvironment.supervisor.dynamic_linker.load(dirname, segment_name)
        if segment:
            segment.data_ptr = seg_ptr
        code.val = 0 if seg_ptr else error_table_.no_directory_entry
        
    def make_seg(self, dirname, segment_name, ref_name, mode, segment, code):
        if segment == null():
            segment = parm("")
        # end if
        
        if dirname == "":
            dirname = get_pdir_()
        # end if
        
        if segment_name == "":
            segment_name = unique_name_()
        # end if
        
        native_path = GlobalEnvironment.fs.path2path(dirname, segment_name)
        
        if GlobalEnvironment.fs.file_exists(native_path):
            segment.data_ptr = GlobalEnvironment.supervisor.dynamic_linker.load(dirname, segment_name)
            code.val = error_table_.namedup
            return
        # end if
        
        try:
            #== A BasedPointer that is null (None) needs to be reset to "point to" its
            #== original structure. This is how we simulate pointing to an "empty"
            #== segment of the based type.
            if type(segment) is BasedPointer and segment.data_ptr is None:
                segment.reset()
                
            #== Create the file on disk
            GlobalEnvironment.fs.segment_data_ptr(native_path, segment.data_ptr, force=True)
            #== Make sure the segment gets into the KST
            segment.data_ptr = GlobalEnvironment.supervisor.dynamic_linker.load(dirname, segment_name)
            code.val = 0
        except:
            import traceback
            traceback.print_exc()
            segment.data_ptr = null()
            code.val = error_table_.fileioerr
            
    def delentry_seg(self, segment_data_ptr, code):
        self.terminate_ptr(segment_data_ptr, code)
        code.val = segment_data_ptr.delete_file()
    
    def delentry_name(self, dirname, filename, code):
        self.fs_file_exists(dirname, filename, code)
        if code.val == 0:
            GlobalEnvironment.fs.delete_file(GlobalEnvironment.fs.merge_path(dirname, filename))
    
    def get_segment_length(self, dir_name, entryname, seg_len, code):
        full_path = GlobalEnvironment.fs.path2path(dir_name, entryname)
        try:
            seg_len.val = GlobalEnvironment.fs.get_size(full_path)
            code.val = 0
        except:
            code.val = error_table_.fileioerr
    
    def create_branch_(self, dir_name, entryname, info_ptr, code):
        dir_path = dir_name + ">" + entryname
        if GlobalEnvironment.fs.file_exists(dir_path):
            code.val = error_table_.namedup
        else:
            print "Creating", dir_path
            code.val = GlobalEnvironment.fs.mkdir(dir_path)
        
    def delete_branch_(self, dir_name, code):
        code.val = GlobalEnvironment.fs.rmdir(dir_name)
        
    def set_ring_brackets(self, dir_name, entryname, ring_brackets, code):
        pass
    
    def get_directory_contents(self, dir_name, branch, segment, code):
        branch.list, segment.list, code.val = GlobalEnvironment.fs.get_directory_contents(dir_name)
        
    def make_path(self, dir_name, entryname, output):
        output.path = GlobalEnvironment.fs.path2path(dir_name, entryname)
