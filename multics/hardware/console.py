from PySide import QtCore, QtGui

N_HORZ_CHARS = 80
N_VERT_LINES = 25

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
        
class ConsoleIO(QtGui.QWidget):
    
    textEntered = QtCore.Signal(str)
    lineFeed = QtCore.Signal()
    breakSignal = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(ConsoleIO, self).__init__(parent)
        
        FONT_NAME = "Consolas" #"Glass TTY VT220"
        FONT_SIZE = 8 #15
        
        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("QTextEdit { font-family: '%s'; font-size: %dpt; color: gold; background: black; border: 0px; }" % (FONT_NAME, FONT_SIZE))
        self.output.setFontFamily(FONT_NAME)
        self.output.setFontPointSize(FONT_SIZE)
        self.output.setFocusPolicy(QtCore.Qt.NoFocus)
        self.output.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.output.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.output.setViewportMargins(3, 0, 0, 0)
        self.output.setFixedSize(self._width(N_HORZ_CHARS), self._height(N_VERT_LINES))
        self.output.setEnabled(False)
        
        output_layout = QtGui.QVBoxLayout()
        output_layout.addWidget(self.output)
        output_layout.setContentsMargins(3, 3, 0, 3)
        
        output_frame = QtGui.QFrame()
        output_frame.setFrameStyle(QtGui.QFrame.NoFrame)
        output_frame.setStyleSheet("QFrame { background: black; }")
        output_frame.setLayout(output_layout)
        
        self.input = KeyboardIO()
        self.input.setStyleSheet("QLineEdit { font-family: '%s'; font-size: %dpt; color: gold; background: black; }" % (FONT_NAME, FONT_SIZE))
        self.input.returnPressed.connect(self._process_input)
        self.input.lineFeed.connect(self._process_line_feed)
        self.input.breakSignal.connect(self._process_break_signal)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(output_frame)
        layout.addWidget(self.input)
        
        self.setLayout(layout)
        
    def _width(self, nchars):
        fm = QtGui.QFontMetrics(self.output.currentFont())
        return fm.width("M" * nchars)
        
    def _height(self, nlines):
        fm = QtGui.QFontMetrics(self.output.currentFont())
        self.output.verticalScrollBar().setSingleStep(fm.lineSpacing())
        return fm.lineSpacing() * nlines
        
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
        max_chars = N_HORZ_CHARS * N_VERT_LINES + 1
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
        
class ConsoleWindow(QtGui.QMainWindow):

    transmitString = QtCore.Signal(str)
    setEchoMode = QtCore.Signal(int)
    heartbeat = QtCore.Signal()
    shutdown = QtCore.Signal()
    closed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(ConsoleWindow, self).__init__(parent)
        
        self.io = ConsoleIO(self)
        self.transmitString.connect(self.io.display)
        self.setEchoMode.connect(self.io.setEchoMode)
        self.shutdown.connect(self.io.shutdown)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.io)
        
        central_widget = QtGui.QWidget()
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget) #(self.io)
        self.setWindowTitle("System Console")
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

    # @QtCore.Slot()
    # def disconnect(self):
        # QtCore.QTimer.singleShot(0, self.close)
        