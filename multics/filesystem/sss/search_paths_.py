
from multics.globals import *

from sl_info import *
from sl_list import *

SEARCH_PATH_SYMBOLS = [
    "-home_dir",
    "-process_dir",
    "-working_dir",
]

class search_paths_(SystemExecutable):
    def __init__(self, system_services):
        super(search_paths_, self).__init__(self.__class__.__name__, system_services)
        
        self.__default_search_list = None
        
    def _default_search_list(self):
        if self.__default_search_list is None:
            paths_to_add = ["-working_dir", ">sss", ">sss>commands", "-home_dir"]
            self.__default_search_list = sl_info_structure()
            for path in paths_to_add:
                info = sl_info_path()
                info.pathname = path
                self.__default_search_list.paths.append(info)
            # end for
        # end if
        return self.__default_search_list
        
    def _default_search_segment(self):
        declare (get_pdir_  = entry . returns (char(168)),
                 search_seg = parm,
                 code       = parm)
                 
        process_dir = get_pdir_()
        call.hcs_.initiate(process_dir, "search_paths", search_seg, code)
        if search_seg.ptr == null():
            call.hcs_.make_seg(process_dir, "search_paths", search_seg(SearchSegment()), code)
        # end if
        
        return search_seg.ptr
        
    def _find_search_list_name(self, sl_name, search_seg_ptr):
        if sl_name not in search_seg_ptr.names:
            for i, link in enumerate(search_seg_ptr.aliases.link):
                if sl_name in link.names:
                    return search_seg_ptr.names[i]
                # end if
            else:
                return ""
            # end for
        # end if
        return sl_name
    
    def init_search_seg(self, search_seg_ptr, code):
        declare (get_pdir_  = entry . returns (char(168)),
                 search_seg = parm)
        
        if search_seg_ptr == null():
            #== If the process search segment already exists, then get it
            #== so we can wipe it clean. Otherwise create it from scratch.
            process_dir = get_pdir_()
            call.hcs_.initiate(process_dir, "search_paths", search_seg, code)
            if search_seg.ptr == null():
                call.hcs_.make_seg(process_dir, "search_paths", search_seg(SearchSegment()), code)
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
        declare (resolve_path_symbol_ = entry . returns (char(168)),
                 sl_info              = parm,
                 code                 = parm)
        self.get(sl_name, search_seg_ptr, sl_info, sl_info_version_1, code)
        if code.val == 0:
            for path in sl_info.ptr.paths:
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
        declare (resolve_path_symbol_ = entry . returns (char(168)),
                 sl_info              = parm,
                 code                 = parm)
        self.get(sl_name, search_seg_ptr, sl_info, sl_info_version_1, code)
        if code.val == 0:
            sl_info_ptr.data = sl_info_structure()
            for path in sl_info.ptr.paths:
                path = resolve_path_symbol_(path.pathname)
                native_path = self.system.fs.path2path(path, entryname)
                if self.system.fs.file_exists(native_path):
                    info = sl_info_path()
                    info.pathname = path
                    sl_info_ptr.data.paths.append(info)
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
        
        # sl_info_ptr.data = search_seg_ptr.paths[sl_name]
        sl_info_ptr.data = sl_info_structure()
        sl_info_ptr.data.paths = search_seg_ptr.paths[sl_name].paths[:]
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
                link = sl_list_link()
                link.names = [sl_name]
                search_seg_ptr.aliases.link.append(link)
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
        
        del search_seg_ptr.paths[sl_name]
        code.val = 0
    
class SearchSegment(object):
    def __init__(self):
        self.names = []
        self.paths = {}
        self.aliases = sl_list_structure()
        