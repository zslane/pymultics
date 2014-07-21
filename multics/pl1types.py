
class Python(object):
    from decimal import Decimal

class parameter(object):

    def __init__(self, value=None):
        self.value = value
        
    @property
    def initial_value(self):
        return self.value
        
    @property
    def local(self):
        return self
        
    #== __getattr__ and __setattr__ allow the stored value to be referred to
    #== by any name that is convenient for the programmer. One possible
    #== convention is to use 'ptr' for pointer values and 'val' for scalars.
    def __getattr__(self, attrname):
        return self.value
        
    def __setattr__(self, attrname, x):
        object.__setattr__(self, "value", x)
        
    def __call__(self, value=None):
        #== Call with no arguments returns the parm's currently stored value
        if value is None:
            return self.value
        #== Calling with an argument stores it as the current value. Note that
        #== we return self so the parm can be initialized to some value as it
        #== is being passed to a function.
        else:
            self.value = value
            return self
        
    @staticmethod
    def init(initial_value):
        return parameter(initial_value)
        
    @staticmethod
    def initialize(initial_value):
        return parameter(initial_value)
        
    # def __repr__(self):
        # s = str(self.value)
        # if len(s) > 50:
            # s = s[:48] + "..."
        # return "<%s.%s object: %s>" % (__name__, self.__class__.__name__, s[:51])

parm = parameter

class FileOp(object):
    def __init__(self, file_obj):
        self.file_obj = file_obj
        
class OpenFileOp(FileOp):
    def title(self, path):
        self.file_obj.path = path
        return self
    @property
    def stream(self):
        self.file_obj.type = "stream"
        return self
    @property
    def record(self):
        self.file_obj.type = "record"
        return self
    @property
    def input(self):
        if self.file_obj.type == "stream":
            self.file_obj.f = open(self.file_obj.path, "r")
        else:
            self.file_obj.f = open(self.file_obj.path, "rb")
        return self
    @property
    def output(self):
        if self.file_obj.type == "stream":
            self.file_obj.f = open(self.file_obj.path, "w")
        else:
            self.file_obj.f = open(self.file_obj.path, "wb")
        return self
        
class ReadFileOp(FileOp):
    def into(self, input_parm):
        if self.file_obj.type == "stream":
            input_parm.value = self.file_obj.f.readline().strip()
        else:
            input_parm.value = self.file_obj.f.read()
        
