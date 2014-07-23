import os
import re
import types
import inspect
import datetime
import contextlib
import __builtin__

from pl1types import *

from PySide import QtCore

#== Functions normally provided by PL/1 ==#

def before(s, p):
    return s.partition(p)[0]

def after(s, p):
    return s.partition(p)[-1]

def verify(s, p):
    for i, c in enumerate(s):
        if not c in p:
            return i + 1
    return 0
    
def vfile_(multics_path):
    return GlobalEnvironment.supervisor.fs.path2path(multics_path)

def alloc(objtype):
    if type(objtype) is PL1.Structure:
        return objtype.copy()
    elif type(objtype) is BasedPointer:
        return objtype.alloc()
    else:
        return objtype()
    
def addr(obj):
    return obj
    
def mod(x, y):
    return x % y
    
#== Conditions represented by exception classes ==#

def continue_to_signal_(code):
    raise
    
class MulticsCondition(Exception):
    def __init__(self, arg=""):
        super(MulticsCondition, self).__init__(arg)
    
class BreakCondition(MulticsCondition):
    def __init__(self):
        super(BreakCondition, self).__init__()
    @staticmethod
    def name(): return "BreakCondition"
    
@contextlib.contextmanager
def on_quit(handler_function):
    process = get_calling_process_()
    try:
        GlobalEnvironment.supervisor.register_condition_handler(BreakCondition, process, handler_function)
        yield
    finally:
        GlobalEnvironment.supervisor.deregister_condition_handler(BreakCondition, process)

class ShutdownCondition(MulticsCondition):
    def __init__(self):
        super(ShutdownCondition, self).__init__()
    @staticmethod
    def name(): return "ShutdownCondition"

class DisconnectCondition(MulticsCondition):
    def __init__(self):
        super(DisconnectCondition, self).__init__()
    @staticmethod
    def name(): return "DisconnectCondition"

@contextlib.contextmanager
def on_finish(handler_function):
    process = get_calling_process_()
    try:
        GlobalEnvironment.supervisor.register_condition_handler(DisconnectCondition, process, handler_function)
        GlobalEnvironment.supervisor.register_condition_handler(ShutdownCondition, process, handler_function)
        yield
    finally:
        GlobalEnvironment.supervisor.deregister_condition_handler(ShutdownCondition, process)
        GlobalEnvironment.supervisor.deregister_condition_handler(DisconnectCondition, process)

class SegmentFault(MulticsCondition):
    def __init__(self, entry_point_name):
        super(SegmentFault, self).__init__("segment not found %s" % (entry_point_name))
        self.segment_name = entry_point_name
    @staticmethod
    def name(): return "SegmentFault"
            
@contextlib.contextmanager
def on_seg_fault_error(handler_function):
    process = get_calling_process_()
    try:
        GlobalEnvironment.supervisor.register_condition_handler(SegmentFault, process, handler_function)
        yield
    finally:
        GlobalEnvironment.supervisor.deregister_condition_handler(SegmentFault, process)

class LinkageError(MulticsCondition):
    def __init__(self, segment_name, entry_point_name):
        super(LinkageError, self).__init__("entry not found %s.%s" % (segment_name, entry_point_name))
        self.entry_point_name = entry_point_name

class InvalidSegmentFault(MulticsCondition):
    def __init__(self, entry_point_name):
        super(InvalidSegmentFault, self).__init__("invalid segment %s" % (entry_point_name))
        self.segment_name = entry_point_name

class NonLocalGoto(Exception):
    def __init__(self, arg=""):
        super(NonLocalGoto, self).__init__(arg)
        
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
    no_command_name_available = -15,
    no_search_list = -16,
    new_search_list = -17,
    action_not_performed = -18,
    noentry = -19,
)

class Subroutine(QtCore.QObject):
    """
    Subroutines are created within the SegmentDescriptor constructor to
    represent both procedure$entrypoint executables and pure functions.
    """
    def __init__(self, segment_name, fn=None):
        super(Subroutine, self).__init__()
        
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
            return super(Subroutine, self).__repr__()
    
