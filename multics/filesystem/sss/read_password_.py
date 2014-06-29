
from multics.globals import *

from PySide import QtGui

class read_password_(SystemSubroutine):
    def __init__(self, supervisor):
        super(read_password_, self).__init__(self.__class__.__name__, supervisor)
        
    def procedure(self, prompt, password):
        tty_channel = get_calling_process_().tty()
        try:
            self.supervisor.llout("%s\n" % (prompt), tty_channel)
            
            self.supervisor.set_input_mode(QtGui.QLineEdit.Password, tty_channel)
            input = self.supervisor.llin(block=True, tty_channel=tty_channel)
            self.supervisor.set_input_mode(QtGui.QLineEdit.Normal, tty_channel)
            
            input = input.strip().replace("\t", " ")
            if input == "": input = "*"
            password.val = input
            
        except:
            self.supervisor.set_input_mode(QtGui.QLineEdit.Normal, tty_channel)
            raise
        # end try
        