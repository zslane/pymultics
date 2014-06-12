import sys

from PySide.QtGui import QApplication
app = QApplication([])

from multics import *

terminal = TerminalWindow()
terminal.show()

hardware = VirtualMulticsHardware(sys.argv)
hardware.attach_terminal(terminal)

multics = hardware.boot_OS()
multics.start()

app.exec_()
