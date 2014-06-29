
from multics.globals import *

include.sl_info
# from sl_info import *
from sl_list import *

SEARCH_PATH_SYMBOLS = [
    "-home_dir",
    "-process_dir",
    "-working_dir",
]

class search_paths_(SystemSubroutine):
    def __init__(self, system_services):
        super(search_paths_, self).__init__(self.__class__.__name__, system_services)
        
        self.__default_search_list = None
        
    def _default_search_list(self):
        if self.__default_search_list is None:
            paths_to_add = ["-working_dir", ">sss", ">sss>commands", "-home_dir"]
            self.__default_search_list = alloc(sl_info_p)
            for i in range(len(paths_to_add)):
                self.__default_search_list.num_paths += 1
                self.__default_search_list.paths[i].pathname = paths_to_add[i]
            # end for
        # end if
        return self.__default_search_list
        
    def _default_search_segment(self):
        declare (get_pdir_  = entry . returns (char(168)))
        
        search_seg = parm()
        code       = parm()
        
        process_dir = get_pdir_()
        call.hcs_.initiate(process_dir, "search_paths", "", 0, 0, search_seg, code)
        if search_seg.ptr == null():
            call.hcs_.make_seg(process_dir, "search_paths", "", 0, search_seg(SearchSegment()), code)
        # end if
        
        return search_seg.ptr
        
    def _find_search_list_name(self, sl_name, search_seg_ptr):
        if sl_name not in search_seg_ptr.names:
            i = 0
            list_link = search_seg_ptr.aliases
            while list_link and i < len(search_seg_ptr.names):
                if sl_name in list_link.names:
                    return search_seg_ptr.names[i]
                # end if
                i += 1
                list_link = list_link.link
            # end while
            return ""
        # end if
        return sl_name
    
    def init_search_seg(self, search_seg_ptr, code):
        declare (get_pdir_  = entry . returns (char(168)))
        
        search_seg = parm()
        
        if search_seg_ptr == null():
            #== If the process search segment already exists, then get it
            #== so we can wipe it clean. Otherwise create it from scratch.
            process_dir = get_pdir_()
            call.hcs_.initiate(process_dir, "search_paths", "", 0, 0, search_seg, code)
            if search_seg.ptr == null():
                call.hcs_.make_seg(process_dir, "search_paths", "", 0, search_seg(SearchSegment()), code)
                return
            else:
                search_seg_ptr = search_seg.ptr
            # end if
        # end if
        
        #== Wipe the search segment clean (i.e., initialize it)
        with search_seg_ptr:
            search_seg_ptr.data = SearchSegment()
        # end with
        code.val = 0
    
    def find_dir(self, sl_name, search_seg_ptr, entryname, dir_name, code):
        declare (resolve_path_symbol_ = entry . returns (char(168)))
        
        sl_info_get = parm()
        code        = parm()
        
        self.get(sl_name, search_seg_ptr, sl_info_get, sl_info_version_1, code)
        if code.val == 0:
            for path in sl_info_get.ptr.paths:
                path = resolve_path_symbol_(path.pathname)
                native_path = self.system.fs.path2path(path, entryname)
                if self.system.fs.file_exists(native_path):
                    dir_name.val = path
                    return
                # end if
            # end for
            code.val = error_table_.noentry
        # end if
    
    def find_all(self, sl_name, search_seg_ptr, entryname, sl_info_ptr, code):
        declare (resolve_path_symbol_ = entry . returns (char(168)))
        
        sl_info_get = parm()
        code        = parm()
        
        self.get(sl_name, search_seg_ptr, sl_info_get, sl_info_version_1, code)
        if code.val == 0:
            sl_info_ptr.data = alloc(sl_info_p)
            for path in sl_info_get.ptr.paths:
                path = resolve_path_symbol_(path.pathname)
                native_path = self.system.fs.path2path(path, entryname)
                if self.system.fs.file_exists(native_path):
                    sl_info_ptr.data.num_paths += 1
                    sl_info_ptr.data.paths[sl_info_ptr.data.num_paths - 1].pathname = path
                # end if
            # end for
            if sl_info_ptr.data.paths == []:
                code.val = error_table_.noentry    
    
    def get(self, sl_name, search_seg_ptr, sl_info_ptr, sl_info_version, code):
        if search_seg_ptr == null():
            search_seg_ptr = self._default_search_segment()
        # end if
        
        sl_name = self._find_search_list_name(sl_name, search_seg_ptr)
        if not sl_name:
            code.val = error_table_.no_search_list
            return
        # end if
        
        sl_info_ptr.data = alloc(sl_info_p)
        for i in range(len(search_seg_ptr.paths[sl_name].paths)):
            sl_info_ptr.data.num_paths += 1
            sl_info_ptr.data.paths[sl_info_ptr.data.num_paths - 1] = search_seg_ptr.paths[sl_name].paths[i] # PL1.Array __setitem__ creates a copy of rhs
        # end for
        code.val = 0
        
    def set(self, sl_name, search_seg_ptr, sl_info_ptr, code):
        code.val = 0
        
        if search_seg_ptr == null():
            search_seg_ptr = self._default_search_segment()
        # end if
        
        found_name = self._find_search_list_name(sl_name, search_seg_ptr)
        if not found_name:
            code.val = error_table_.new_search_list
        # end if
        sl_name = found_name or sl_name
        
        if sl_info_ptr != null():
            for path in sl_info_ptr.data.paths:
                if path.pathname in SEARCH_PATH_SYMBOLS or self.system.fs.file_exists(path.pathname):
                    path.code = 0
                else:
                    path.code = error_table_.no_directory_entry
                    code.val = error_table_.action_not_performed
                # end if
            # end for
        # end if
        
        if code.val == error_table_.action_not_performed:
            return
        # end if
        
        with search_seg_ptr:
            if code.val == error_table_.new_search_list:
                search_seg_ptr.names.append(sl_name)
                new_sl_list = alloc(sl_list)
                new_sl_list.version = sl_list_version_1
                new_sl_list.names.append(sl_name)
                new_sl_list.link = null()
                search_seg_ptr.aliases = new_sl_list
            # end if
            
            if sl_info_ptr != null():
                search_seg_ptr.paths[sl_name] = sl_info_ptr.data
            else:
                search_seg_ptr.paths[sl_name] = self._default_search_list()
            
    def list(self, search_seg_ptr, sl_list, code):
        if search_seg_ptr == null():
            search_seg_ptr = self._default_search_segment()
        # end if
        
        sl_list.ptr = search_seg_ptr.aliases
        code.val = 0
        
    def delete_list(self, sl_name, search_seg_ptr, code):
        if search_seg_ptr == null():
            search_seg_ptr = self._default_search_segment()
        # end if
        
        sl_name = self._find_search_list_name(sl_name, search_seg_ptr)
        if not sl_name:
            code.val = error_table_.no_search_list
            return
        # end if
        
        #== Remove matching link from list
        list_link = search_seg_ptr.aliases
        while list_link:
            if sl_name in list_link.names:
                list_link.link = sl_link.link
                break
            else:
                list_link = list_link.link
            # end if
        # end while
        
        del search_seg_ptr.paths[sl_name]
        code.val = 0
    
class SearchSegment(object):
    def __init__(self):
        self.names = []
        self.paths = {} # sl_name : sl_info
        self.aliases = null()
        