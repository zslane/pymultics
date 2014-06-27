
from multics.globals import *

from PySide import QtGui

class read_password_(SystemExecutable):
    def __init__(self, system_services):
        super(read_password_, self).__init__(self.__class__.__name__, system_services)
        
    def procedure(self, prompt, password):
        tty_channel = get_calling_process_().tty()
        try:
            self.system.llout("%s\n" % (prompt), tty_channel)
            
            self.system.set_input_mode(QtGui.QLineEdit.Password, tty_channel)
            input = self.system.llin(block=True, tty_channel=tty_channel)
            self.system.set_input_mode(QtGui.QLineEdit.Normal, tty_channel)
            
            input = input.strip().replace("\t", " ")
            if input == "": input = "*"
            password.val = input
            
        except:
            self.system.set_input_mode(QtGui.QLineEdit.Normal, tty_channel)
            raise
        # end try
        