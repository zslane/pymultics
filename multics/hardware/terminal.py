from PySide import QtCore, QtGui

class KeyboardIO(QtGui.QLineEdit):

    lineFeed = QtCore.Signal()
    breakSignal = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(KeyboardIO, self).__init__(parent)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Pause:
            self.breakSignal.emit()
            event.accept()
        elif event.key() == QtCore.Qt.Key_Down:
            self.lineFeed.emit()
            event.accept()
        else:
            super(KeyboardIO, self).keyPressEvent(event)
        
class TerminalIO(QtGui.QWidget):
    
    textEntered = QtCore.Signal(str)
    lineFeed = QtCore.Signal()
    breakSignal = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(TerminalIO, self).__init__(parent)
        
        FONT_NAME = "Glass TTY VT220"
        FONT_SIZE = 15

        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("QTextEdit { font-family: '%s'; font-size: %dpt; color: lightgreen; background: black; }" % (FONT_NAME, FONT_SIZE))
        self.output.setFontFamily(FONT_NAME)
        self.output.setFontPointSize(FONT_SIZE)
        self.output.setFocusPolicy(QtCore.Qt.NoFocus)
        self.output.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.output.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.output.setViewportMargins(3, -5, 0, 0)
        self.output.setFixedSize(self._width(80), self._height(25))
        self.output.setEnabled(False)
        
        self.input = KeyboardIO()
        self.input.setStyleSheet("QLineEdit { font-family: '%s'; font-size: %dpt; color: lightgreen; background: black; }" % (FONT_NAME, FONT_SIZE))
        self.input.returnPressed.connect(self._process_input)
        self.input.lineFeed.connect(self._process_line_feed)
        self.input.breakSignal.connect(self._process_break_signal)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.output)
        layout.addWidget(self.input)
        
        self.setLayout(layout)
        
    def _width(self, nchars):
        fm = QtGui.QFontMetrics(self.output.currentFont())
        return 8 + fm.width("M" * nchars) + 8
        
    def _height(self, nlines):
        fm = QtGui.QFontMetrics(self.output.currentFont())
        self.output.verticalScrollBar().setSingleStep(fm.lineSpacing())
        return fm.lineSpacing() * nlines + 4
        
    def _process_input(self):
        txt = self.input.text()
        self.input.clear()
        self.textEntered.emit(txt)
        
    def _process_line_feed(self):
        if not self.input.text():
            self.lineFeed.emit()
        
    def _process_break_signal(self):
        self.input.clear()
        self.breakSignal.emit()
        
    @QtCore.Slot()
    def shutdown(self):
        self.input.setEnabled(False)
        
    @QtCore.Slot(str)
    def display(self, txt):
        self.output.insertPlainText(txt)
        #== Remove characters that will never be seen again. This keeps the text edit
        #== widget from filling up with useless characters.
        max_chars = 80 * 25 + 1
        num_chars = len(self.output.toPlainText())
        if num_chars > max_chars:
            cursor = self.output.textCursor()
            cursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(num_chars - max_chars, QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
        # end if
        self.output.moveCursor(QtGui.QTextCursor.End)
        
    @QtCore.Slot(int)
    def setEchoMode(self, mode):
        self.input.setEchoMode(QtGui.QLineEdit.EchoMode(mode))
        
class TerminalWindow(QtGui.QMainWindow):

    transmitString = QtCore.Signal(str)
    setEchoMode = QtCore.Signal(int)
    heartbeat = QtCore.Signal()
    shutdown = QtCore.Signal()
    closed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(TerminalWindow, self).__init__(parent)
        
        self.io = TerminalIO(self)
        self.transmitString.connect(self.io.display)
        self.setEchoMode.connect(self.io.setEchoMode)
        self.shutdown.connect(self.io.shutdown)
        
        self.setCentralWidget(self.io)
        self.setWindowTitle("Virtual VT220 Terminal")
        self.setStyleSheet("QWidget, QMainWindow { background: #444444; border: 1px solid #252525; }")
        
        HEARTBEAT_PERIOD = 200
        self.timerid = self.startTimer(HEARTBEAT_PERIOD)
        
        self.move(300, 50)
    
    def timerEvent(self, event):
        self.heartbeat.emit()
        
    def closeEvent(self, event):
        self.killTimer(self.timerid)
        self.closed.emit()
        event.accept()
