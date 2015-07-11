import os
import re
import sys

from PySide import QtCore, QtGui, QtNetwork

from ..vt100 import QTelnetSocket

N_HORZ_CHARS = 132
N_VERT_LINES = 60

DEFAULT_SERVER_NAME = "localhost"
DEFAULT_SERVER_PORT = 6800
DEFAULT_PHOSPHOR_COLOR = "vintage"
DEFAULT_BUFFER_SIZE = 300

UNKNOWN_CODE       = chr(0)
CONTROL_CODE       = chr(129)
ECHO_NORMAL_CODE   = chr(130)
ECHO_PASSWORD_CODE = chr(131)
ASSIGN_PORT_CODE   = chr(132)
WHO_CODE           = chr(133)
BREAK_CODE         = chr(134)
END_CONTROL_CODE   = chr(254)

BEL = chr(7)
BS  = chr(8)
TAB = chr(9)
LF  = chr(10)
CR  = chr(13)
ESC = chr(27)

TEXTIO_STYLE_SHEET = "QTextEdit, QLineEdit { color: %s; background: %s; border: 0px; }"

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
        if ord(data_code[0]) >= ord(CONTROL_CODE): # control codes are all greater than ASCII value 127
            # print "DataPacket.Out(CONTROL_CODE + chr(%d) + %s + END_CONTROL_CODE)" % (ord(data_code[0]), repr(payload))
            return QtCore.QByteArray(CONTROL_CODE + data_code + str(payload) + END_CONTROL_CODE)
        else:
            # print "DataPacket.Out(%s)" % (repr(data_code))
            return QtCore.QByteArray(data_code)

#-- end class DataPacket

class KeyboardIO(QtGui.QLineEdit):

    lineFeed = QtCore.Signal()
    breakSignal = QtCore.Signal()
    
    def __init__(self, font, color="white", bkgdcolor="black", parent=None):
        super(KeyboardIO, self).__init__(parent)
        self.setStyleSheet(TEXTIO_STYLE_SHEET % (color, bkgdcolor))
        self.setFont(font)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Pause:
            self.breakSignal.emit()
            event.accept()
        elif event.key() == QtCore.Qt.Key_Enter:
            self.lineFeed.emit()
            event.accept()
        else:
            super(KeyboardIO, self).keyPressEvent(event)
        
class ScreenIO(QtGui.QTextEdit):

    def __init__(self, font, color="white", bkgdcolor="black", parent=None):
        super(ScreenIO, self).__init__(parent)
        
        fm = QtGui.QFontMetrics(font)
        
        self.setStyleSheet(TEXTIO_STYLE_SHEET % (color, bkgdcolor))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.document().setMaximumBlockCount(1024)
        self.document().setDocumentMargin(0)
        self.setCursorWidth(fm.width("M"))
        self.setFont(font)
        self.setReadOnly(True)
        # self.setEnabled(False)
        self.setConnected(False)
        
    def setConnected(self, flag):
        self.connected = flag
        self.update()
        
    def mousePressEvent(self, event):
        event.ignore()
        
    def paintEvent(self, event):
        super(ScreenIO, self).paintEvent(event)
        if self.connected:
            painter = QtGui.QPainter(self.viewport())
            painter.fillRect(self.cursorRect(), QtGui.QBrush(self.palette().text().color()))
        
