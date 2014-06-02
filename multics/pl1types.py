
class PL1(object):

    Integer = 0
    Realnum = 1
    Cstring = 2
    Bstring = 3
    Pointer = 4
    Varying = 5
    
    Ascii = 0
    Binary = 2
    Decimal = 10
    
    Procedure = 0
    Function = 1

    class Type(object):
        def __init__(self, type, base, size):
            self.type = type
            self.base = base
            self.size = size
            
        def __call__(self, size):
            return PL1.Type(self.type, self.base, size)
            
        def __repr__(self):
            if self.type == PL1.Pointer:
                return "pointer"
            elif self.type == PL1.Varying:
                return "varying"
            elif self.type == PL1.Integer:
                s = "fixed"
            elif self.type == PL1.Realnum:
                s = "float"
            elif self.type == PL1.Cstring:
                s = "char"
            elif self.type == PL1.Bstring:
                s = "bit"
            if self.base == PL1.Binary:
                s += " binary"
            elif self.base == PL1.Decimal:
                s += " decimal"
            if not (self.type == PL1.Cstring and self.size == 1):
                s += "(%s)" % s #(str(self.size) if self.size > 0 else "*")
            return s
    
    class Options(object):
        def __init__(self, signature):
            self.signature = signature
            
        def __getattr__(self, attrname):
            return self.signature
            
    class ProcSignature(object):
        def __init__(self, *args):
            self.type = PL1.Procedure
            self.taking = args
            self.returning = None
            self.options = PL1.Options(self)
            
        def __call__(self, *args):
            return PL1.ProcSignature(*args)
            
        def returns(self, *args):
            return PL1.FuncSignature(self.taking, args)
            
        def __repr__(self):
            s = "entry"
            if self.taking:
                s += " (%s)" % (", ".join(map(repr, self.taking)))
            return s
            
    class FuncSignature(object):
        def __init__(self, taking, returning):
            self.type = PL1.Function
            self.taking = taking
            self.returning = returning
            self.options = PL1.Options(self)
            
        def __repr__(self):
            s = "entry"
            if self.taking:
                s += " (%s)" % (", ".join(map(repr, self.taking)))
            s += " returns (%s)" % (", ".join(map(repr, self.returning)))
            return s
            
    class Structure(object):
        def __init__(self, **attrs):
            self.__dict__.update(attrs)
            object.__setattr__(self, "_frozen_", True)
        
        def __setattr__(self, attr, val):
            if self._frozen_ and attr not in self.__dict__:
                raise AttributeError("'%s' has no attribute '%s'" % (self.__class__.__name__, attr))
            else:
                object.__setattr__(self, attr, val)
    
    class EnumValue(object):
        def __init__(self, enum_name, member_name, value):
            self.__enum_name = enum_name
            self.__member_name = member_name
            self.value = value
            
        def __eq__(self, rhs):
            if rhs == 0: # <-- special case: allow comparison with 0 literal
                return self.value == 0
            return type(self) == type(rhs) and self.value == rhs.value
        
        def __ne__(self, rhs):
            return not self.__eq__(rhs)
            
        def __repr__(self):
            return self.__enum_name + "." + self.__member_name

    class Enum(object):
        def __init__(self, enum_name, **members):
            for member_name, value in members.items():
                setattr(self, member_name, PL1.EnumValue(enum_name, member_name, value))
    
#-- end class PL1

fixed = PL1.Type(PL1.Integer, PL1.Binary, 17)
fixed.bin = fixed.binary = PL1.Type(PL1.Integer, PL1.Binary, 17)
fixed.dec = fixed.decimal = PL1.Type(PL1.Integer, PL1.Decimal, 18)

float = PL1.Type(PL1.Realnum, PL1.Binary, 31)
float.bin = float.binary = PL1.Type(PL1.Realnum, PL1.Binary, 31)
float.dec = float.decimal = PL1.Type(PL1.Realnum, PL1.Decimal, 32)

bit = PL1.Type(PL1.Bstring, PL1.Ascii, 1)
pointer = ptr = PL1.Type(PL1.Pointer, PL1.Binary, 36)

char = character = PL1.Type(PL1.Cstring, PL1.Ascii, 1)
varying = PL1.Type(PL1.Varying, PL1.Varying, PL1.Varying)

entry = PL1.ProcSignature()
