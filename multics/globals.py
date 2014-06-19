import os
import re
import types
import inspect
import datetime
import contextlib
# from contextlib import contextmanager

from pl1types import *

from PySide import QtCore

class MulticsCondition(Exception):
    def __init__(self, arg=""):
        super(MulticsCondition, self).__init__(arg)
    
class BreakCondition(MulticsCondition):
    def __init__(self):
        super(BreakCondition, self).__init__()
        
class ShutdownCondition(MulticsCondition):
    def __init__(self):
        super(ShutdownCondition, self).__init__()

class DisconnectCondition(MulticsCondition):
    def __init__(self):
        super(DisconnectCondition, self).__init__()

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
    no_command_name_available = -15,
    no_search_list = -16,
    new_search_list = -17,
    action_not_performed = -18,
    noentry = -19,
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
        
class CommandProcessor(Executable):
    def __init__(self, segment_name):
        super(CommandProcessor, self).__init__(segment_name)
        
    def execute(self):
        raise LinkageError(self.__segment_name, "execute (command processor entry point)")

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
    
# _system_services = None
call = None

class GlobalEnvironment(object):

    supervisor    = None
    async_process = None
    
    @staticmethod
    def register_system_services(supervisor, dynamic_linker):
        GlobalEnvironment.supervisor = supervisor
        global call
        call = dynamic_linker

def check_conditions_(ignore_break_signal=False):
    if GlobalEnvironment.supervisor.hardware.io.terminal_closed():
        raise DisconnectCondition
    # end if
    if (not ignore_break_signal and
        GlobalEnvironment.supervisor.hardware.io.break_received()):
        raise BreakCondition
    # end if
    if GlobalEnvironment.supervisor.shutting_down():
        raise ShutdownCondition
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
            
        QtCore.QCoreApplication.processEvents()

        yield
        
    # except ShutdownCondition:
        # container.exit_code = System.SHUTDOWN
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
        # my_globals={}
        # my_globals.update(fn.__globals__)
        # my_globals['system'] = _system_services
        # call_fn = types.FunctionType(fn.func_code, my_globals)
        # return call_fn(*args, **kw)
        fn.__globals__['system'] = GlobalEnvironment.supervisor #_system_services
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
    def inject_func(pframe, name, dynamic_linker):
        if pframe:
            fn = LinkageReference(name, dynamic_linker)
            # print "Injecting", fn, "into", pframe.f_globals['__name__'], "as", name
            pframe.f_globals.update({name:fn})
        
    @staticmethod
    def inject_parm(pframe, name, initial_value=None):
        if pframe:
            p = parameter(initial_value)
            # if initial_value is not None:
                # with_init_string = "with initial value {0}".format(initial_value)
            # else:
                # with_init_string = ""
            # print "Injecting", p, "into", pframe.f_globals['__name__'], "as", name, with_init_string
            pframe.f_globals.update({name:p})
        
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
            elif type(dcl_type) is parameter_with_init:
                #== Creates and injects a parm object with an initial value
                Injector.inject_parm(pframe, fn_name, dcl_type.initial_value)
            elif type(dcl_type) in [PL1.FuncSignature, PL1.ProcSignature]:
                #== Creates and injects a LinkageReference object. Inclusion of
                #== PL1.ProcSignature here allows methods inside Executable
                #== objects to be called with regular function call syntax.
                Injector.inject_func(pframe, fn_name, call)
            else:
                # print "declaring", fn_name, dcl_type
                #== Creates and injects a local variable
                Injector.inject_local(pframe, fn_name, self.get_initial_value(dcl_type))
                
    def get_initial_value(self, initial_value):
        if type(initial_value) is PL1.Type:
            return initial_value.toPython()
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
