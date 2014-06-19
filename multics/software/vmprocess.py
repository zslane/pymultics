import datetime

from ..globals import *

from PySide import QtCore, QtGui

class ProcessWorker(QtCore.QObject):

    PROCESS_TIMER_DURATION = 1.0
    
    def __init__(self, supervisor, process_env):
        super(ProcessWorker, self).__init__()
        self.supervisor = supervisor
        self.__process_env = process_env
        self.__known_segment_table = {}
        self.__timerid = 0
        self.__registered_msg_handlers = {}
        self.exit_code = 0
        
        self.setObjectName(self.uid() + ".Worker")
        self.__process_env.core_function.setParent(self)
        
    def __repr__(self):
        return "<%s.%s %s>" % (__name__, self.__class__.__name__, self.objectName())
    
    @property
    def stack(self):
        return self.__process_env.pds.process_stack
        
    @property
    def search_paths(self):
        try:
            declare (resolve_path_symbol_ = entry . returns (char(168)))
            search_paths = self.__process_env.pds.process_stack.search_seg_ptr.paths['objects'].paths
            return [ resolve_path_symbol_(p.pathname) for p in search_paths ]
        except:
            return [">sss", ">sss>commands"]
    
    @property
    def directory_stack(self):
        return self.__process_env.rnt.working_dir
        
    def id(self):
        return self.__process_env.process_id
        
    def dir(self):
        return self.__process_env.process_dir
        
    def kst(self):
        return self.__known_segment_table
        
    def pds(self):
        return self.__process_env.pds
        
    def rnt(self):
        return self.__process_env.rnt
        
    def pit(self):
        return self.__process_env.pit
        
    def msg(self):
        return self.__process_env.msg
        
    def uid(self):
        return "%s.%s" % (self.__process_env.pit.login_name, self.__process_env.pit.project)
        
    def gid(self):
        return "%s.%s.%s" % (self.__process_env.pit.login_name, self.__process_env.pit.project, self.__process_env.pit.instance_tag)
        
    @QtCore.Slot()
    def start(self):
        self._initialize()
        
        self.exit_code = self._main_loop()
        
        # do any cleanup necessary at the VirtualMulticsProcess level
        self._cleanup()
        
    def kill(self):
        print QtCore.QThread.currentThread().objectName(), "executing kill() method"
        self.__process_env.core_function.kill()
        # self._cleanup()
    
    def timerEvent(self, event):
        # print QtCore.QThread.currentThread().objectName(), "timerEvent!"
        self._process_timers()
    
    def register_msg_handlers(self, handler_table):
        self.__registered_msg_handlers.update(handler_table)
    
    @QtCore.Slot()
    def _process_messages(self):
        declare (code = parm)
        next_message = ""
        # print QtCore.QThread.currentThread().objectName(), "executing _process_messages()"
        
        if self.__process_env.msg.messages:
            call.timer_manager_.reset_alarm_call(self._process_messages)
            
            #== Process msg messages one per timer trigger ==#
            try:
                # print self.objectName()+"._process_messages calling set_lock_.lock"
                call.set_lock_.lock(self.__process_env.msg, 3, code)
                if code.val != 0:
                    print "Could not lock %s" % self.__process_env.msg.filepath
                    return
                # end if
                
                with self.__process_env.msg:
                    next_message = self.__process_env.msg.messages.pop(0)
                # end with
                
            finally:
                # print self.objectName()+"._process_messages calling set_lock_.unlock"
                call.set_lock_.unlock(self.__process_env.msg, code)
                if code.val != 0:
                    print "Could not unlock %s" % self.__process_env.msg.filepath
                    return
                # end if
            # end try
            
            if next_message:
                self._dispatch_msg_message(next_message)
            # end if
            
            call.timer_manager_.alarm_call(self.PROCESS_TIMER_DURATION, self._process_messages)
    
    def _main_loop(self):
        self.supervisor.llout("New process for %s started on %s\n" % (self.uid(), datetime.datetime.now().ctime()))
        code = self.__process_env.core_function.start(self)
        return code
    
    def _on_condition__break(self):
        self.__process_env.core_function._on_condition__break()
        
    def _initialize(self):
        #== Create the internal process heartbeat timer. It processes the high-level
        #== 'process timers', created with timer_manager_.
        HEARTBEAT_PERIOD = 250
        self.__timerid = self.startTimer(HEARTBEAT_PERIOD)
        
        #== Start the event MBX process timer
        call.timer_manager_.alarm_call(self.PROCESS_TIMER_DURATION, self._process_messages)
        
        #== Create default search paths and store them in the process stack
        declare (search_seg = parm,
                 code = parm)
        call.search_paths_.set("objects", null(), null(), code)
        call.hcs_.initiate(self.dir(), "search_paths", search_seg, code)
        self.__process_env.pds.process_stack.search_seg_ptr = search_seg.ptr
    
    def _process_timers(self):
        for routine_key in self.stack.process_timers.keys():
            timer = self.stack.process_timers[routine_key]
            if timer.dead():
                del self.stack.process_timers[routine_key]
            else:
                timer.check()
        
    def _cleanup(self):
        #== Kill the MBX process timer
        call.timer_manager_.reset_alarm_call(self._process_messages)
        # if self.__timerid:
            # self.killTimer(self.__timerid)
            # self.__timerid = 0
        print QtCore.QThread.currentThread().objectName() + " process terminating"
        
    def _dispatch_msg_message(self, msg_message):
        print "(%s)" % (get_calling_process_().objectName()), self.objectName(), "process message found", msg_message
        handler = self.__registered_msg_handlers.get(msg_message['type'])
        if handler:
            handler(msg_message)
    