class SystemSubroutine(Subroutine):
    def __init__(self, segment_name, supervisor):
        super(SystemSubroutine, self).__init__(segment_name)
        
        self.supervisor = supervisor
        
class CommandProcessor(Subroutine):
    def __init__(self, segment_name):
        super(CommandProcessor, self).__init__(segment_name)
        
    def execute(self):
        raise LinkageError(self.__segment_name, "execute (command processor entry point)")

class DataSegment(object):
    pass
    
def print_stackframes():
    def _print_pframe(pframe, indent=""):
        if pframe:
            indent = _print_pframe(pframe.f_back, indent)
            module_name = re.sub("_\w{15}$", "", pframe.f_globals['__name__'])
            function_name = pframe.f_code.co_name
            print indent, "%s.%s (line %d)" % (module_name, function_name, pframe.f_lineno)
            # print indent, pframe.f_globals['__name__']+"."+pframe.f_code.co_name+" (line "+str(pframe.f_lineno)+")"
        return indent + " "
        
    import inspect
    print "Calling frame stack:"
    _print_pframe(inspect.currentframe())
    
# def _find_pframe():
    # import inspect
    # cframe = inspect.currentframe()
    # # print "...stepping back from", cframe.f_globals['__name__']+"."+cframe.f_code.co_name
    # pframe = cframe.f_back
    # while pframe and pframe.f_globals['__name__'] == __name__:
        # # print "...stepping back from", pframe.f_globals['__name__']+"."+pframe.f_code.co_name
        # pframe = pframe.f_back
    # # end while
    # return pframe
    
# call = None

class GlobalEnvironment(object):

    supervisor = None
    hardware   = None
    linker     = None
    fs         = None
    
    @staticmethod
    def register_filesystem(filesystem):
        GlobalEnvironment.fs         = filesystem
        
    @staticmethod
    def register_supervisor(supervisor):
        GlobalEnvironment.supervisor = supervisor
        GlobalEnvironment.hardware   = supervisor.hardware
        GlobalEnvironment.linker     = supervisor.dynamic_linker
        # global call
        # call = supervisor.dynamic_linker
        __builtin__.__dict__['call'] = supervisor.dynamic_linker
        
    @staticmethod
    def deregister_supervisor():
        GlobalEnvironment.supervisor = None
        GlobalEnvironment.hardware   = None
        GlobalEnvironment.linker     = None
        # global call
        # call = None
        __builtin__.__dict__['call'] = None

def call_(entryname):
    """
    call_ is an alternate way to invoke the dynamic linker on an entry name.
    Ex: call_('hcs_$initiate') (dir_name, entryname, ...)
    """
    procedure_name, _, entry_name = entryname.partition("$")
    subroutine = GlobalEnvironment.supervisor.dynamic_linker.snap(procedure_name)
    if subroutine:
        if entry_name:
            return getattr(subroutine, entry_name)
        else:
            return subroutine
    else:
        raise SegmentFault(procedure_name)

def check_conditions_(ignore_break_signal=False):
    if GlobalEnvironment.supervisor.hardware.io.terminal_closed():
        raise DisconnectCondition
    # end if
    if (not ignore_break_signal and
        GlobalEnvironment.supervisor.hardware.io.break_received()):
        
        ### ! EXPERIMENTAL ! ###
        process = get_calling_process_()
        GlobalEnvironment.supervisor.llout("QUIT\n", process.tty())
        GlobalEnvironment.supervisor.invoke_condition_handler(BreakCondition, process)
        
        # raise BreakCondition
    # end if
    if GlobalEnvironment.supervisor.shutting_down():
        raise ShutdownCondition
    # end if
    if GlobalEnvironment.supervisor.condition_signalled():
        condition_instance = GlobalEnvironment.supervisor.pop_condition()
        raise condition_instance
    # end if

    QtCore.QCoreApplication.processEvents()
    
