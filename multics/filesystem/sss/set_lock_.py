
from multics.globals import *

class set_lock_(SystemSubroutine):
    def __init__(self, system_services):
        super(set_lock_, self).__init__(self.__class__.__name__, system_services)
        
    def lock(self, lock_word, wait_time, code):
        process = get_calling_process_()
        self.system.hardware.acquire_hardware_lock(lock_word, process.id(), wait_time, code)
    
    def unlock(self, lock_word, code):
        process = get_calling_process_()
        self.system.hardware.release_hardware_lock(lock_word, process.id(), code)
