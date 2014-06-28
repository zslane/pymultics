import re

from PySide import QtCore, QtGui, QtNetwork

N_HORZ_CHARS = 80
N_VERT_LINES = 25
            
SERVER_NAME = "localhost"
SERVER_PORT = 6800

CONTROL_CODE       = chr(17) # Device Control 1
UNKNOWN_CODE       = chr(0)
ECHO_NORMAL_CODE   = chr(1)
ECHO_PASSWORD_CODE = chr(2)
ASSIGN_PORT_CODE   = chr(26) # Substitute
END_CONTROL_CODE   = chr(4)  # End of Transmission

LINEFEED_CODE      = chr(10) # Linefeed
BREAK_CODE         = chr(24) # Cancel

class DataPacket(object):

    def __init__(self, byte_array):
        self.data = byte_array.data()
        
    def is_empty(self):
        return len(self.data) == 0
        
    def is_control_seq(self):
        return self.data != "" and re.match(CONTROL_CODE + ".+" + END_CONTROL_CODE, self.data, re.DOTALL) != None
        
    def extract_control_data(self):
        if self.is_control_seq():
            m = re.match(CONTROL_CODE + "(.)(.*)" + END_CONTROL_CODE + "(.*)", self.data, re.DOTALL)
            data_code = m.group(1)
            payload   = m.group(2)
            self.data = m.group(3)
            return (data_code, payload)
        # end if
        return (None, None)
        
    def extract_plain_data(self):
        data, control_code, the_rest = self.data.partition(CONTROL_CODE)
        self.data = control_code + the_rest
        return data

