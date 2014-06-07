
from multics.globals import *

class MyData(object):
    def __init__(self):
        self.x = 1
        self.y = 2
        self.z = 3
    def __repr__(self):
        return "<MyData x:%d, y:%d, z:%d>" % (self.x, self.y, self.z)
        
universe = PL1.Structure(
    number         = fixed.bin,
    pdir           = Dim(10) (char(32)),
    user           = Dim(10) (char(21)),
    unique_id      = Dim(10) (fixed.bin),
    holes          = fixed.bin,
    black_hole     = Dim(5) (char(8)),
    password       = char(10),
    robot          = Dim(2) (PL1.Structure(
        name       = char(5),
        energy     = fixed.bin,
        condition  = char(7),
        location   = char(8),
        controller = char(21),
        )),
    notifications  = Dim(5) (PL1.Structure(
        person_id  = char(21),
        project_id = char(9),
        )),
    lock           = bit(36),
)

declare (clock_          = entry . returns (fixed.bin(32)),
         unique_name_    = entry . returns (char('*')),
         active_function = entry,
         do              = entry . options (variable))

declare (test_ = entry)

def mycommand():
    declare (args = parm,
             segment = parm,
             code = parm,
             local_var  = fixed.decimal(12, 6) . init ([0, 2, 3.1415]), # <-- pythonic but not PL1-ish...use Dim() instead
             my_table   = Dim(3, 4) (fixed.decimal(6, 4) . init (3.1415)),
             test0_bits = bit('*') . init ("0b100110101"),
             test1_bits = bit(6) . init ("0b110101"),
             test2_bits = bit(6) . init ("0b011001"))
    
    call.cu_.arg_list(args)
    call.ioa_("arg_list: {0}", args.list)
    call.test_()
    call.test_.func1()
    call.ioa_("{0} squared = {1}", 5, test_.func2(5))
    x = clock_()
    call.ioa_("clock_() = {0}", x)
    s = unique_name_(x)
    call.ioa_("shriekname is {0}", s)
    call.active_function()
    call.ioa_("local_var = {0}", local_var)
    call.ioa_("test0_bits = {0} ({1})", test0_bits, int(test0_bits))
    call.ioa_("test1_bits = {0} ({1})", test1_bits, int(test1_bits))
    call.ioa_("test2_bits = {0} ({1})", test2_bits, int(test2_bits))
    test3_bits = test1_bits & test2_bits
    call.ioa_("test3_bits = {0} ({1})", test3_bits, int(test3_bits))
    
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
    
    declare (data2 = parm)
    call.hcs_.initiate(dirname, filename, data2, code)
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
        
    call.hcs_.make_seg(dirname, filename, segment(local_var), code)
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
    
    if data3.ptr != null():
        call.hcs_.delentry_seg(data3.ptr, code)
    
    call.do("who")
    call.term_.single_refname("do", code)
    call.hcs_.initiate(">sss", "do", null(), code)
    call.do("whoami")
    