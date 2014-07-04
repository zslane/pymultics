import re

from PySide import QtCore, QtGui, QtNetwork

N_HORZ_CHARS = 80
N_VERT_LINES = 25

DEFAULT_SERVER_NAME = "localhost"
DEFAULT_SERVER_PORT = 6800
DEFAULT_PHOSPHOR_COLOR = "green"

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
    
    @staticmethod
    def In(byte_array):
        return DataPacket(byte_array)
        
    @staticmethod
    def Out(data_code, payload=""):
        if data_code[0] < chr(32) and data_code[0] != '\r': # control codes are all less than ASCII value 32
            # print "DataPacket.Out(CONTROL_CODE + chr(%d) + %s + END_CONTROL_CODE)" % (ord(data_code[0]), repr(payload))
            return QtCore.QByteArray(CONTROL_CODE + data_code + str(payload) + END_CONTROL_CODE)
        else:
            # print "DataPacket.Out(%s)" % (repr(data_code))
            return QtCore.QByteArray(data_code)

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
    
    setNormalStatus = QtCore.Signal(str)
    setConnectStatus = QtCore.Signal(str)
    setErrorStatus = QtCore.Signal(str)
    
    TEXT_EDIT_STYLE_SHEET = "QTextEdit { font-family: '%s'; font-size: %dpt; color: %s; background: black; border: 0px; }"
    LINE_EDIT_STYLE_SHEET = "QLineEdit { font-family: '%s'; font-size: %dpt; color: %s; background: black; }"
    
    def __init__(self, phosphor_color, parent=None):
        super(TerminalIO, self).__init__(parent)
        self.ME = self.__class__.__name__
        
        if phosphor_color == "green": color = "lightgreen"
        if phosphor_color == "amber": color = "gold"
        if phosphor_color == "white": color = "white"
        
        self.host = DEFAULT_SERVER_NAME
        self.port = DEFAULT_SERVER_PORT
        
        self.socket = QtNetwork.QTcpSocket(self)
        self.socket.error.connect(self.socket_error)
        self.socket.hostFound.connect(self.host_found)
        self.socket.connected.connect(self.connection_made)
        self.socket.disconnected.connect(self.connection_lost)
        self.socket.readyRead.connect(self.data_available)
        self.com_port = 0
        
        self.FONT_NAME = "Glass TTY VT220"
        self.FONT_SIZE = 15
        
        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(self.TEXT_EDIT_STYLE_SHEET % (self.FONT_NAME, self.FONT_SIZE, color))
        self.output.setFontFamily(self.FONT_NAME)
        self.output.setFontPointSize(self.FONT_SIZE)
        self.output.setFocusPolicy(QtCore.Qt.NoFocus)
        self.output.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.output.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
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
        self.input.setStyleSheet(self.LINE_EDIT_STYLE_SHEET % (self.FONT_NAME, self.FONT_SIZE, color))
        self.input.setEnabled(False)
        self.input.returnPressed.connect(self.send_string)
        self.input.lineFeed.connect(self.send_linefeed)
        self.input.breakSignal.connect(self.send_break_signal)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(output_frame)
        layout.addWidget(self.input)
        
        self.setLayout(layout)
        
    def startup(self):
        self.socket.connectToHost(self.host, self.port)
        
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
            self.setErrorStatus.emit("Host Server not Active")
        else:
            self.setErrorStatus.emit(self.socket.errorString())
            print self.ME, "socket_error:", error
        
    @QtCore.Slot()
    def host_found(self):
        self.setNormalStatus.emit("Waiting for Host Server")
        
    @QtCore.Slot()
    def connection_made(self):
        self.socket.setSocketOption(QtNetwork.QAbstractSocket.LowDelayOption, 1)
        self.setConnectStatus.emit("Connected on port %d" % (self.socket.peerPort()))
        if self.socket.peerPort() != self.port:
            self.input.setEnabled(True)
            self.input.setFocus()
        
    @QtCore.Slot()
    def connection_lost(self):
        self.input.setEnabled(False)
        self.setNormalStatus.emit("Disconnected")
        #== Original connection closed; this sets up the "permanent" connection
        if self.com_port:
            self.socket.connectToHost(self.host, self.com_port)
            self.socket.bytesWritten.connect(self.written)
            self.com_port = 0
        else:
            print self.ME, "connection closed by host"
        
    @QtCore.Slot()
    def data_available(self):
        data_packet = DataPacket.In(self.socket.readAll())
        while not data_packet.is_empty():
            if data_packet.is_control_seq():
                data_code, payload = data_packet.extract_control_data()
                
                if data_code == ASSIGN_PORT_CODE:
                    self.com_port = int(payload)
                    # print self.ME, "disconnecting and reconnecting on port", self.com_port
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
        s = self.input.text().strip() or "\r"
        self.input.clear()
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            # print self.ME, "sending:", repr(s)
            n = self.socket.write(DataPacket.Out(s))
            # print self.ME, n, "bytes sent"
            self.socket.flush()
    
    @QtCore.Slot()
    def send_linefeed(self):
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            # print self.ME, "sending LINEFEED"
            n = self.socket.write(DataPacket.Out(LINEFEED_CODE))
            # print self.ME, n, "bytes sent"
            self.socket.flush()
            
    @QtCore.Slot()
    def send_break_signal(self):
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            # print self.ME, "sending BREAK signal"
            n = self.socket.write(DataPacket.Out(BREAK_CODE))
            # print self.ME, n, "bytes sent"    
            self.socket.flush()
    
    def written(self, nbytes):
        # print self.ME, nbytes, "written"
        pass
        
    @QtCore.Slot()
    def shutdown(self):
        self.input.setEnabled(False)
        if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.socket.disconnectFromHost()
        
    @QtCore.Slot()
    def reconnect(self):
        self.socket.connectToHost(self.host, self.port)
        
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
        
    def set_server_name(self, host):
        self.host = host
        
    def set_server_port(self, port):
        self.port = port
        
    def set_phosphor_color(self, phosphor_color):
        if phosphor_color == "green": color = "lightgreen"
        if phosphor_color == "amber": color = "gold"
        if phosphor_color == "white": color = "white"
        
        self.output.setStyleSheet(self.TEXT_EDIT_STYLE_SHEET % (self.FONT_NAME, self.FONT_SIZE, color))
        self.output.style().unpolish(self)
        self.output.style().polish(self)
        self.output.update()
        
        self.input.setStyleSheet(self.LINE_EDIT_STYLE_SHEET % (self.FONT_NAME, self.FONT_SIZE, color))
        self.input.style().unpolish(self)
        self.input.style().polish(self)
        self.input.update()
        
