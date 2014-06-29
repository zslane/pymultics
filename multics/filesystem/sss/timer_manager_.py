
from multics.globals import *
            
class timer_manager_(SystemSubroutine):
    def __init__(self, system_services):
        super(timer_manager_, self).__init__(self.__class__.__name__, system_services)
        
    def alarm_call(self, time, routine, data_ptr=None):
        timer = self.system.make_timer(time, routine, data_ptr)
        process = get_calling_process_()
        process.stack.process_timers[routine] = timer
        timer.start()
        
    def reset_alarm_call(self, routine):
        process = get_calling_process_()
        timer = process.stack.process_timers.pop(routine, None)
        if timer:
            timer.kill()
        # end if
        
    def sleep(self, time, flags):
        self.system.sleep(time)
        