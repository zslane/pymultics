
from ..globals import *

class Messenger(SystemExecutable):

    def __init__(self, supervisor, command_processor):
        super(Messenger, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        # self.__default_command_processor = command_processor
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
                self._process_mbx()
            # end with
        # end while
        
        # do any cleanup necessary at the core function level
        self._cleanup()
        
        return self.exit_code
        
    def _on_condition__break(self):
        pass
        
    def _initialize(self):
        self.__mbx = self.__process.mbx()
    
    def _process_mbx(self):
        try:
            if self.__mbx.messages:
                #== Process mbx messages one per main loop iteration
                with self.__mbx:
                    next_message = self.__mbx.messages.pop(0)
                # end with
                self._dispatch_mbx_message(next_message)
            # end if
        except:
            print "ERROR in messenger._process_mbx()!"
            print type(self.__mbx)
            self.exit_code = -1
            
    def _cleanup(self):
        pass
        
    def _dispatch_mbx_message(self, mbx_message):
        declare (users = parm)
        
        print self.__process.objectName(), "process message found", mbx_message
        
        if mbx_message['type'] == "user_message_request" or mbx_message['type'] == "shutdown_announcement":
            call.sys_.get_users(users, mbx_message['to'])
            for user_id in users.list:
                self._deliver_user_message(user_id, mbx_message)
            # end for
        
    def _deliver_user_message(self, recipient, mbx_message):
        declare (mbx_segment = parm,
                 code        = parm)
                 
        call.sys_.lock_process_mbx_(recipient, mbx_segment, code)
        if code.val != 0:
            return
        # end if
        print self.__process.uid(), "delivering user message to", recipient
        process_mbx = mbx_segment.ptr
        with process_mbx:
            if mbx_message['type'] == "user_message_request":
                mbx_message['type'] = "user_message_delivery"
            # end if
            mbx_message['to'] = recipient
            process_mbx.messages.append(mbx_message)
        # end with
        call.sys_.unlock_process_mbx_(process_mbx, code)
        