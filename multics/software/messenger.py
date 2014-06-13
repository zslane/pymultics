
from ..globals import *

class Messenger(SystemExecutable):

    def __init__(self, supervisor, command_processor):
        super(Messenger, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        self.__process = None
        self.__mbx = None
        self.exit_code = 0
        
    def start(self, owning_process):
        self.__process = owning_process
        return self._main_loop()
        
    def kill(self):
        self._cleanup()
        
    def _main_loop(self):
        self._initialize()
        
        while self.exit_code == 0:
            with do_loop(self):
                pass
            # end with
            QtCore.QThread.msleep(200)
        # end while
        
        # do any cleanup necessary at the core function level
        self._cleanup()
        
        return self.exit_code
        
    def _on_condition__break(self):
        pass
        
    def _initialize(self):
        self.__mbx = self.__process.mbx()
        mbx_handlers = {
            'interactive_message': self._interactive_message_handler,
            'shutdown_announcement': self._interactive_message_handler,
            # 'shutdown': self._interactive_message_handler,
        }
        self.__process.register_mbx_handlers(mbx_handlers)
        
    def _cleanup(self):
        pass
        
    def _interactive_message_handler(self, mbx_message):
        declare (users = parm)
        
        print self.__process.objectName(), "handling message", mbx_message
        
        call.sys_.get_users(users, mbx_message['to'])
        for user_id in users.list:
            self._deliver_interactive_message(user_id, mbx_message)
        
    def _deliver_interactive_message(self, recipient, mbx_message):
        declare (mbx_segment = parm,
                 code        = parm)
                 
        mbx_message['to'] = recipient
        
        try:
            call.sys_.lock_process_mbx_(recipient, mbx_segment, code)
            if code.val != 0:
                print "Could not lock %s" % mbx_segment.ptr.filepath
                print "  code =", code.val
                return
            # end if
            
            print self.__process.uid(), "delivering interactive message to", recipient
            
            process_mbx = mbx_segment.ptr
            with process_mbx:
                process_mbx.messages.append(mbx_message)
            # end with
            
        finally:
            call.sys_.unlock_process_mbx_(mbx_segment.ptr, code)
            if code.val != 0:
                print "Could not unlock %s" % mbx_segment.ptr.filepath
                print "  code =", code.val
            # end if
            