
from multics.globals import *

include.iox_control

from PySide import QtGui

class read_password_(Subroutine):
    def __init__(self):
        super(read_password_, self).__init__(self.__class__.__name__)
        
    def procedure(self, prompt, password):
        tty_channel = get_calling_process_().tty()
        iox_control.echo_input_sw = False
        iox_control.enable_signals_sw = True
        iox_control.filter_chars = common_ctrl_chars
        buffer = parm()
        try:
            call.iox_.write(tty_channel, "%s\n" % (prompt))
            
            call.iox_.set_input_mode(tty_channel, QtGui.QLineEdit.Password)
            call.iox_.wait_get_line(tty_channel, iox_control, buffer)
            call.iox_.set_input_mode(tty_channel, QtGui.QLineEdit.Normal)
            
            input = buffer.val.strip().replace("\t", " ")
            if input == "": input = "*"
            password.val = input
            
        except:
            call.iox_.set_input_mode(tty_channel, QtGui.QLineEdit.Normal)
            raise
        # end try
        