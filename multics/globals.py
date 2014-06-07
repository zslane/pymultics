import os
import re
import types

from pl1types import *

from PySide import QtCore

class MulticsCondition(Exception):
    def __init__(self, arg=""):
        super(MulticsCondition, self).__init__(arg)
    
class BreakCondition(MulticsCondition):
    def __init__(self):
        super(MulticsCondition, self).__init__()
        
class ShutdownCondition(MulticsCondition):
    def __init__(self):
        super(ShutdownCondition, self).__init__()

class SegmentFault(MulticsCondition):
    def __init__(self, entry_point_name):
        super(SegmentFault, self).__init__("segment not found %s" % (entry_point_name))
        self.segment_name = entry_point_name
        
class LinkageError(MulticsCondition):
    def __init__(self, segment_name, entry_point_name):
        super(LinkageError, self).__init__("entry not found %s.%s" % (segment_name, entry_point_name))
        self.entry_point_name = entry_point_name

class InvalidSegmentFault(MulticsCondition):
    def __init__(self, entry_point_name):
        super(InvalidSegmentFault, self).__init__("invalid segment %s" % (entry_point_name))
        self.segment_name = entry_point_name
        
class System:
    
    INVALID_LOGIN = -1
    SHUTDOWN = -2
    LOGOUT = -3
    NEW_PROCESS = -4
    
error_table_ = PL1.Enum("error_table_",
    no_such_user = -4,
    fileioerr = -5,
    namedup = -6,
    invalid_lock_reset = -7,
    locked_by_this_process = -8,
    lock_wait_time_exceeded = -9,
    no_w_permission = -10,
    lock_not_locked = -11,
    locked_by_other_process = -12,
    noarg = -13,
    no_directory_entry = -14, # non-existant file or directory
)

class Executable(QtCore.QObject):
    """
    Executables are created within the SegmentDescriptor constructor to
    represent both procedure$entrypoint executables and pure functions.
    """
    def __init__(self, segment_name, fn=None):
        super(Executable, self).__init__()
        
        self.__segment_name = segment_name
        self.__fn = fn # wrapped python function
        
    def __call__(self, *args, **kwargs):
        return self.procedure(*args, **kwargs)
        
    def procedure(self, *args, **kwargs):
        if self.__fn:
            #== Call the wrapped python function
            return self.__fn(*args, **kwargs)
        else:
            raise LinkageError(self.__segment_name, "procedure (main entry point)")
        
    def __getattr__(self, entry_point_name):
        raise LinkageError(self.__segment_name, entry_point_name)
        
    def __repr__(self):
        if self.__fn:
            return "<%s.%sCommand %s>" % (__name__, self.__class__.__name__, self.__segment_name)
        else:
            return super(Executable, self).__repr__()
    
class SystemExecutable(Executable):
    def __init__(self, segment_name, system_services):
        super(SystemExecutable, self).__init__(segment_name)
        
        self.system = system_services
        
class CommandProcessor(SystemExecutable):
    def __init__(self, segment_name, system_services):
        super(CommandProcessor, self).__init__(segment_name, system_services)
        
    def start(self):
        raise LinkageError(self.__segment_name, "start (command processor entry point)")
        
    def kill(self):
        raise LinkageError(self.__segment_name, "kill (command processor kill point)")
        
    def _on_condition__break(self):
        pass

__system_services = None
call = None

def _register_system_services(system_services, dynamic_linker):
    global __system_services
    __system_services = system_services
    global call
    call = dynamic_linker

def system_privileged(fn):
    def decorated(*args, **kw):
        # my_globals={}
        # my_globals.update(fn.__globals__)
        # my_globals['system'] = __system_services
        # call_fn = types.FunctionType(fn.func_code, my_globals)
        # return call_fn(*args, **kw)
        fn.__globals__['system'] = __system_services
        return fn(*args, **kw)
    decorated.__name__ = fn.__name__
    return decorated

class LinkageReference(object):
    def __init__(self, name, dynamic_linker):
        self.dynamic_linker = dynamic_linker
        self.name = name
    def __call__(self, *args, **kwargs):
        entry_point = self.dynamic_linker.snap(self.name)
        if entry_point:
            return entry_point(*args, **kwargs)
        else:
            raise SegmentFault(self.name)
    def __getattr__(self, entry_point_name):
        segment = self.dynamic_linker.snap(self.name)
        if segment:
            try:
                return getattr(segment, entry_point_name)
            except:
                raise LinkageError(entry_point_name)
        else:
            raise SegmentFault(self.name)
        
    def __repr__(self):
        return "<%s.%s object %s>" % (__name__, self.__class__.__name__, self.name)
    
