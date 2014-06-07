from decimal import Decimal as PyDecimal

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
        def __init__(self, type, base, size, prec=0):
            self.type = type
            self.base = base
            self.size = size
            self.prec = prec
            self.data = None
            
        def init(self, data):
            self.data = data
            return self
            
        def initialize(self, data):
            return self.init(data)
            
        def copy(self):
            return PL1.Type(self.type, self.base, self.size, self.prec).init(self.data)
            
        def toPython(self):
            if self.data is not None:
                if type(self.data) == list:
                    return [ self.pythonType()(val) for val in self.data ]
                elif type(self.data) == tuple:
                    return tuple( self.pythonType()(val) for val in self.data )
                else:
                    return self.pythonType()(self.data)
            else:
                return self.pythonType()()
                
        def pythonType(self):
            if self.type == PL1.Pointer:
                return int
            elif self.type == PL1.Varying:
                return list
            elif self.type == PL1.Integer:
                if self.base == PL1.Binary:
                    return int
                elif self.base == PL1.Decimal:
                    return self.DecimalFactory
            elif self.type == PL1.Realnum:
                if self.base == PL1.Binary:
                    return float
                elif self.base == PL1.Decimal:
                    return self.DecimalFactory
            elif self.type == PL1.Cstring:
                return str
            elif self.type == PL1.Bstring:
                return bitstring
                
        def DecimalFactory(self, val=0):
            fmt = "%%%d.%df" % (self.size, self.prec)
            return PyDecimal(fmt % val)
        
        def __call__(self, size, prec=0):
            return PL1.Type(self.type, self.base, size, prec)
            
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
                if self.prec > 0:
                    s += "(%d, %d)" % (self.size, self.prec)
                else:
                    s += "(%s)" % self.size
            return s
    
    class Options(object):
        def __init__(self, signature):
            self.signature = signature
            
        def __call__(self, option):
            return self.signature
            
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
            def toPythonList(x): return [ toType(elem) for elem in x ]
            def toType(x):
                if type(x) is PL1.Type:
                    return x.toPython()
                elif type(x) is list:
                    return toPythonList(x)
                else:
                    return x
            
            for attr in attrs:
                attrs[attr] = toType(attrs[attr])
                
            self.__dict__.update(attrs)
            
            object.__setattr__(self, "_frozen_", True)
        
        def __setattr__(self, attr, val):
            if self._frozen_ and attr not in self.__dict__:
                raise AttributeError("'%s' has no attribute '%s'" % (self.__class__.__name__, attr))
            else:
                object.__setattr__(self, attr, val)
                
        def copy(self):
            return PL1.Structure(**self.__dict__)
            
        def __repr__(self):
            attributes = ",\n  ".join([ "{0}: {1}".format(k, repr(v)) for k, v in self.__dict__.items() if k != "_frozen_" ])
            s = "<PL1.Structure\n  %s>" % (attributes)
            return s
    
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
    
    class Array(object):
        def __init__(self, size):
            self.size = size
            
        def __call__(self, dcl_type):
            a = []
            for i in range(self.size):
                a.append(dcl_type.copy())
            return a
    
#-- end class PL1
    
class bitstring(object):
    def __init__(self, initial_value=""):
        self._set(initial_value)
        
    def _set(self, value):
        self.__value = []
        
        if type(value) is bitstring:
            self.__value = value.__value[:]
            return
        # end if
        
        if type(value) is int:
            value = bin(value)
        else:
            value = value or "0b0"
        # end if
        
        if value.lower().startswith("0b"):
            for bit in value[:1:-1]:
                if bit in ["0", "1"]:
                    self.__value.append(int(bit))
                else:
                    raise ValueError(value)
                # end if
            # end for
        else:
            raise ValueError(value)
            
    def __call__(self, index):
        return self.__value[len(self.__value) - index - 1]
        
    def __getitem__(self, index):
        return self.__value[len(self.__value) - index - 1]
        
    def __setitem__(self, index, value):
        self.__value[len(self.__value) - index - 1] = value
        
    def __and__(self, rhs):
        if type(rhs) is bitstring:
            self._set(self.__int__() & rhs.__int__())
            return self
        else:
            raise TypeError(rhs)
            
    def __or__(self, rhs):
        if type(rhs) is bitstring:
            self._set(self.__int__() | rhs.__int__())
            return self
        else:
            raise TypeError(rhs)
        
    def __xor__(self, rhs):
        if type(rhs) is bitstring:
            self._set(self.__int__() ^ rhs.__int__())
            return self
        else:
            raise TypeError(rhs)
    
    def __lshift__(self, n):
        self._set(self.__int__() << n)
        return self
        
    def __rshift__(self, n):
        self._set(self.__int__() >> n)
        return self
    
    def __eq__(self, rhs):
        if type(rhs) is str:
            return self.__int__() == int(rhs, 2)
        elif type(rhs) is int:
            return self.__int__() == rhs
        elif type(rhs) is bitstring:
            return self.__int__() == rhs.__int__()
        else:
            return False
            
    def __neq__(self, rhs):
        return not self.__eq__(rhs)
        
    def __int__(self):
        return int("0b%s" % ("".join(map(str, self.__value[::-1]))), 2)
        
    def __bool__(self):
        return any(self.__value)
    
    def __repr__(self):
        return '"%s"b' % ("".join(map(str, self.__value[::-1])))
        
#-- end class bitstring

PL1.Option = PL1.Enum("pl1_options",
        variable = -1,
    )
    
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
variable = PL1.Option.variable

#== This is defined just so PL1.Structures can be pickled
Structure = PL1.Structure
