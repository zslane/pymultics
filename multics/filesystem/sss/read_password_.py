
from multics.globals import *

from PySide import QtGui

class read_password_(Subroutine):
    def __init__(self):
        super(read_password_, self).__init__(self.__class__.__name__)
        
    def procedure(self, prompt, password):
        tty_channel = get_calling_process_().tty()
        try:
            GlobalEnvironment.supervisor.llout("%s\n" % (prompt), tty_channel)
            
            GlobalEnvironment.supervisor.set_input_mode(QtGui.QLineEdit.Password, tty_channel)
            input = GlobalEnvironment.supervisor.llin(block=True, tty_channel=tty_channel)
            GlobalEnvironment.supervisor.set_input_mode(QtGui.QLineEdit.Normal, tty_channel)
            
            input = input.strip().replace("\t", " ")
            if input == "": input = "*"
            password.val = input
            
        except:
            GlobalEnvironment.supervisor.set_input_mode(QtGui.QLineEdit.Normal, tty_channel)
            raise
        # end try
        