
from multics.globals import *

class com_err_(Executable):

    def __init__(self):
        super(com_err_, self).__init__(self.__class__.__name__)
        
    def procedure(self, code, name):
        call.ioa_("{0}: {1}", name, code)
        
#-- end class com_err_