#-- end class DataPacket

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
    
    setStatus = QtCore.Signal(list)
    
    def __init__(self, parent=None):
        super(TerminalIO, self).__init__(parent)
        self.ME = self.__class__.__name__
        
        self.socket = QtNetwork.QTcpSocket(self)
        self.socket.error.connect(self.socket_error)
        self.socket.hostFound.connect(self.host_found)
        self.socket.connected.connect(self.connection_made)
        self.socket.disconnected.connect(self.connection_lost)
        self.socket.readyRead.connect(self.data_available)
        self.com_port = 0
        
        FONT_NAME = "Glass TTY VT220"
        FONT_SIZE = 15

        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("QTextEdit { font-family: '%s'; font-size: %dpt; color: lightgreen; background: black; border: 0px; }" % (FONT_NAME, FONT_SIZE))
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
        self.input.setStyleSheet("QLineEdit { font-family: '%s'; font-size: %dpt; color: lightgreen; background: black; }" % (FONT_NAME, FONT_SIZE))
        self.input.setEnabled(False)
        self.input.returnPressed.connect(self.send_string)
        self.input.lineFeed.connect(self.send_linefeed)
        self.input.breakSignal.connect(self.send_break_signal)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(output_frame)
        layout.addWidget(self.input)
        
        self.setLayout(layout)
        
        QtCore.QTimer.singleShot(0, self.startup)
        
    def startup(self):
        self.socket.connectToHost(SERVER_NAME, SERVER_PORT)
        
    def _width(self, nchars):
        fm = QtGui.QFontMetrics(self.output.currentFont())
        return fm.width("M" * nchars)
        
    def _height(self, nlines):
        fm = QtGui.QFontMetrics(self.output.currentFont())
        self.output.verticalScrollBar().setSingleStep(fm.lineSpacing())
        return fm.lineSpacing() * nlines
        
    @QtCore.Slot("QAbstractSocket.SocketError")
    def socket_error(self, error):
        if error == QtNetwork.QAbstractSocket.SocketError.ConnectionRefusedError:
            self.setStatus.emit(["Host Server not Active", 0x935353])
            pass

        else:
            self.setStatus.emit([self.socket.errorString(), 0x935353])
            print self.ME, "socket_error:", error
        
    @QtCore.Slot()
    def host_found(self):
        self.setStatus.emit(["Waiting for Host Server", None])
        pass
        
    @QtCore.Slot()
    def connection_made(self):
        self.socket.setSocketOption(QtNetwork.QAbstractSocket.LowDelayOption, 1)
        self.setStatus.emit(["Connected on port %d" % (self.socket.peerPort()), 0x445e44])
        if self.socket.peerPort() != SERVER_PORT:
            self.input.setEnabled(True)
            self.input.setFocus()
        
    @QtCore.Slot()
    def connection_lost(self):
        self.setStatus.emit(["Not Connected", None])
        #== Original connection closed; this sets up the "permanent" connection
        if self.com_port:
            self.socket.connectToHost(SERVER_NAME, self.com_port)
            self.socket.bytesWritten.connect(self.written)
            self.com_port = 0
        
    @QtCore.Slot()
    def data_available(self):
        data_packet = DataPacket(self.socket.readAll())
        while not data_packet.is_empty():
            if data_packet.is_control_seq():
                data_code, payload = data_packet.extract_control_data()
                
                if data_code == ASSIGN_PORT_CODE:
                    self.com_port = int(payload)
                    print self.ME, "disconnecting and reconnecting on port", self.com_port
                    self.socket.close()
                    
                elif data_code == ECHO_NORMAL_CODE:
                    self.input.setEchoMode(QtGui.QLineEdit.Normal)
                    
                elif data_code == ECHO_PASSWORD_CODE:
                    self.input.setEchoMode(QtGui.QLineEdit.Password)
                    
                else:
                    raise ValueError("unknown control data code %d" % (ord(data_code)))
                # end if
            else:
                self.display(data_packet.extract_plain_data())
        
    @QtCore.Slot()
    def send_string(self):
        s = self.input.text().strip() or "\n"
        self.input.clear()
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            print self.ME, "sending:", repr(s)
            n = self.socket.write(QtCore.QByteArray(s))
            print self.ME, n, "bytes sent"
    
    @QtCore.Slot()
    def send_linefeed(self):
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            print self.ME, "sending LINEFEED"
            n = self.socket.write(QtCore.QByteArray(CONTROL_CODE + LINEFEED_CODE + END_CONTROL_CODE))
            print self.ME, n, "bytes sent"
            
    @QtCore.Slot()
    def send_break_signal(self):
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            print self.ME, "sending BREAK signal"
            n = self.socket.write(QtCore.QByteArray(CONTROL_CODE + BREAK_CODE + END_CONTROL_CODE))
            print self.ME, n, "bytes sent"    
    
    def written(self, nbytes):
        print self.ME, nbytes, "written"
        
    @QtCore.Slot()
    def shutdown(self):
        self.input.setEnabled(False)
        if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.socket.disconnectFromHost()
        
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
        
class TerminalWindow(QtGui.QMainWindow):

    transmitString = QtCore.Signal(str)
    shutdown = QtCore.Signal()
    closed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(TerminalWindow, self).__init__(parent)
        
        self.io = TerminalIO(self)
        self.io.setStatus.connect(self.set_status)
        self.transmitString.connect(self.io.display)
        self.shutdown.connect(self.io.shutdown)
        
        self.setCentralWidget(self.io)
        self.setWindowTitle("Virtual VT220 Terminal")
        self.setStyleSheet("QLineEdit, QMainWindow { background: #444444; border: 1px solid #252525; }")
        # self.setFixedSize(821, 596)
        
        self.palette = QtGui.QPalette()
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x444444))
        
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().setAutoFillBackground(True)
        self.statusBar().setPalette(self.palette)
        self.statusBar().showMessage("Ready")
        
        self.move(300, 50)
        
        QtCore.QTimer.singleShot(0, self.startup)
        
    def startup(self):
        self.setFixedSize(self.size())
        
    @QtCore.Slot(str)
    def set_status(self, data):
        txt, color = data
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(color or 0x444444))
        self.statusBar().setPalette(self.palette)
        self.statusBar().showMessage(txt)
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
    @QtCore.Slot()
    def disconnect(self):
        QtCore.QTimer.singleShot(0, self.close)
        
if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = TerminalWindow()
    win.show()
    app.exec_()
    