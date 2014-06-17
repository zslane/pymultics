
from multics.globals import *

from PySide import QtGui

class read_password_(SystemExecutable):
    def __init__(self, system_services):
        super(read_password_, self).__init__(self.__class__.__name__, system_services)
        
    def procedure(self, prompt, password):
        try:
            self.system.llout("%s\n" % (prompt))
            
            self.system.set_input_mode(QtGui.QLineEdit.Password)
            input = self.system.llin(block=True)
            self.system.set_input_mode(QtGui.QLineEdit.Normal)
            
            input = input.strip().replace("\t", " ")
            if input == "": input = "*"
            password.val = input
            
        except:
            self.system.set_input_mode(QtGui.QLineEdit.Normal)
            raise
        # end try
        