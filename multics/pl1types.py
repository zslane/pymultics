
class Python(object):
    from decimal import Decimal

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
                    return list( self.pythonType()(val) for val in self.data )
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
                return self.BitstringFactory
                
        def DecimalFactory(self, val=0):
            fmt = "%%%d.%df" % (self.size, self.prec)
            return Python.Decimal(fmt % val)
            
        def BitstringFactory(self, val=""):
            return bitstring(self.size, val)
        
        def __call__(self, size, prec=0):
            return PL1.Type(self.type, self.base, size, prec)
            
        def __getattr__(self, attrname):
            return self
            
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
            def toArray(x): return PL1.Array([ toType(elem) for elem in x ], x.array_type)
            def toType(x):
                if type(x) is PL1.Type:
                    return x.toPython()
                elif type(x) is PL1.Array:
                    return toArray(x)
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
            if rhs == 0: # <-- special case: allow comparison with 0 literal (the 'success' code)
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
    
    class Array(list):
        class Expander(object):
            def __init__(self, array):
                self.array = array
                self.size = len(array)
            def __iadd__(self, value):
                self.size += value
                self.array._expand(value)
                return self
            def __int__(self):
                return self.size
            def __long__(self):
                return self.size
            
        def __init__(self, array, dcl_type):
            super(PL1.Array, self).__init__()
            self.extend(array)
            self.array_type = dcl_type
            self.size = PL1.Array.Expander(self)
            
        def expand(self, num_elements):
            self.size += num_elements
            
        def _expand(self, num_elements):
            for i in range(num_elements):
                if type(self.array_type) is PL1.Structure:
                    self.append(self.array_type.copy())
                elif type(self.array_type) is PL1.Type:
                    self.append(self.array_type.toPython())
                else:
                    self.append(self.array_type())
                
#-- end class PL1

class Dim(object):
    def __init__(self, *sizes):
        self.dimensions = list(sizes)
        
    def __call__(self, dcl_type):
        return self._make_nested_arrays(self.dimensions, dcl_type)
        
    def _make_nested_arrays(self, dimensions, dcl_type):
        size, dimensions = dimensions[0], dimensions[1:]
        if size == "*": size = 0
        a = []
        for i in range(size):
            if dimensions:
                a.append(self._make_nested_arrays(dimensions, dcl_type))
            else:
                a.append(dcl_type.copy())
            # end if
        # end for
        # return a
        return PL1.Array(a, dcl_type)

class bitstring(object):

    UNLIMITED = 0
        
    def __init__(self, num_bits, initial_value=""):
        if num_bits == "*":
            self.num_bits = self.UNLIMITED
        elif num_bits > 0:
            self.num_bits = num_bits
        else:
            raise ValueError("invalid bit string size {0}".format(num_bits))
        # end if
        self._set(initial_value)
        
    def _set(self, value):
        self.__value = []
        
        if type(value) is bitstring:
            self.__value = value.__value[-self.num_bits:]
            return
        # end if
        
        if type(value) is int:
            if self.num_bits == self.UNLIMITED:
                value = "{0:#b}".format(value)
            else:
                value = "{0:#0{width}b}".format(value, width=self.num_bits + 2)
            # end if
        elif type(value) is str:
            if self.num_bits == self.UNLIMITED:
                zero_value = "{0:#b}".format(0)
            else:
                zero_value = "{0:#0{width}b}".format(0, width=self.num_bits + 2)
            # end if
            value = value or zero_value
        else:
            raise TypeError(value)
        # end if
        
        if (self.num_bits != self.UNLIMITED) and (len(value) > self.num_bits + 2):
            raise OverflowError(value)
        # end if
        
        if value.lower().startswith("0b"):
            for bit in value[2:]:
                if bit in ["0", "1"]:
                    self.__value.append(int(bit))
                else:
                    raise ValueError(value)
                # end if
            # end for
        else:
            raise ValueError(value)
        
    def v(self):
        return self.__value

    def _int(self, num_bits):
        return reduce(lambda x, y: (x << 1) + y, self.__value[-num_bits:])
    
    def __call__(self, index):
        return self.__value[index]
        
    def __getitem__(self, index):
        return self.__value[index]
        
    def __setitem__(self, index, value):
        self.__value[index] = value
        
    def __and__(self, rhs):
        if type(rhs) is bitstring:
            return bitstring(self.num_bits, self.__int__() & rhs._int(self.num_bits))
        else:
            raise TypeError(rhs)
            
    def __or__(self, rhs):
        if type(rhs) is bitstring:
            return bitstring(self.num_bits, self.__int__() | rhs._int(self.num_bits))
        else:
            raise TypeError(rhs)
        
    def __xor__(self, rhs):
        if type(rhs) is bitstring:
            return bitstring(self.num_bits, self.__int__() ^ rhs._int(self.num_bits))
        else:
            raise TypeError(rhs)
    
    def __lshift__(self, n):
        return bitstring(self.UNLIMITED, self.__int__() << n)
        
    def __rshift__(self, n):
        return bitstring(self.num_bits, self.__int__() >> n)
    
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
        return reduce(lambda x, y: (x << 1) + y, self.__value)
        
    def __bool__(self):
        return any(self.__value)
    
    def __repr__(self):
        return '"%s"b' % ("".join(map(str, self.__value)))
        
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
