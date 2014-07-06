
from ..globals import *

class Messenger(SystemSubroutine):

    def __init__(self, supervisor, command_processor):
        super(Messenger, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        self.__process = None
        self.exit_code = 0
        
    def start(self, owning_process):
        self.__process = owning_process
        return self._main_loop()
        
    def kill(self):
        # self._cleanup()
        self.exit_code = self.exit_code or System.LOGOUT
        
    def _main_loop(self):
        self._initialize()
        
        while self.exit_code == 0:
            with do_loop(self, ignore_break_signal=True):
                QtCore.QThread.msleep(200)
            # end with
        # end while
        
        # do any cleanup necessary at the core function level
        self._cleanup()
        
        return self.exit_code
        
    def _initialize(self):
        msg_handlers = {
            'interactive_message': self._interactive_message_handler,
            'shutdown_announcement': self._interactive_message_handler,
        }
        self.__process.register_msg_handlers(msg_handlers)
        
    def _cleanup(self):
        pass
        
    def _interactive_message_handler(self, message):
        user_ids = parm()
        homedirs = parm()
        
        print self.__process.objectName(), "handling message", message
        call.sys_.get_registered_users(user_ids, homedirs, message['to'])
        for user_id, homedir in zip(user_ids.list, homedirs.list):
            self._deliver_interactive_message(user_id, homedir, message)
        # end for
    
    def _deliver_interactive_message(self, recipient, homedir, message):
        declare (clock_ = entry . returns (fixed.bin(32)))
        mbx_segment = parm()
        code        = parm()
        
        print self.__process.uid(), "delivering interactive message to", recipient
        message['id'] = clock_()
        message['to'] = recipient
        message['status'] = "unread"
        call.sys_.lock_user_mbx_(recipient, homedir, mbx_segment, code)
        if mbx_segment.ptr != null():
            with mbx_segment.ptr:
                mbx_segment.ptr.add_message(message)
            # end with
            call.sys_.unlock_user_mbx_(mbx_segment.ptr, code)
        # end if
