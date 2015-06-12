import os

from mainframe import VirtualMulticsHardware

from PySide import QtCore, QtGui

N_HORZ_CHARS = 80
N_VERT_LINES = 25

BEL = chr(7)
BS  = chr(8)
TAB = chr(9)
LF  = chr(10)
CR  = chr(13)
ESC = chr(27)

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
        
class ScreenIO(QtGui.QTextEdit):

    def __init__(self, font, parent=None):
        super(ScreenIO, self).__init__(parent)
        
        self.bkgd = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "multics_watermark.png"))
        
        fm = QtGui.QFontMetrics(font)
        
        self.setReadOnly(True)
        self.setStyleSheet("QTextEdit { color: gold; background: black; border: 0px; }")
        self.setFont(font)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setCursorWidth(fm.width("M"))
        self.setEnabled(False)
        self.setConnected(True)
        
    def setConnected(self, flag):
        self.connected = flag
        
    def paintEvent(self, event):
        #== Paint Multics logo as a faint background watermark
        painter = QtGui.QPainter()
        painter.begin(self.viewport())
        painter.setOpacity(0.08)
        painter.drawPixmap(self.viewport().rect(), self.bkgd, self.bkgd.rect())
        painter.end()
        #== Call default event handler to draw the text on top of the watermark
        super(ScreenIO, self).paintEvent(event)
        #== Draw a block cursor if we're connected (i.e., the mainframe is up and running)
        if self.connected:
            painter = QtGui.QPainter(self.viewport())
            painter.fillRect(self.cursorRect(), QtGui.QBrush(self.palette().text().color()))
        
class ConsoleIO(QtGui.QWidget):
    
    textEntered = QtCore.Signal(str)
    breakSignal = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(ConsoleIO, self).__init__(parent)
        
        font = QtGui.QFont(*parent.config['font'])
        
        self.output = ScreenIO(font)
        self.output.setFixedSize(self._width(N_HORZ_CHARS), self._height(N_VERT_LINES))
        
        output_layout = QtGui.QVBoxLayout()
        output_layout.addWidget(self.output)
        output_layout.setContentsMargins(0, 3, 0, 3)
        
        output_frame = QtGui.QFrame()
        output_frame.setFrameStyle(QtGui.QFrame.NoFrame)
        output_frame.setStyleSheet("QFrame { background: black; }")
        output_frame.setLayout(output_layout)
        
        self.input = KeyboardIO()
        self.input.setStyleSheet("QLineEdit { color: gold; background: black; }" )
        self.input.setFont(font)
        self.input.returnPressed.connect(self.send_string)
        self.input.lineFeed.connect(self.send_linefeed)
        self.input.breakSignal.connect(self.send_break_signal)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(output_frame)
        layout.addWidget(self.input)
        
        self.setLayout(layout)
        
    def _width(self, nchars):
        fm = QtGui.QFontMetricsF(self.output.currentFont())
        return int(round(fm.width("M") * nchars + 0.5) + self.output.document().documentMargin() * 2)
        
    def _height(self, nlines):
        fm = QtGui.QFontMetrics(self.output.currentFont())
        self.output.verticalScrollBar().setSingleStep(fm.lineSpacing())
        return fm.lineSpacing() * nlines
        
    def send_string(self):
        txt = self.input.text() + CR
        self.input.clear()
        self.textEntered.emit(txt)
        
    def send_linefeed(self):
        #== If there are other characters in the input buffer, treat the LF as a CR
        #== and send the whole string out.
        if self.input.text():
            self.send_string()
        else:
            self.textEntered.emit(LF)
        
    def send_break_signal(self):
        self.input.clear()
        self.breakSignal.emit()
        
    @QtCore.Slot()
    def shutdown(self):
        self.input.setEnabled(False)
        self.output.setConnected(False)
        
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
        
#-- end class ConsoleIO

class MainframePanel(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MainframePanel, self).__init__(parent)
        
        pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "pymultics_panel.jpg"))
        
        self.image_label = QtGui.QLabel()
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.image_label.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.image_label.setStyleSheet("QLabel { background: #c4c4b4; }")
        
        self.restart_button = QtGui.QPushButton("Restart", self.image_label)
        self.restart_button.setStyleSheet("QPushButton { font: bold 7pt ; }")
        self.restart_button.setFixedSize(93, 15)
        self.restart_button.move(85, 181)
        self.restart_button.setEnabled(False)
        
        main_layout = QtGui.QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.image_label)
        
        self.setLayout(main_layout)
        
#-- end class MainframePanel

class ConsoleWindow(QtGui.QMainWindow):

    transmitString = QtCore.Signal(str)
    setEchoMode = QtCore.Signal(int)
    heartbeat = QtCore.Signal()
    shutdown = QtCore.Signal()
    closed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(ConsoleWindow, self).__init__(parent)
        
        self.config = self.read_console_config()
        
        self.mainframe_panel = MainframePanel()
        self.mainframe_panel.restart_button.clicked.connect(self.restart_system)
        
        self.io = ConsoleIO(self)
        self.transmitString.connect(self.io.display)
        self.setEchoMode.connect(self.io.setEchoMode)
        self.shutdown.connect(self.on_shutdown)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.mainframe_panel)
        layout.addWidget(self.io)
        
        central_widget = QtGui.QWidget()
        central_widget.setLayout(layout)
        
        # from sysadmin import SysAdminWindow
        # sysadmin_widget = SysAdminWindow(self)
        
        # splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        # splitter.addWidget(central_widget)
        # splitter.addWidget(sysadmin_widget)
        
        self.setCentralWidget(central_widget)
        # self.setCentralWidget(splitter)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "multics_logo.png")))
        self.setStyleSheet("QWidget, QMainWindow { background: #c4c4b4; border: 1px solid #252525; }")
        
        HEARTBEAT_PERIOD = 200
        self.timerid = self.startTimer(HEARTBEAT_PERIOD)
        
        self.move(300, 10)
        
        self.io.input.setFocus()
        
        QtCore.QTimer.singleShot(0, self.boot)
        
    def boot(self):
        self.setFixedSize(self.size())
        
        import sys
        self.__hardware = VirtualMulticsHardware(sys.argv)
        self.__hardware.attach_console(self)

        self.__multics = self.__hardware.boot_OS()
        self.__multics.start()
        
    def restart_system(self):
        if not self.io.input.isEnabled():
            self.mainframe_panel.restart_button.setEnabled(False)
            self.io.output.setConnected(True)
            self.io.input.setEnabled(True)
            self.io.input.setFocus()
            
            self.__hardware = VirtualMulticsHardware()
            self.__hardware.attach_console(self)

            self.__multics = self.__hardware.boot_OS()
            self.__multics.start()
    
    def read_console_config(self):
        with open(os.path.join(os.path.dirname(__file__), "console.config"), "r") as f:
            config_text = f.read()
        return eval(config_text)
    
    def timerEvent(self, event):
        self.heartbeat.emit()
        
    def closeEvent(self, event):
        self.killTimer(self.timerid)
        self.closed.emit()
        event.accept()

    @QtCore.Slot()
    def on_shutdown(self):
        self.io.shutdown()
        self.mainframe_panel.restart_button.setEnabled(True)
        