class CloseFileOp(object):
    def __init__(self, file_obj):
        file_obj.f.close()
            
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
            
            self.parm = parameter()
            self.parameter = self.parm
            
        @property
        def local(self):
            return self.toPython()
            
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
                    import __builtin__
                    return __builtin__.float
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
            
        def __call__(self, size=-1, prec=0):
            if size == -1:
                return self.toPython()
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
            def toArray(x): return PL1.Array([ toType(elem) for elem in x ], x.attrs, x.dynamic_size_ref)
            # def toArray(x): return PL1.Array([ toType(elem) for elem in x ])
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
                
            # print attrs
            
            self.__dict__.update(attrs)
            
            for attr in attrs.values():
                if type(attr) is PL1.Array:
                    if attr.dynamic_size_ref in attrs:
                        # print "Structure resolving dynamic size reference:", attr.dynamic_size_ref
                        initial_size = self.__dict__[attr.dynamic_size_ref]
                        self.__dict__[attr.dynamic_size_ref] = DynamicArraySizer(attr)
                        if initial_size:
                            self.__dict__[attr.dynamic_size_ref] += int(initial_size)
                        # end if
                        # del attr.__dict__['size']
                        attr.__dict__['size'] = self.__dict__[attr.dynamic_size_ref]
                    # end if
                # end if
            # end for
            
            object.__setattr__(self, "_frozen_", True)
        
        def __setattr__(self, attr, val):
            if self._frozen_ and attr not in self.__dict__:
                raise AttributeError("'%s' has no attribute '%s'" % (self.__class__.__name__, attr))
            else:
                object.__setattr__(self, attr, val)
                
        def copy(self):
            return PL1.Structure(**self.__dict__)

        def dumps(self):
            attributes = ",\n  ".join([ "{0}: {1}".format(k, repr(v)) for k, v in self.__dict__.items() if k != "_frozen_" ])
            s = "<PL1.Structure\n  %s>" % (attributes)
            return s
            
        # @staticmethod
        # def based(base_pointer):
            # import inspect, re
            # pframe = inspect.currentframe()
            # # x = inspect.getargvalues(pframe)
            # # print x
            # outer = pframe.f_back
            # info = inspect.getframeinfo(outer)
            # expr = info.code_context[info.index]
            # expr = re.sub(r"\s+", "", expr)
            # m = re.search(r"(.*)=.*based\((\w+)\)", expr)
            # # print expr
            # # print m
            # # if m:
               # # print m.groups()
            # outer = inspect.getouterframes(outer)
            # struct_name = m.group(1)
            # pointer_name = m.group(2)
            # for pframe in outer:
                # if pointer_name in pframe[0].f_globals or pointer_name in pframe[0].f_locals:
                    # globals_dict = pframe[0].f_globals
                    # break
            # else:
                # raise Exception(pointer_name + " not found")
            # return BasedStructureFactory(globals_dict, struct_name, pointer_name)
            
        @staticmethod
        def based(**args):
            import inspect, re
            pframe = inspect.currentframe()
            outer = pframe.f_back
            outer = inspect.getouterframes(outer)
            for pointer_name, struct_name in args.items():
                for pframe in outer:
                    if pointer_name in pframe[0].f_globals or pointer_name in pframe[0].f_locals:
                        globals_dict = pframe[0].f_globals
                        break
                else:
                    raise Exception(pointer_name + " not found")
                return BasedStructureFactory(globals_dict, struct_name, pointer_name)
            
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
            return self.__enum_name + "$" + self.__member_name

    class Enum(object):
        def __init__(self, enum_name, **members):
            for member_name, value in members.items():
                setattr(self, member_name, PL1.EnumValue(enum_name, member_name, value))
    
    class Array(list):
        def __init__(self, a, dcl_type, refname=""):
            self[:] = a
            self.attrs = None
            if type(dcl_type) is PL1.Structure:
                self.attrs = dcl_type.__dict__
            elif type(dcl_type) is PL1.Type:
                self.attrs = dcl_type.toPython()
            else:
                self.attrs = dcl_type
            # end if
            self.size = None
            #== This allows dynamic sizing using Dim('*')
            if a == []:
                self.size = DynamicArraySizer(self)
            # end if
            #== This allows dynamic sizing using Dim(Dynamic.attrname)
            self.dynamic_size_ref = refname
            
        @property
        def local(self):
            return self
            
        def init(self, value):
            self[:] = value
            if self.size:
                #== Replace with a new dynamic sizer
                self.size = DynamicArraySizer(self)
            return self
            
        def initialize(self, value):
            return self.init(value)
            
        def append(self, element=None):
            if element is None:
                if type(self.attrs) is dict:
                    super(PL1.Array, self).append(PL1.Structure(**self.attrs))
                else:
                    super(PL1.Array, self).append(self.attrs)
                # end if
            else:
                super(PL1.Array, self).append(element)
            # end if
            if self.size:
                self.size.pushing()
            
        def insert(self, where, element=None):
            if element is None:
                if type(self.attrs) is dict:
                    super(PL1.Array, self).insert(where, PL1.Structure(**self.attrs))
                else:
                    super(PL1.Array, self).insert(where, self.attrs)
                # end if
            else:
                super(PL1.Array, self).insert(where, element)
            # end if
            if self.size:
                self.size.pushing()
            
        def extend(self, elements):
            super(PL1.Array, self).extend(elements)
            if self.size:
                self.size.pushing(len(elements))
            
        def pop(self, index):
            if self.size:
                self.size.popping()
            return super(PL1.Array, self).pop(index)
            
        def __delitem__(self, index):
            n = len(self)
            super(PL1.Array, self).__delitem__(index)
            if self.size:
                self.size.popping(n - len(self))
                
        def __setitem__(self, index, value):
            if type(value) is PL1.Structure:
                super(PL1.Array, self).__setitem__(index, value.copy())
            else:
                super(PL1.Array, self).__setitem__(index, value)
        
        def _expand(self, num_elements):
            for i in range(num_elements):
                #== Dictionaries are used to capture PL1.Structures
                if type(self.attrs) is dict:
                    super(PL1.Array, self).append(PL1.Structure(**self.attrs))
                else:
                    super(PL1.Array, self).append(self.attrs)
                    
        def _shrink(self, num_elements):
            del self[-num_elements:]
            
        def _reset(self, to_size):
            #== If we're too big, delete extraneous elements off the end
            if len(self) > to_size:
                del self[to_size:]
            #== If we're too small, expand (by appending)
            elif len(self) < to_size:
                self._expand(to_size - len(self))
            
        def __repr__(self):
            refstring = "(sized by '%s')" % self.dynamic_size_ref if self.dynamic_size_ref else "(%d)" % (len(self))
            return "<PL1.Array %s %s>" % (refstring, repr(self[:]))
    
    class File(object):
        def __init__(self):
            self.path = ""
            self.type = "record"
            self.f = None
        
    class Opener(object):
        def __init__(self):
            self.file = OpenFileOp
        
    class Reader(object):
        def __init__(self):
            self.file = ReadFileOp
        
    class Closer(object):
        def __init__(self):
            self.file = CloseFileOp
    
    open = Opener()
    read = Reader()
    close = Closer()
        
#-- end class PL1

