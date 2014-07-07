import datetime

from ..globals import *

from PySide import QtCore, QtGui

class ProcessWorker(QtCore.QObject):

    PROCESS_TIMER_DURATION = 1.0
    
    def __init__(self, supervisor, process_env):
        super(ProcessWorker, self).__init__()
        self.supervisor = supervisor
        self.__process_env = process_env
        self.__registered_msg_handlers = {}
        self.__known_segment_table = {}
        self.__timerid = 0
        self.exit_code = 0
        
        self.setObjectName(self.uid() + ".Worker")
        self.__process_env.core_function.setParent(self)
        
        self.tty_channel = None
        
    def __repr__(self):
        return "<%s.%s %s>" % (__name__, self.__class__.__name__, self.objectName())
    
    @property
    def stack(self):
        return self.__process_env.pds.process_stack[-1]
        
    @property
    def search_paths(self):
        try:
            declare (resolve_path_symbol_ = entry . returns (char(168)))
            search_paths = self.stack.search_seg_ptr.paths['objects'].paths
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
        
    def person_id(self):
        return self.__process_env.pit.login_name
        
    def project_id(self):
        return self.__process_env.pit.project
        
    def homedir(self):
        return self.__process_env.pit.homedir
        
    @QtCore.Slot()
    def start(self):
        self._initialize()
        
        self.exit_code = self._main_loop()
        
        # do any cleanup necessary at the VirtualMulticsProcess level
        self._cleanup()
        
    def kill(self):
        self.__process_env.core_function.kill()
        
    def timerEvent(self, event):
        # print QtCore.QThread.currentThread().objectName(), "timerEvent!"
        self._process_timers()
        
    def register_msg_handlers(self, handler_table):
        self.__registered_msg_handlers.update(handler_table)
        
    def push_stack(self):
        self.__process_env.pds.process_stack.append(self.stack.copy())
        
    def pop_stack(self):
        self.__process_env.pds.process_stack.pop()
    
    def stack_level(self):
        return len(self.__process_env.pds.process_stack)
        
    @QtCore.Slot()
    def _process_messages(self):
        code = parm()
        
        next_message = None
        # print QtCore.QThread.currentThread().objectName(), "executing _process_messages()"
        
        if self.__process_env.msg.messages:
            call.timer_manager_.reset_alarm_call(self._process_messages)
            
            #== Process msg messages one per timer trigger ==#
            try:
                # print self.objectName()+"._process_messages calling set_lock_.lock"
                call.set_lock_.lock(self.__process_env.msg.lock_word(), 3, code)
                if code.val != 0 and code.val != error_table_.invalid_lock_reset:
                    print "Could not lock %s" % self.__process_env.msg._filepath()
                    raise Exception(code.val)
                # end if
                
                with self.__process_env.msg:
                    next_message = self.__process_env.msg.messages.pop(0)
                # end with
                
                # print self.objectName()+"._process_messages calling set_lock_.unlock"
                call.set_lock_.unlock(self.__process_env.msg.lock_word(), code)
                if code.val != 0 and code.val != error_table_.invalid_lock_reset:
                    print "Could not unlock %s" % self.__process_env.msg._filepath()
                # end if
            
                if next_message:
                    self._dispatch_msg_message(next_message)
                # end if
                
            except:
                pass
                
            finally:
                call.timer_manager_.alarm_call(self.PROCESS_TIMER_DURATION, self._process_messages)
            # end try
    
    def _main_loop(self):
        if self.__process_env.pit.instance_tag == "z":
            call.ioa_("New process for {0} started on {1}", self.uid(), datetime.datetime.now().ctime())
        code = self.__process_env.core_function.start(self)
        return code
        
    def _initialize(self):
        search_seg = parm()
        code       = parm()
        
        #== Create the internal process heartbeat timer. It processes the high-level
        #== 'process timers', created with timer_manager_.
        HEARTBEAT_PERIOD = 250
        self.__timerid = self.startTimer(HEARTBEAT_PERIOD)
        
        #== Start the event MBX process timer
        call.timer_manager_.alarm_call(self.PROCESS_TIMER_DURATION, self._process_messages)
        
        #== Create default search paths and store them in the process stack
        call.search_paths_.set("objects", null(), null(), code)
        call.hcs_.initiate(self.dir(), "search_paths", "", 0, 0, search_seg, code)
        self.stack.search_seg_ptr = search_seg.ptr
    
    def _process_timers(self):
        for routine_key in self.stack.process_timers.keys():
            timer = self.stack.process_timers[routine_key]
            if timer.dead():
                del self.stack.process_timers[routine_key]
            else:
                timer.check()
        
    def _cleanup(self):
        print QtCore.QThread.currentThread().objectName() + " process terminating (_cleanup)"
        #== Kill the MBX process timer
        call.timer_manager_.reset_alarm_call(self._process_messages)
        
        # if self.__timerid:
            # self.killTimer(self.__timerid)
            # self.__timerid = 0
            
        if self.tty_channel:
            self.tty_channel.detach_from_process()
        
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
        self.tty_channel = None
        
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
        
    def tty(self):
        return self.tty_channel
        
    def person_id(self):
        return self.worker.person_id()
        
    def project_id(self):
        return self.worker.project_id()
        
    def homedir(self):
        return self.worker.homedir()
    
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
        self.worker.kill()
        self.worker.deleteLater()
        self.thread.quit()
        
    def wait(self, *args, **kwargs):
        return self.thread.wait(*args, **kwargs)
        
    def isRunning(self):
        return self.thread.isRunning()
        
    def attach_tty(self, tty_channel):
        if tty_channel:
            tty_channel.moveToThread(self.thread)
            self.thread.tty_channel = tty_channel
            self.worker.tty_channel = tty_channel
            
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
        
    def tty(self):
        return self.thread.tty()
        
    def person_id(self):
        return self.worker.person_id()
        
    def project_id(self):
        return self.worker.project_id()
        
    def homedir(self):
        return self.worker.homedir()
    