
from multics.globals import *

def ioa_test():
    call. ioa_("1234567890"*8)
    call. ioa_(":^5xFoo: ^2-^a.^a, ^4|^vd messages^/^20t^i%^2/Pi: ^v.vf ^4^, ^p", "JRCooper", "Psyop", 12, 15, 63, 0, 4, 3.141569, id(ioa_test))
    call. ioa_(":^5xUser:^20t^a.^a has ^vd messages.^/^2-^[^i% Done.^] ^20a^/", "JRCooper", "Psyop", 12, 15, True, 63, "Hello")
    call. ioa_("^v/Pi: ^v.vf ^v(^v^ ^)", 3, 20, 2, 3.141569, 3, 5, 2, 5)

    s1 = "^[froboz^] and ^[hello^;there^] or ^[a^;b^;c^;d^;e^]"
    s2 = "^[foobar^;^3(baz^)^]"
    s3 = "^v(this and ^[that^;other thing^;nothing^] ^)or something"

    b1 = bitstring(1, b'1')
    b2 = bitstring(12, b'110111000011')
    call. ioa_(s1, b1, 1, 3)
    call. ioa_(s2, 1)
    call. ioa_(s3, 4, 1, 2, 0, 1)

    s4 = "Foo: ^4|^3(bar ^) ^r"
    s5 = "Foo: ^v(baz ^) ^vp"
    call. ioa_(s4, s1)
    call. ioa_(s5, 3, 12, id(s5))

    s6 = "^vxoct=^.3b hex=^.4b bin=^20.1b dec=^d other=^.99b"
    print "%s" % b2, repr(b2), b2
    call. ioa_(s6, 6, b2, b2, b2, b2, b2)
    
    include.query_info
    input = parm()
    call. command_query_(query_info, input, "Continue...")
    
    s7 = "^(^a ^d ^)"
    s8 = "^(foobar and baz^) ^a ^d ^a ^v(^a^) ^d"
    s9 = "^v(foobar and baz^) ^a ^d ^a ^v(^a^) ^d"
    call. ioa_(s7, "foo", 1, "bar", 2, "baz", 3)
    call. ioa_(s8, "foo", 1, "bar", 2, "baz", "gruz", 3)
    call. ioa_(s9, 0, "foo", 1, "bar", 2, "baz", "frob", 3)
    call. ioa_("^(^d ^)", 1, 2, 56, 198, 456.7, 3e6)
    abs_sw = 0
    call. ioa_("^v(Absentee user ^)^a ^a logged out.", abs_sw, "LeValley", "Shop")
    abs_sw = 1
    call. ioa_("^v(Absentee user ^)^a ^a logged out.", abs_sw, "LeValley", "Shop")
    w1 = 0o112233445566
    w2 = 0o000033004400
    w3 = 0o000000000001
    w4 = 0o777777777777
    call. ioa_("^2(^2(^w ^)^/^)", w1, w2, w3, w4)
    a = [[1, 2], [3, 4]]
    call. ioa_("^d^s ^d ^w", a)
    b = [6, 7, 8, 9]
    call. ioa_("^v(^3d ^)", len(b), b)
    sw = False
    call. ioa_("a=^d ^[b=^d^;^s^] c=^d", 5, sw, 7, 9)
    sw = True
    call. ioa_("a=^d ^[b=^d^;^s^] c=^d", 5, sw, 7, 9)
    sw2 = bitstring(1, b'1')
    which = 0
    call. ioa_("^2(^[JRCooper^[.^[sa^;SysAdmin^]^]^] ^)", [sw, sw2, which] * 2)
    call. ioa_("^[a^;b^;^;^;c^;d^2;^v;e^]", 9, 2)
    call. ioa_("^4(^d. ^a^/^)", 1, "foo", 2, "bar", 3, "baz", 4)