@contextlib.contextmanager
def do_loop(container, ignore_break_signal=False):
    # container.exit_code = 0
    try:
        if GlobalEnvironment.supervisor.hardware.io.terminal_closed():
            container.exit_code = System.LOGOUT
        # end if
        if (not ignore_break_signal and
            GlobalEnvironment.supervisor.hardware.io.break_received()):
            print "Break signal detected by", container
            call.hcs_.signal_break()
        # end if
        if GlobalEnvironment.supervisor.shutting_down():
            container.exit_code = System.SHUTDOWN
            print "Shutdown signal detected by", container
        # end if
        if GlobalEnvironment.supervisor.condition_signalled():
            condition_instance = GlobalEnvironment.supervisor.pop_condition()
            print type(condition_instance), "signal detected by " + container
            raise condition_instance
        # end if
        
        QtCore.QCoreApplication.processEvents()
        
        yield
        
    except NonLocalGoto:
        raise
    except (SegmentFault, LinkageError, InvalidSegmentFault):
        call.dump_traceback_()
        container.exit_code = -1
    except:
        #== FOR DEBUGGING THE SIMULATION
        call.dump_traceback_()
        container.exit_code = -1
    # end try
    
def system_privileged(fn):
    def decorated(*args, **kw):
        fn.__globals__['supervisor'] = GlobalEnvironment.supervisor
        return fn(*args, **kw)
    decorated.__name__ = fn.__name__
    return decorated

def get_calling_process_():
    calling_process = QtCore.QThread.currentThread()
    if calling_process.objectName() == "Multics.Supervisor":
        return GlobalEnvironment.supervisor
    else:
        return calling_process

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
            # end try
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
        
    @staticmethod
    def import_module(name):
        import sys
        try:
            process = get_calling_process_()
            search_paths = process.search_paths
        except:
            search_paths = []
        # end try
        search_paths.append(GlobalEnvironment.fs.system_library_standard + ">includes")
        
        for include_path in search_paths:
            sys.path.append(GlobalEnvironment.fs.path2path(include_path))
                
        module = __import__(name, globals(), locals(), ())
        
        for include_path in search_paths:
            sys.path.remove(GlobalEnvironment.fs.path2path(include_path))
        
        return module
    
    @staticmethod
    def inject_func(pframe, name, dynamic_linker):
        if pframe:
            fn = LinkageReference(name, dynamic_linker)
            # print "Injecting", fn, "into", pframe.f_globals['__name__'], "as", name
            pframe.f_globals.update({name:fn})
    
    @staticmethod
    def inject_data(pframe, name):
        if pframe:
            module = Injector.import_module(name)
            for member_name in dir(module):
                if member_name != name:
                    # print "Injector skipping", member_name
                    continue
                # end if
                member_object = getattr(module, member_name)
                # print "Injecting", member_name, "into", pframe.f_globals['__name__']
                pframe.f_globals.update({member_name:member_object})
        
    @staticmethod
    def inject_parm(pframe, name, initial_value=None):
        if pframe:
            p = parameter(initial_value)
            # if initial_value is not None:
                # with_init_string = "with initial value {0}".format(initial_value)
            # else:
                # with_init_string = ""
            # print "Inject {0} into {1} module GLOBALS as {2} {3}", p, pframe.f_globals['__name__'], name, with_init_string
            pframe.f_globals.update({name:p})
        
    @staticmethod
    def inject_incl(pframe, name):
        if pframe:
            # module = __import__(name, globals(), locals(), ())
            module = Injector.import_module(name)
            for member_name in dir(module):
                if re.match("__\w+__", member_name):
                    # print "Injector skipping", member_name
                    continue
                # end if
                member_object = getattr(module, member_name)
                
                if (type(member_object) is type and 
                    hasattr(member_object, "__bases__") and # <-- can be fooled by instances of classes implementing __getattr__
                    PL1.Structure in inspect.getmro(member_object)):
                    
                    member_object = member_object()
                    # print "Injecting", member_object, "into", pframe.f_globals['__name__'], "as", name
                    pframe.f_globals.update({name:member_object})
                else:
                    # print "Injecting", member_name, "into", pframe.f_globals['__name__'], "with value", member_object
                    pframe.f_globals.update({member_name:member_object})
        
    @staticmethod
    def inject_local(pframe, name, initial_value):
        if pframe:
            if name in pframe.f_globals and type(pframe.f_globals[name]) is BasedStructure:
                print name, "already injected as a based structure pointer in", pframe.f_globals['__name__']
                # pframe.f_locals.update({name:initial_value})
                based_struct = pframe.f_globals[name]
                based_ptr_item = based_struct.based_ptr_item()
                pframe.f_locals.update(based_ptr_item)
                #== This is an amazingly dirty python hack, but necessary in order to update the local variable
                #== dictionary in the calling frame.
                import ctypes
                ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(pframe), ctypes.c_int(0))
            else:
                # print "Injecting", name, "into", pframe.f_globals['__name__'], "with initial value", repr(initial_value)
                pframe.f_globals.update({name:initial_value})
        
    @staticmethod
    def find_pframe():
        cframe = inspect.currentframe()
        # print "...stepping back from", cframe.f_globals['__name__']+"."+cframe.f_code.co_name
        pframe = cframe.f_back
        while pframe and pframe.f_globals['__name__'] == __name__:
            # print "...stepping back from", pframe.f_globals['__name__']+"."+pframe.f_code.co_name
            pframe = pframe.f_back
        # end while
        return pframe
        
