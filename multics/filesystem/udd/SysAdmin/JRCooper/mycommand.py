
from multics.globals import *

class MyData(object):
    def __init__(self):
        self.x = 1
        self.y = 2
        self.z = 3
    def __repr__(self):
        return "<MyData x:%d, y:%d, z:%d>" % (self.x, self.y, self.z)
        
declare (clock_          = entry . returns (fixed.bin(32)),
         unique_name_    = entry . returns (char('*')),
         active_function = entry . returns (fixed.bin))

declare (test_ = entry)

def mycommand():
    declare (args = parm,
             segment = parm,
             code = parm)
    
    call.cu_.arg_list(args)
    call.ioa_("arg_list: {0}", args.list)
    call.test_()
    call.test_.func1()
    call.ioa_("{0} squared = {1}", 5, test_.func2(5))
    x = clock_()
    call.ioa_("clock_() = {0}", x)
    s = unique_name_(x)
    call.ioa_("shriekname is {0}", s)
    active_function()
    
    dirname = ">udd>SysAdmin>JRCooper"
    filename = "test.data"
    
    call.hcs_.make_seg(dirname, filename, segment(MyData()), code)
    data = segment.ptr
    if not data:
        call.ioa_("Error creating {0}>{1}", dirname, filename)
        return
    call.ioa_("data.x = {0}", data.x)
    call.ioa_("data.y = {0}", data.y)
    call.ioa_("data.z = {0}", data.z)
    
    # data2 = call.hcs_.initiate(dirname, filename)
    # if not data2:
        # call.ioa_("Error loading {0}>{1}", dirname, filename)
        # return
    # data.x = 10
    # call.ioa_("data.x = {0}", data2.x)
    # call.ioa_("data.y = {0}", data2.y)
    # call.ioa_("data.z = {0}", data2.z)
    dcl (data2 = parm)
    call.hcs_.initiate(dirname, filename, data2)
    if not data2.ptr:
        call.ioa_("Error loading {0}>{1}", dirname, filename)
        return
    data.x = 10
    call.ioa_("data.x = {0}", data2.ptr.x)
    call.ioa_("data.y = {0}", data2.ptr.y)
    call.ioa_("data.z = {0}", data2.ptr.z)
    
    call.hcs_.delentry_seg(data, code)
    if code.val != 0:
        call.ioa_("Error deleting {0}>{1}", dirname, filename)
        return
        
    call.hcs_.make_seg(dirname, filename, segment([]), code)
    data = segment.ptr
    if not data:
        call.ioa_("Error creating {0}>{1}", dirname, filename)
        return
    call.ioa_("data = {0}", data())
    data([1, 2, 3, 4, 5, 6, 7, 8, 9])
    call.ioa_("data = {0}", data())
    call.ioa_("data[0:6:2] = {0}", data[0:6:2])
    
    call.hcs_.delentry_seg(data, code)
    if code.val != 0:
        call.ioa_("Error deleting {0}>{1}", dirname, filename)
        return
        
    declare (data3 = parameter . initialize (['a', 'b', 'c']))
    call.hcs_.make_seg("", "test.data", data3, code)
    if code.val != 0:
        call.ioa_("Error creating test.data in >pdd")
        if code.val == error_table_.namedup:
            call.ioa_("...NAMEDUP")
        else:
            call.ioa_("code = {0}", code.val)
    else:
        call.ioa_("data3 = {0}", data3.ptr)
    
    if data3.ptr != nullptr():
        call.hcs_.delentry_seg(data3.ptr, code)
    