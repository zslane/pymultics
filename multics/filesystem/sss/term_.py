
from multics.globals import *

class term_(Subroutine):
    def __init__(self):
        super(term_, self).__init__(self.__class__.__name__)
    
    def procedure(self, filepath, code):
        dir_name, segment_name = GlobalEnvironment.fs.split_path(filepath)
        self.single_refname(segment_name, code)

    def single_refname(self, ref_name, code):
        try:
            GlobalEnvironment.supervisor.dynamic_linker.unsnap(ref_name)
            code.val = 0
        except SegmentFault:
            code.val = error_table_.fileioerr
        
    def seg_ptr(self, segment, code):
        # dir_name, segment_name = GlobalEnvironment.fs.split_path(segment._filepath())
        # self.single_refname(segment_name, code)
        multics_path = GlobalEnvironment.fs.path2path(segment._filepath())
        try:
            GlobalEnvironment.supervisor.dynamic_linker.unsnap(multics_path)
            code.val = 0
        except SegmentFault:
            code.val = error_table_.fileioerr
    