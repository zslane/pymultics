
from PySide.QtGui import QApplication
app = QApplication([])

from multics.hardware.console import ConsoleWindow
console = ConsoleWindow()
console.show()

app.exec_()
