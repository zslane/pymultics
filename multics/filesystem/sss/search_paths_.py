
from multics.globals import *

from sl_info import *
include.sl_list

class search_paths_(SystemExecutable):
    def __init__(self, system_services):
        super(search_paths_, self).__init__(self.__class__.__name__, system_services)
        paths_to_add = ["-working_dir", ">sss", ">sss>commands", "-home_dir"]
        self.__default_search_list = sl_info_structure()
        for path in paths_to_add:
            info = sl_info_path()
            info.pathname = path
            self.__default_search_list.paths.append(info)
        
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
        
    def _resolve_path_symbol(self, home_dir, working_dir, path):
        if path == "-home_dir":
            return home_dir
        elif path == "-working_dir":
            return working_dir
        else:
            return path
        # end if
    
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
    
    def find_dir(self, sl_name, search_seg_ptr, entryname, dir_name, code):
        declare (get_wdir_ = entry . returns (char(168)),
                 sl_info   = parm,
                 code      = parm)
        process = get_calling_process_()
        home_dir = process.pit().homedir
        try:
            working_dir = get_wdir_()
        except:
            working_dir = ">sc1"
        self.get(sl_name, search_seg_ptr, sl_info, sl_info_version_1, code)
        if code.val == 0:
            for path in sl_info.ptr.paths:
                path = self._resolve_path_symbol(home_dir, working_dir, path.pathname)
                native_path = self.system.fs.path2path(path, entryname)
                if self.system.fs.file_exists(native_path):
                    dir_name.val = path
                    return
                # end if
            # end for
            code.val = error_table_.noentry
        # end if
    
    def find_all(self, sl_name, search_seg_ptr, entryname, sl_info_ptr, code):
        declare (get_wdir_ = entry . returns (char(168)),
                 sl_info   = parm,
                 code      = parm)
        process = get_calling_process_()
        home_dir = process.pit().homedir
        working_dir = get_wdir_()
        self.get(sl_name, search_seg_ptr, sl_info, sl_info_version_1, code)
        if code.val == 0:
            sl_info_ptr.data = sl_info_structure()
            for path in sl_info.ptr.paths:
                path = self._resolve_path_symbol(home_dir, working_dir, path.pathname)
                native_path = self.system.fs.path2path(path, entryname)
                if self.system.fs.file_exists(native_path):
                    info = sl_info_path()
                    info.pathname = path
                    sl_info_ptr.data.paths.append(info)
                # end if
            # end for
            if sl_info_ptr.data.paths == []:
                code.val = error_table_.noentry    
    
    def get(self, sl_name, search_seg_ptr, sl_info, sl_info_version, code):
        if search_seg_ptr == null():
            search_seg_ptr = self._default_search_segment()
        # end if
        
        # if sl_name not in search_seg_ptr.names:
            # for i, link in enumerate(search_seg_ptr.aliases.link):
                # if sl_name in names:
                    # sl_name = search_seg_ptr.names[i]
                    # break
                # # end if
            # else:
                # code.val = error_table_.no_search_list
                # return
            # # end for
        # # end if
        sl_name = self._find_search_list_name(sl_name, search_seg_ptr)
        if not sl_name:
            code.val = error_table_.no_search_list
            return
        # end if
        
        sl_info.ptr = search_seg_ptr.paths[sl_name]
        code.val = 0
        
    def set(self, sl_name, search_seg_ptr, sl_info_ptr, code):
        code.val = 0
        
        if search_seg_ptr == null():
            search_seg_ptr = self._default_search_segment()
        # end if
        
        # if sl_name not in search_seg_ptr.names:
            # for i, link in enumerate(search_seg_ptr.aliases.link):
                # if sl_name in link.names:
                    # sl_name = search_seg_ptr.names[i]
                    # break
                # # end if
            # else:
                # code.val = error_table_.new_search_list
            # # end for
        # # end if
        found_name = self._find_search_list_name(sl_name, search_seg_ptr)
        if not found_name:
            code.val = error_table_.new_search_list
        # end if
        sl_name = found_name or sl_name
        
        if sl_info_ptr:
            for path in sl_info_ptr.paths:
                if self.system.fs.file_exists(path.pathname):
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
                search_seg_ptr.aliases.link.append([sl_name])
            # end if
            
            search_seg_ptr.paths[sl_name] = sl_info_ptr or self.__default_search_list
            
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
        
        # if sl_name not in search_seg_ptr.names:
            # for i, link in enumerate(search_seg_ptr.aliases.link):
                # if sl_name in names:
                    # sl_name = search_seg_ptr.names[i]
                    # break
                # # end if
            # else:
                # code.val = error_table_.no_search_list
                # return
            # # end for
        # # end if
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
        self.aliases = type(sl_list)()
        
    