class Injector(object):
    """
    This class injects objects into the calling frame's global namespace with a given name.
    These objects can then be used as functions or function 'output' parameters.
    """
    def __init__(self):
        pass
        
    #== This is for making the 'declare . foo' coding pattern available
    def __getattr__(self, fn_name):
        Injector.inject_func(Injector.find_pframe(), fn_name, call)
        
    @staticmethod
    def inject_func(pframe, name, dynamic_linker):
        if pframe:
            fn = LinkageReference(name, dynamic_linker)
            # print "Injecting", fn, "into", pframe.f_globals['__name__'], "as", name
            pframe.f_globals.update({name:fn})
        # end if
        
    @staticmethod
    def inject_parm(pframe, name, initial_value=None):
        if pframe:
            p = parameter(initial_value)
            if initial_value is not None:
                with_init_string = "with initial value {0}".format(initial_value)
            else:
                with_init_string = ""
            # print "Injecting", p, "into", pframe.f_globals['__name__'], "as", name, with_init_string
            pframe.f_globals.update({name:p})
        # end if
        
    @staticmethod
    def inject_incl(pframe, name):
        if pframe:
            module = __import__(name)
            for member_name in dir(module):
                if re.match("__\w+__", member_name):
                    # print "Injector skipping", member_name
                    continue
                # end if
                member_object = getattr(module, member_name)
                if member_name == name + "_structure":
                    member_object = member_object()
                    # print "Injecting", member_object, "into", pframe.f_globals['__name__'], "as", name
                    # pframe.f_globals[name] = member_object
                    pframe.f_globals.update({name:member_object})
                else:
                    # print "Injecting", member_name, "into", pframe.f_globals['__name__'], "with value", member_object
                    # pframe.f_globals[member_name] = member_object
                    pframe.f_globals.update({member_name:member_object})
                # end if
            # end for
        # end if
        
    @staticmethod
    def inject_local(pframe, name, initial_value):
        if pframe:
            print "Injecting", name, "into", pframe.f_globals['__name__'], "with initial value", repr(initial_value)
            pframe.f_globals.update({name:initial_value})
        
    @staticmethod
    def find_pframe():
        import inspect
        cframe = inspect.currentframe()
        # print "...stepping back from", cframe.f_globals['__name__']+"."+cframe.f_code.co_name
        pframe = cframe.f_back
        while pframe and pframe.f_globals['__name__'] == __name__:
            # print "...stepping back from", pframe.f_globals['__name__']+"."+pframe.f_code.co_name
            pframe = pframe.f_back
        # end while
        return pframe
        
class alloc(object):
    def __init__(self, objtype):
        setattr(self, objtype.__name__, objtype())

def null():
    return None
    
class declare(object):
    #== We only want declare objects for their side effects during construction. It
    #== is expected that the instantiated object won't even be assigned to anything.
    #== Example:
    #==
    #==     declare (get_pdir = entry.returns (charstar),
    #==              acl_list = parm,
    #==              code     = parm)
    #==
    def __init__(self, **kwargs):
        pframe = Injector.find_pframe()
        for fn_name, dcl_type in kwargs.items():
            if dcl_type is parameter:
                #== Creates and injects a parm object
                Injector.inject_parm(pframe, fn_name)
            elif type(dcl_type) is parameter_with_init:
                #== Creates and injects a parm object with an initial value
                Injector.inject_parm(pframe, fn_name, dcl_type.initial_value)
            elif type(dcl_type) in [PL1.FuncSignature, PL1.ProcSignature]:
                #== Creates and injects a LinkageReference object
                Injector.inject_func(pframe, fn_name, call)
            elif type(dcl_type) == PL1.Type:
                #== Creates and injects a PL1.Type local variable converted to a python type
                name, initial_value = fn_name, dcl_type.toPython()
                print "declaring", name, dcl_type
                Injector.inject_local(pframe, name, initial_value)
            else:
                #== Creates a normal (python type) local variable
                name, initial_value = fn_name, dcl_type
                Injector.inject_local(pframe, name, initial_value)
        
dcl = declare

class parameter_with_init(object):
    def __init__(self, initial_value):
        self.initial_value = initial_value
        
class parameter(object):

    def __init__(self, initial_value=None):
        self.value = initial_value
        
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
        # end if
        
    @staticmethod
    def init(initial_value):
        return parameter_with_init(initial_value)
        
    @staticmethod
    def initialize(initial_value):
        return parameter_with_init(initial_value)
        
    # def __repr__(self):
        # s = str(self.value)
        # if len(s) > 50:
            # s = s[:48] + "..."
        # return "<%s.%s object: %s>" % (__name__, self.__class__.__name__, s[:51])

parm = parameter

class Includer(object):
    def __init__(self):
        pass
        
    def __getattr__(self, include_name):
        pframe = Injector.find_pframe()
        Injector.inject_incl(pframe, include_name)
        
include = Includer()

def traceback_print_exc():
    import traceback
    traceback.print_exc()
    