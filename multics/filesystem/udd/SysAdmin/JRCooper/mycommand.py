
from multics.globals import *

class MyData(object):
    def __init__(self):
        self.x = 1
        self.y = 2
        self.z = 3
    def __repr__(self):
        return "<MyData x:%d, y:%d, z:%d>" % (self.x, self.y, self.z)
        
declare (clock           = entry.returns,
         unique_name_    = entry.returns,
         active_function = entry.returns)

def mycommand():

    args = call.cu_.arg_list()
    call.ioa_("arg_list: {0}", args)
    call.test_()
    call.test_.func1()
    x = clock()
    call.ioa_("clock() = {0}", x)
    s = unique_name_(x)
    call.ioa_("shriekname is {0}", s)
    active_function()
    
    dirname = ">udd>SysAdmin>JRCooper"
    filename = "test.data"
    
    data, code = call.hcs_.make_seg(dirname, filename, MyData)
    if not data:
        call.ioa_("Error creating {0}>{1}", dirname, filename)
        return
    call.ioa_("data.x = {0}", data.x)
    call.ioa_("data.y = {0}", data.y)
    call.ioa_("data.z = {0}", data.z)
    
    data2 = call.hcs_.initiate(dirname, filename)
    if not data2:
        call.ioa_("Error loading {0}>{1}", dirname, filename)
        return
    data.x = 10
    call.ioa_("data.x = {0}", data2.x)
    call.ioa_("data.y = {0}", data2.y)
    call.ioa_("data.z = {0}", data2.z)
    
    code = call.hcs_.delentry_seg(data)
    if code != 0:
        call.ioa_("Error deleting {0}>{1}", dirname, filename)
        return
        
    data, code = call.hcs_.make_seg(dirname, filename, list)
    if not data:
        call.ioa_("Error creating {0}>{1}", dirname, filename)
        return
    call.ioa_("data = {0}", data())
    data([1, 2, 3, 4, 5, 6, 7, 8, 9])
    call.ioa_("data = {0}", data())
    call.ioa_("data[0:6:2] = {0}", data[0:6:2])
    
    code = call.hcs_.delentry_seg(data)
    if code != 0:
        call.ioa_("Error deleting {0}>{1}", dirname, filename)
        return
        
    (data, code) = call.hcs_.make_seg("", "test.data", list)
    if code != 0:
        call.ioa_("Error creating test.data in >pdd")
        if code == error_table_.namedup:
            call.ioa_("...NAMEDUP")
        else:
            call.ioa_("code = {0}", code)
    
    if data:
        call.hcs_.delentry_seg(data)
    