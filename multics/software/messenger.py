
from ..globals import *

class Messenger(SystemExecutable):

    def __init__(self, supervisor, command_processor):
        super(Messenger, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        self.__process = None
        self.exit_code = 0
        
    def start(self, owning_process):
        self.__process = owning_process
        return self._main_loop()
        
    def kill(self):
        self._cleanup()
        
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
        
    def _on_condition__break(self):
        pass
        
    def _initialize(self):
        msg_handlers = {
            'interactive_message': self._interactive_message_handler,
            'shutdown_announcement': self._interactive_message_handler,
            'shutdown': self._interactive_message_handler,
        }
        self.__process.register_msg_handlers(msg_handlers)
        
    def _cleanup(self):
        pass
        
    def _interactive_message_handler(self, message):
        users = parm()
        
        print self.__process.objectName(), "handling message", message
        
        call.sys_.get_users(users, message['to'])
        for user_id in users.list:
            self._deliver_interactive_message(user_id, message)
    
    def _deliver_interactive_message(self, recipient, message):
        code = parm()
        print self.__process.uid(), "delivering interactive message to", recipient
        message['to'] = recipient
        call.sys_.add_process_msg(recipient, message, code)
        