#-- end class ProcessWorker

class ProcessThread(QtCore.QThread):

    def __init__(self, worker):
        super(ProcessThread, self).__init__()
        
        self.worker = worker
        
        self.setObjectName(self.worker.uid() + ".Thread")
        
    @property
    def stack(self):
        return self.worker.stack
        
    @property
    def search_paths(self):
        return self.worker.search_paths
        
    @property
    def directory_stack(self):
        return self.worker.directory_stack
        
    def id(self):
        return self.worker.id()
        
    def dir(self):
        return self.worker.dir()
        
    def kst(self):
        return self.worker.kst()
        
    def pds(self):
        return self.worker.pds()
        
    def rnt(self):
        return self.worker.rnt()
        
    def pit(self):
        return self.worker.pit()
        
    def msg(self):
        return self.worker.msg()
        
    def uid(self):
        return self.worker.uid()
        
    def gid(self):
        return self.worker.gid()
          
#-- end class ProcessThread

class VirtualMulticsProcess(QtCore.QObject):

    def __init__(self, supervisor, process_env):
        super(VirtualMulticsProcess, self).__init__()
        
        self.worker = ProcessWorker(supervisor, process_env)
        self.thread = ProcessThread(self.worker)
        
        self.thread.finished.connect(self._thread_finished)
        
        self.worker.moveToThread(self.thread)
        self.thread.start()
        
        self.setObjectName(self.worker.gid())
        
    def _thread_finished(self):
        print self.thread.objectName() + " finished signal detected"
        
    def start(self):
        QtCore.QMetaObject.invokeMethod(self.worker, "start", QtCore.Qt.QueuedConnection)
        
    def kill(self):
        print self.objectName() + ".kill() called"
        self.worker.deleteLater()
        self.thread.quit()
        
    def wait(self, *args, **kwargs):
        return self.thread.wait(*args, **kwargs)
        
    def isRunning(self):
        return self.thread.isRunning()
        
    def __repr__(self):
        return "<%s.%s %s>" % (__name__, self.__class__.__name__, self.objectName())
        # return repr(self.worker)
    
    @property
    def stack(self):
        return self.worker.stack
        
    @property
    def search_paths(self):
        return self.worker.search_paths
        
    @property
    def directory_stack(self):
        return self.worker.directory_stack
        
    @property
    def exit_code(self):
        return self.worker.exit_code
        
    def id(self):
        return self.worker.id()
        
    def dir(self):
        return self.worker.dir()
        
    def kst(self):
        return self.worker.kst()
        
    def pds(self):
        return self.worker.pds()
        
    def rnt(self):
        return self.worker.rnt()
        
    def pit(self):
        return self.worker.pit()
        
    def msg(self):
        return self.worker.msg()
        
    def uid(self):
        return self.worker.uid()
        
    def gid(self):
        return self.worker.gid()
        
    