MENUBAR_STYLE_SHEET = """
    QMenuBar                { background: #252525; color: #c8c8c8; }
    QMenuBar::item          { background: transparent; }
    QMenuBar::item:selected { background: #444444; }
"""

MENU_STYLE_SHEET = """
    QMenu                { background: #444444; color: #c8c8c8; }
    QMenu::item:selected { background: #656565; }
"""

class TerminalWindow(QtGui.QMainWindow):

    transmitString = QtCore.Signal(str)
    shutdown = QtCore.Signal()
    closed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(TerminalWindow, self).__init__(parent)
        
        self.settings = QtCore.QSettings("pymultics", "Multics.Terminal")
        
        self.io = TerminalIO(DEFAULT_PHOSPHOR_COLOR, self)
        self.io.setNormalStatus.connect(self.set_normal_status)
        self.io.setConnectStatus.connect(self.set_connect_status)
        self.io.setErrorStatus.connect(self.set_error_status)
        self.transmitString.connect(self.io.display)
        self.shutdown.connect(self.io.shutdown)
        
        self.setCentralWidget(self.io)
        self.setWindowTitle("Virtual VT220 Terminal")
        self.setStyleSheet("QLineEdit, QMainWindow { background: #444444; border: 1px solid #252525; }")
        
        self.palette = QtGui.QPalette()
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x444444))
        
        self.status_label = QtGui.QLabel()
        self.status_label.setAutoFillBackground(True)
        self.status_label.setPalette(self.palette)
        self.status_label.setText("Ready")
        
        status_layout = QtGui.QVBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        status_frame = QtGui.QFrame()
        status_frame.setLayout(status_layout)
        
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().setAutoFillBackground(True)
        self.statusBar().setPalette(self.palette)
        self.statusBar().addPermanentWidget(status_frame, 1)
        
        self.setup_menus()
        
        self.move(300, 50)
        
        QtCore.QTimer.singleShot(0, self.startup)
        
    def setup_menus(self):
        self.menuBar().setStyleSheet(MENUBAR_STYLE_SHEET)
        
        self.options_menu = self.menuBar().addMenu("Options")
        self.options_menu.setStyleSheet(MENU_STYLE_SHEET)
        
        self.set_host_action = self.options_menu.addAction("Set Host...")
        self.set_port_action = self.options_menu.addAction("Set Port...")
        self.options_menu.addSeparator()
        self.phosphor_color_menu = self.options_menu.addMenu("Phosphor Color")
        self.options_menu.addSeparator()
        self.reconnect_action = self.options_menu.addAction("Reconnect")
        
        self.set_phosphor_green = self.phosphor_color_menu.addAction("Green")
        self.set_phosphor_amber = self.phosphor_color_menu.addAction("Amber")
        self.set_phosphor_white = self.phosphor_color_menu.addAction("White")
        
        self.phosphor_color_group = QtGui.QActionGroup(self)
        self.phosphor_color_group.addAction(self.set_phosphor_green)
        self.phosphor_color_group.addAction(self.set_phosphor_amber)
        self.phosphor_color_group.addAction(self.set_phosphor_white)
        
        self.set_phosphor_green.setCheckable(True)
        self.set_phosphor_amber.setCheckable(True)
        self.set_phosphor_white.setCheckable(True)
        
        self.set_phosphor_green.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "green")
        self.set_phosphor_amber.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "amber")
        self.set_phosphor_white.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "white")
        self.reconnect_action.setEnabled(False)
        
        self.set_host_action.triggered.connect(self.set_host_dialog)
        self.set_port_action.triggered.connect(self.set_port_dialog)
        
        self.set_phosphor_green.triggered.connect(lambda: self.set_phosphor_color("green"))
        self.set_phosphor_amber.triggered.connect(lambda: self.set_phosphor_color("amber"))
        self.set_phosphor_white.triggered.connect(lambda: self.set_phosphor_color("white"))
        
        self.reconnect_action.triggered.connect(self.io.reconnect)
        self.io.socket.connected.connect(lambda: self.reconnect_action.setEnabled(False))
        self.io.socket.disconnected.connect(lambda: self.reconnect_action.setEnabled(True))
        self.io.socket.error.connect(lambda: self.reconnect_action.setEnabled(True))
    
    def startup(self):
        self.setFixedSize(self.size())
        self.io.set_server_name(self.settings.value("host", DEFAULT_SERVER_NAME))
        self.io.set_server_port(self.settings.value("port", DEFAULT_SERVER_PORT))
        self.io.set_phosphor_color(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR))
        self.io.startup()
        
    def set_phosphor_color(self, color):
        self.io.set_phosphor_color(color)
        self.settings.setValue("phosphor_color", color)
    
    def set_status(self, txt):
        self.statusBar().setPalette(self.palette)
        self.status_label.setPalette(self.palette)
        self.status_label.setText(txt)
    
    @QtCore.Slot(str)
    def set_normal_status(self, txt):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x444444))
        self.set_status(txt)
        
    @QtCore.Slot(str)
    def set_connect_status(self, txt):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x445e44))
        self.set_status(txt)
        
    @QtCore.Slot(str)
    def set_error_status(self, txt):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x935353))
        self.set_status(txt)
    
    @QtCore.Slot()
    def disconnect(self):
        QtCore.QTimer.singleShot(0, self.close)
        
    @QtCore.Slot()
    def set_host_dialog(self):
        host, ok = QtGui.QInputDialog.getText(None, "Set Host", "Enter host address:", text=self.settings.value("host", DEFAULT_SERVER_NAME))
        if ok:
            self.io.set_server_name(host)
            self.settings.setValue("host", host)
        
    @QtCore.Slot()
    def set_port_dialog(self):
        port, ok = QtGui.QInputDialog.getInt(None, "Set Port", "Enter port number:", value=self.settings.value("port", DEFAULT_SERVER_PORT))
        if ok:
            self.io.set_server_port(port)
            self.settings.setValue("port", port)
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = TerminalWindow()
    win.show()
    app.exec_()
    