class TerminalIO(QtGui.QWidget):
    
    setNormalStatus = QtCore.Signal(str)
    setConnectStatus = QtCore.Signal(str)
    setErrorStatus = QtCore.Signal(str)
    
    def __init__(self, phosphor_color, parent=None):
        super(TerminalIO, self).__init__(parent)
        self.ME = self.__class__.__name__
        
        color, bkgdcolor = self.get_text_colors(phosphor_color)
        
        self.name = QtNetwork.QHostInfo.localHostName()
        self.host = DEFAULT_SERVER_NAME
        self.port = DEFAULT_SERVER_PORT
        
        # self.socket = QtNetwork.QTcpSocket(self)
        self.socket = QTelnetSocket.QTelnetSocket(self)
        parent.closed.connect(self.socket._thread.stop)
        self.socket.error.connect(self.socket_error)
        self.socket.hostFound.connect(self.host_found)
        self.socket.connected.connect(self.connection_made)
        self.socket.disconnected.connect(self.connection_lost)
        self.socket.readyRead.connect(self.data_available)
        self.com_port = 0
        
        if N_HORZ_CHARS <= 80 and N_VERT_LINES <= 25:
            FONT_NAME = "Glass TTY VT220"
            FONT_SIZE = 20 if sys.platform == "darwin" else 15
        else:
            FONT_NAME = "Consolas"
            FONT_SIZE = 10 if sys.platform == "win32" else 15
        # end if
        font = QtGui.QFont(FONT_NAME, FONT_SIZE)
        font.setStyleHint(QtGui.QFont.TypeWriter)
        
        self.output = ScreenIO(font, color, bkgdcolor)
        self.output.setFixedSize(self._width(N_HORZ_CHARS), self._height(N_VERT_LINES))
        
        output_layout = QtGui.QVBoxLayout()
        output_layout.addWidget(self.output)
        
        output_frame = QtGui.QFrame()
        output_frame.setFrameStyle(QtGui.QFrame.NoFrame)
        output_frame.setStyleSheet("QFrame { background: %s; }" % (bkgdcolor))
        output_frame.setLayout(output_layout)
        
        self.input = KeyboardIO(font, color, bkgdcolor)
        self.input.setEnabled(False)
        self.input.returnPressed.connect(self.send_string)
        self.input.lineFeed.connect(self.send_linefeed)
        self.input.breakSignal.connect(self.send_break_signal)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(output_frame)
        layout.addWidget(self.input)
        
        self.setLayout(layout)
        
    def startup(self):
        # self.host = "batmud.bat.org"
        # self.port = 23
        self.host = "104.174.119.211"
        self.port = 6180
        global BREAK_CODE
        BREAK_CODE = chr(3) # Ctrl-C
        self.socket.connectToHost(self.host, self.port)
        
    def _width(self, nchars):
        fm = QtGui.QFontMetricsF(self.output.currentFont())
        return int(round(fm.width("M") * nchars + 0.5) + self.output.document().documentMargin() * 2) + 20
        
    def _height(self, nlines):
        fm = QtGui.QFontMetrics(self.output.currentFont())
        self.output.verticalScrollBar().setSingleStep(fm.lineSpacing())
        return fm.lineSpacing() * nlines
        
    def get_text_colors(self, phosphor_color):
        if phosphor_color == "vintage": color = QtGui.QColor(57, 255, 174)
        elif phosphor_color == "green": color = QtGui.QColor(63, 255, 127)
        elif phosphor_color == "amber": color = QtGui.QColor(255, 215, 0)
        elif phosphor_color == "white": color = QtGui.QColor(200, 240, 255)
        
        bkgdcolor = QtGui.QColor(color).darker(1500)
        
        return (color.name(), bkgdcolor.name())
    
    @QtCore.Slot(int)
    def socket_error(self, error):
        if error == QtNetwork.QAbstractSocket.SocketError.ConnectionRefusedError:
            self.setErrorStatus.emit("Host Server %s not Active" % (self.host))
        elif error != QtNetwork.QAbstractSocket.SocketError.RemoteHostClosedError:
            self.setErrorStatus.emit(self.socket.errorString())
            print self.ME, "socket_error:", error
        
    @QtCore.Slot()
    def host_found(self):
        self.setNormalStatus.emit("Waiting for Host Server %s" % (self.host))
        
    @QtCore.Slot()
    def connection_made(self):
        self.socket.setSocketOption(QtNetwork.QAbstractSocket.LowDelayOption, 1)
        connected_msg = "Connected to %s on port %d" % (self.socket.peerName(), self.socket.peerPort())
        if self.socket.peerPort() != self.port:
            self.send_who_code()
            self.output.setConnected(True)
            self.input.setEnabled(True)
            self.input.setFocus()
            self.setConnectStatus.emit(connected_msg)
        else:
            self.setNormalStatus.emit(connected_msg)
        
    @QtCore.Slot()
    def connection_lost(self):
        self.input.setEnabled(False)
        self.output.setConnected(False)
        self.setNormalStatus.emit("Disconnected")
        #== Original connection closed; this sets up the "permanent" connection
        if self.com_port:
            self.socket.connectToHost(self.host, self.com_port)
            self.socket.bytesWritten.connect(self.written)
            self.com_port = 0
        else:
            print self.ME, "connection closed by host", self.host
        
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
        s = self.input.text().strip() + CR + LF
        self.input.clear()
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            # print self.ME, "sending:", repr(s)
            n = self.socket.write(DataPacket.Out(s))
            # print self.ME, n, "bytes sent"
            self.socket.flush()
    
    @QtCore.Slot()
    def send_linefeed(self):
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            #== If there are other characters in the input buffer, treat the LF as a CR
            #== and send the whole string out.
            if self.input.text():
                self.send_string()
            else:
                # print self.ME, "sending LINEFEED"
                n = self.socket.write(DataPacket.Out(LF))
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
        self.output.setConnected(False)
        if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.socket.disconnectFromHost()
        
    @QtCore.Slot()
    def reconnect(self):
        self.socket.connectToHost(self.host, self.port)
        
    @QtCore.Slot(str)
    def display(self, txt):
        self.output.insertPlainText(txt)
        # self.output.moveCursor(QtGui.QTextCursor.End)
        self.output.ensureCursorVisible()
        
    def send_who_code(self):
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            # print self.ME, "sending WHO code"
            n = self.socket.write(DataPacket.Out(WHO_CODE, self.name))
            # print self.ME, n, "bytes sent"    
            self.socket.flush()
    
    def reset(self):
        self.socket.abort()
        QtCore.QTimer.singleShot(0, self.reconnect)
        
    def set_server_name(self, host):
        self.host = host
        
    def set_server_port(self, port):
        self.port = port
        
    def set_phosphor_color(self, phosphor_color):
        color, bkgdcolor = self.get_text_colors(phosphor_color)
        
        self.output.setStyleSheet(TEXTIO_STYLE_SHEET % (color, bkgdcolor))
        self.output.style().unpolish(self)
        self.output.style().polish(self)
        self.output.update()
        
        self.input.setStyleSheet(TEXTIO_STYLE_SHEET % (color, bkgdcolor))
        self.input.style().unpolish(self)
        self.input.style().polish(self)
        self.input.update()
        
    def set_buffer_size(self, n_lines):
        self.output.document().setMaximumBlockCount(n_lines)
        
    def get_buffer_contents(self):
        return self.output.toPlainText().encode("Latin-1")
        
    def send_frame(self, s):
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            # print self.ME, "sending:", repr(s)
            n = self.socket.write(DataPacket.Out(s))
            # print self.ME, n, "bytes sent"
            self.socket.flush()
            
    def send_file(self, path):
        STX = chr(2)
        EOT = chr(4)
        f = open(path)
        lines = f.read().split("\n")
        f.close()
        num_lines = len(lines)
        max_chars = max(map(len, lines))
        self.send_frame(STX)
        
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
        self.io.socket.connected.connect(self.disable_reconnect)
        self.io.socket.disconnected.connect(self.enable_reconnect)
        self.io.socket.error.connect(self.enable_reconnect)
        self.transmitString.connect(self.io.display)
        self.shutdown.connect(self.io.shutdown)
        
        self.setCentralWidget(self.io)
        self.setWindowTitle("pyMultics Virtual Terminal - {0}".format(self.io.name))
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "terminal.png")))
        self.setStyleSheet("QLineEdit, QMainWindow { background: #444444; border: 1px solid #252525; }")
        
        self.palette = QtGui.QPalette()
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x444444))
        self.palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
        
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
        self.statusBar().setStyleSheet("QStatusBar::item { border: 0px; }")
        self.statusBar().addPermanentWidget(status_frame, 1)
        
        self.setup_menus()
        
        self.move(300, 50)
        
        QtCore.QTimer.singleShot(0, self.startup)
        
    def setup_menus(self):
        self.menuBar().setStyleSheet(MENUBAR_STYLE_SHEET)
        self.menuBar().setNativeMenuBar(False)
        
        self.options_menu = self.menuBar().addMenu("Options")
        self.options_menu.setStyleSheet(MENU_STYLE_SHEET)
        
        self.set_host_action = self.options_menu.addAction("Set Host...", self.set_host_dialog)
        self.set_port_action = self.options_menu.addAction("Set Port...", self.set_port_dialog)
        self.options_menu.addSeparator()
        self.set_buffer_size_action = self.options_menu.addAction("Set Buffer Size...", self.set_buffer_size_dialog)
        self.save_buffer_action = self.options_menu.addAction("Save Buffer...", self.save_buffer)
        self.send_file_action = self.options_menu.addAction("Send File...", self.send_file)
        self.options_menu.addSeparator()
        self.phosphor_color_menu = self.options_menu.addMenu("Phosphor Color")
        self.options_menu.addSeparator()
        self.reconnect_action = self.options_menu.addAction("Reconnect", self.io.reconnect)
        
        self.set_phosphor_vintg = self.phosphor_color_menu.addAction("Vintage Green", lambda: self.set_phosphor_color("vintage"))
        self.set_phosphor_green = self.phosphor_color_menu.addAction("Green", lambda: self.set_phosphor_color("green"))
        self.set_phosphor_amber = self.phosphor_color_menu.addAction("Amber", lambda: self.set_phosphor_color("amber"))
        self.set_phosphor_white = self.phosphor_color_menu.addAction("White", lambda: self.set_phosphor_color("white"))
        
        self.phosphor_color_group = QtGui.QActionGroup(self)
        self.phosphor_color_group.addAction(self.set_phosphor_vintg)
        self.phosphor_color_group.addAction(self.set_phosphor_green)
        self.phosphor_color_group.addAction(self.set_phosphor_amber)
        self.phosphor_color_group.addAction(self.set_phosphor_white)
        
        self.set_phosphor_vintg.setCheckable(True)
        self.set_phosphor_green.setCheckable(True)
        self.set_phosphor_amber.setCheckable(True)
        self.set_phosphor_white.setCheckable(True)
        
        self.set_phosphor_vintg.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "vintage")
        self.set_phosphor_green.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "green")
        self.set_phosphor_amber.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "amber")
        self.set_phosphor_white.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "white")
        self.reconnect_action.setEnabled(False)
    
    def startup(self):
        self.setFixedSize(self.size())
        self.io.set_server_name(self.settings.value("host", DEFAULT_SERVER_NAME))
        self.io.set_server_port(int(self.settings.value("port", DEFAULT_SERVER_PORT)))
        self.io.set_phosphor_color(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR))
        self.io.set_buffer_size(int(self.settings.value("buffsize", DEFAULT_BUFFER_SIZE)))
        self.io.startup()
        
    def set_phosphor_color(self, color):
        self.io.set_phosphor_color(color)
        self.settings.setValue("phosphor_color", color)
        
    def set_status(self, txt):
        self.statusBar().setPalette(self.palette)
        self.status_label.setPalette(self.palette)
        self.status_label.setText(txt)
    
    @QtCore.Slot()
    def enable_reconnect(self):
        self.reconnect_action.setEnabled(True)
        
    @QtCore.Slot()
    def disable_reconnect(self):
        self.reconnect_action.setEnabled(False)
    
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
        host, ok = QtGui.QInputDialog.getText(self, "Set Host", "Enter host address:", text=self.settings.value("host", DEFAULT_SERVER_NAME))
        if ok:
            self.settings.setValue("host", host)
            self.io.set_server_name(host)
            self.io.reset()
        
    @QtCore.Slot()
    def set_port_dialog(self):
        port, ok = QtGui.QInputDialog.getInt(self, "Set Port", "Enter port number:", value=int(self.settings.value("port", DEFAULT_SERVER_PORT)))
        if ok:
            self.settings.setValue("port", port)
            self.io.set_server_port(port)
            self.io.reset()
    
    @QtCore.Slot()
    def set_buffer_size_dialog(self):
        n_lines, ok = QtGui.QInputDialog.getInt(self, "Set Buffser Size", "Maximum Buffer Size (in lines):", value=int(self.settings.value("buffsize", DEFAULT_BUFFER_SIZE)))
        if ok:
            self.settings.setValue("buffsize", n_lines)
            self.io.set_buffer_size(n_lines)
    
    @QtCore.Slot()
    def save_buffer(self):
        path, _ = QtGui.QFileDialog.getSaveFileName(self, "Save Buffer")
        if path:
            with open(path, "w") as f:
                f.write(self.io.get_buffer_contents())
        
    @QtCore.Slot()
    def send_file(self):
        path, _ = QtGui.QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self.io.send_file(path)
            
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = TerminalWindow()
    win.show()
    app.exec_()
    
