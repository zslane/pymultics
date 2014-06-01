
from multics.globals import *
            
class timer_manager_(SystemExecutable):
    def __init__(self, system_services):
        super(timer_manager_, self).__init__(self.__class__.__name__, system_services)
        
    def alarm_call(self, time, routine, data_ptr=None):
        timer = self.system.make_timer(time, routine, data_ptr)
        timer.start()
        
    def reset_alarm_call(self, routine):
        self.system.kill_timer(routine)
        