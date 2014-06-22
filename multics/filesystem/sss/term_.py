
from multics.globals import *

class term_(SystemExecutable):
    def __init__(self, system_services):
        super(term_, self).__init__(self.__class__.__name__, system_services)
        
        self.__filesystem = system_services.hardware.filesystem
    
    def procedure(self, filepath, code):
        dir_name, segment_name = self.__filesystem.split_path(filepath)
        self.single_refname(segment_name, code)

    def single_refname(self, ref_name, code):
        try:
            self.system.dynamic_linker.unsnap(ref_name)
            code.val = 0
        except SegmentFault:
            code.val = error_table_.fileioerr
        
    def seg_ptr(self, segment, code):
        dir_name, segment_name = self.__filesystem.split_path(segment._filepath())
        self.single_refname(segment_name, code)
    