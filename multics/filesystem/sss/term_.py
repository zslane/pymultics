
from multics.globals import *

class term_(SystemSubroutine):
    def __init__(self, supervisor):
        super(term_, self).__init__(self.__class__.__name__, supervisor)
        
        self.__filesystem = supervisor.hardware.filesystem
    
    def procedure(self, filepath, code):
        dir_name, segment_name = self.__filesystem.split_path(filepath)
        self.single_refname(segment_name, code)

    def single_refname(self, ref_name, code):
        try:
            self.supervisor.dynamic_linker.unsnap(ref_name)
            code.val = 0
        except SegmentFault:
            code.val = error_table_.fileioerr
        
    def seg_ptr(self, segment, code):
        dir_name, segment_name = self.__filesystem.split_path(segment._filepath())
        self.single_refname(segment_name, code)
    