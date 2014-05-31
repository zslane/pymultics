from PySide.QtGui import QApplication
app = QApplication([])

from multics import *

terminal = TerminalWindow()
terminal.show()

hardware = VirtualMulticsHardware()
hardware.attach_terminal(terminal)

multics = hardware.boot_OS()
multics.start()

app.exec_()