def null():
    return None
    
subsystem_request = staticmethod

class declare(object):
    #== We only want declare objects for their side effects during construction. It
    #== is expected that the instantiated object won't even be assigned to anything.
    #== Example:
    #==
    #==     declare (get_pdir_ = entry . returns (char ('*')),
    #==              acl_list  = parm,
    #==              code      = parm)
    #==
    def __init__(self, **kwargs):
        self.global_decls = ""
        pframe = Injector.find_pframe()
        for fn_name, dcl_type in kwargs.items():
            if dcl_type is parameter:
                #== Creates and injects a parm object
                Injector.inject_parm(pframe, fn_name)
            elif isinstance(dcl_type, parameter):
                #== Creates and injects a parm object with an initial value
                Injector.inject_parm(pframe, fn_name, dcl_type.initial_value)
            elif type(dcl_type) in [PL1.FuncSignature, PL1.ProcSignature]:
                #== Creates and injects a LinkageReference object. Inclusion of
                #== PL1.ProcSignature here allows methods inside Subroutine
                #== objects to be called with regular function call syntax.
                Injector.inject_func(pframe, fn_name, call)
            elif type(dcl_type) is PL1.DataSegment:
                #== Creates and injects a data segment
                Injector.inject_data(pframe, fn_name)
            else:
                # print "declaring", fn_name, dcl_type
                #== Creates and injects a local variable
                Injector.inject_local(pframe, fn_name, self.get_initial_value(dcl_type))
                
    def get_initial_value(self, initial_value):
        if type(initial_value) is PL1.Type:
            return initial_value.toPython()
        elif initial_value is PL1.File:
            return PL1.File()
        elif type(initial_value) is list:
            return list( self.get_initial_value(t) for t in initial_value )
        elif type(initial_value) is tuple:
            return tuple( self.get_initial_value(t) for t in initial_value )
        else:
            return initial_value
        
dcl = declare

class Includer(object):
    def __init__(self):
        pass
        
    def __getattr__(self, include_name):
        # print "INCLUDE."+include_name
        pframe = Injector.find_pframe()
        Injector.inject_incl(pframe, include_name)
        
include = Includer()

class ProcessMessage(dict):
    def __init__(self, msgtype, **fields):
        # msg_data = {
            # 'type': msgtype,
            # 'time': datetime.datetime.now(),
        # }
        super(ProcessMessage, self).__init__(fields)
        self['type'] = msgtype
        self['time'] = datetime.datetime.now()
