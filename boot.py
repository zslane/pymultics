import sys

from PySide.QtGui import QApplication
app = QApplication([])

from multics import *

console = ConsoleWindow()
console.show()

hardware = VirtualMulticsHardware(sys.argv)
hardware.attach_console(console)

multics = hardware.boot_OS()
multics.start()

app.exec_()
