
from multics.globals import *

class set_lock_(SystemSubroutine):
    def __init__(self, supervisor):
        super(set_lock_, self).__init__(self.__class__.__name__, supervisor)
        
    def lock(self, lock_word, wait_time, code):
        process = get_calling_process_()
        self.supervisor.hardware.acquire_hardware_lock(lock_word, process.id(), wait_time, code)
    
    def unlock(self, lock_word, code):
        process = get_calling_process_()
        self.supervisor.hardware.release_hardware_lock(lock_word, process.id(), code)
