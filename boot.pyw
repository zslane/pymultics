import sys        
sys.stdout = open("nul", "w")

from PySide.QtGui import QApplication
app = QApplication([])

from multics.hardware.console import ConsoleWindow
console = ConsoleWindow()
console.show()

app.exec_()