class BasedStructureFactory(object):
    def __init__(self, gdict, struct_name, pointer_name):
        self.globals_dict = gdict
        self.pointer_name = pointer_name
        self.based_struct_name = struct_name
        
    def __call__(self, **kwargs):
        structure = PL1.Structure(**kwargs)
        based_pointer = BasedPointer(structure)
        self.globals_dict[self.pointer_name] = based_pointer
        based_struct = BasedStructure(self.pointer_name, based_pointer)
        self.globals_dict[self.based_struct_name] = based_struct
        # print "CREATING BASED STRUCT OBJECTS:"
        # print self.globals_dict['__name__']
        # print structure
        # print self.pointer_name, based_pointer
        # print self.based_struct_name, self.globals_dict[self.based_struct_name]
        # return structure
        return based_struct

class BasedPointer(parameter):
    def __init__(self, data):
        super(BasedPointer, self).__init__(data)
        #== Remember the based structure in case we are set to None and
        #== need to be 'reset'
        self.__dict__['__based_type'] = data
    def reset(self):
        self(self.__dict__['__based_type'])
    def alloc(self):
        return self.__dict__['__based_type'].copy()
    def __repr__(self):
        return "<BasedPointer of: %s>" % (repr(self.value))
        
class BasedStructure(object):
    def __init__(self, tracked_name, tracked_object):
        self.__dict__['tracked_name'] = tracked_name
        self.__dict__['tracked_object'] = tracked_object
    def __getattr__(self, attrname):
        return getattr(self.tracked_object.value, attrname)
    def __setattr__(self, attrname, value):
        setattr(self.tracked_object.value, attrname, value)
    def __repr__(self):
        return repr(self.tracked_object.value)
        # return "%s tracking %s %s" % (object.__repr__(self), repr(self.__dict__['tracked_name']), repr(self.__dict__['tracked_object']))
    def __enter__(self):
        return self.tracked_object.value.__enter__()
    def __exit__(self, *args):
        return self.tracked_object.value.__exit__(*args)
    def dumps(self):
        return repr(self.tracked_object.value)
    def based_ptr_item(self):
        return {self.__dict__['tracked_name']:self.__dict__['tracked_object']}

class DynamicArraySizer(object):
    def __init__(self, array):
        self.array = array
        self.size = len(array)
    def __iadd__(self, value):
        self.size += value
        self.array._expand(value)
        return self
    def __isub__(self, value):
        self.size -= value
        self.array._shrink(value)
        return self
    def __add__(self, value):
        return self.size + value
    def __sub__(self, value):
        return self.size - value
    def __int__(self):
        return self.size
    def __long__(self):
        return self.size
    def __index__(self):
        return self.size
    def reset(self, val=0):
        self.array._reset(val)
        self.size = val
    def pushing(self, value=1):
        self.size += value
    def popping(self, value=1):
        self.size -= value
    def __repr__(self):
        return "<DynamicArraySizer (%d) size for: %s>" % (self.size, repr(self.array))
        
class DynamicSizeRef(object):
    def __init__(self, refname):
        self.ref = refname
    def __getattr__(self, refname):
        self.ref = (self.ref + "." + refname) if self.ref else refname
        return self
        
class DynamicSizeRefFactory(object):
    def __getattr__(self, refname):
        return DynamicSizeRef(refname)
        
Dynamic = DynamicSizeRefFactory()

class Dim(object):
    def __init__(self, *sizes):
        self.dimensions = list(sizes)
        
    def __call__(self, dcl_type):
        return self._make_nested_arrays(self.dimensions, dcl_type)
        
    def _make_nested_arrays(self, dimensions, dcl_type):
        size, dimensions = dimensions[0], dimensions[1:]
        if size == "*": size = 0
        
        if type(size) is DynamicSizeRef:
            # print "DYNSIZEREF: " + size.ref
            refname = size.ref
            size = 0
        else:
            refname = ""
        # end if
        
        a = []
        for i in range(size):
            if dimensions:
                a.append(self._make_nested_arrays(dimensions, dcl_type))
            else:
                a.append(dcl_type.copy())
            # end if
        # end for
        
        # return a
        return PL1.Array(a, dcl_type, refname)

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
            value = value[2:]
        if set(list(value)) - set(['0', '1']) == set():
            self.__value = map(int, list(value))
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
    
    def __str__(self):
        return '"%s"b' % ("".join(map(str, self.__value)))
    
    def __repr__(self):
        return '%s' % ("".join(map(str, self.__value)))
        
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
pointer = ptr = PL1.Type(PL1.Pointer, PL1.Binary, 36).parm

char = character = PL1.Type(PL1.Cstring, PL1.Ascii, 1)
varying = PL1.Type(PL1.Varying, PL1.Varying, PL1.Varying)

entry = PL1.ProcSignature()
variable = PL1.Option.variable

#== This is defined just so PL1.Structures can be pickled
Structure = PL1.Structure
Array = PL1.Array
