import os
import re
import sys

from PySide import QtCore, QtGui, QtNetwork

import terminal2_rc

N_HORZ_CHARS = 80
N_VERT_LINES = 25

DEFAULT_SERVER_NAME = "localhost"
DEFAULT_SERVER_PORT = 6800
DEFAULT_PHOSPHOR_COLOR = "vintage"
DEFAULT_BRIGHTNESS  = 1.0
DEFAULT_AA_FLAG     = True

UNKNOWN_CODE       = chr(0)
CONTROL_CODE       = chr(128)
ECHO_NORMAL_CODE   = chr(129)
ECHO_PASSWORD_CODE = chr(130)
ASSIGN_PORT_CODE   = chr(131)
WHO_CODE           = chr(132)
BREAK_CODE         = chr(133)
LINEFEED_CODE      = chr(134)
END_CONTROL_CODE   = chr(254)

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

class FontGlyphs(object):

    ord_BS = 8
    ord_CR = 13
    ord_LF = 10
    ord_SP = 32
    ord_BK = 128
    
    def __init__(self, path):
        self.cell_width = 10
        self.cell_height = 22
        self.glyphColor = {}
        
        if path.endswith(".glyphs"):
            self.glyphs = self.load(path)
        elif path.endswith(".bmp"):
            self.glyphs = self.loadGlyphPixmaps(path)
            self.colored_glyphs = {}
        else:
            self.glyphs = self.loadGlyphData(path)
            
    def load(self, path):
        import cPickle as pickle
        with open(path, "r") as f:
            return pickle.load(f)
            
    def save(self, path):
        import cPickle as pickle
        with open(path, "w") as f:
            pickle.dump(self.glyphs, f)
    
    def createColoredGlyphs(self, name, color):
        self.glyphColor[name] = color
        try:
            self.colored_glyphs[name] = []
            for glyph in self.glyphs:
                colored_glyph = glyph.copy()
                painter = QtGui.QPainter(colored_glyph)
                painter.setCompositionMode(QtGui.QPainter.CompositionMode_Multiply)
                painter.fillRect(colored_glyph.rect(), color)
                self.colored_glyphs[name].append(colored_glyph)
            # end for
        except:
            pass
        
    def loadGlyphPixmaps(self, path):
        pixmap = QtGui.QPixmap(path)
        ncells = pixmap.width() // self.cell_width
        return [ pixmap.copy(QtCore.QRect(x * self.cell_width, 0, self.cell_width, self.cell_height)) for x in range(ncells) ]
        
    def loadGlyphData(self, path):
        with open(path) as f:
        
            bytecodes = []
            while True:
                c = f.read(1)
                if c == "{":
                    break
                    
            while True:
                bytecode = self._next_bytecode(f)
                if bytecode:
                    u = ast.literal_eval(bytecode)
                    bytecodes.append(u)
                else:
                    break
                    
            # xlat_entries = []
            # while True:
                # c = f.read(1)
                # if c == "{":
                    # break
                    
            # while True:
                # bytecode = self._next_bytecode(f)
                # if bytecode:
                    # u = ast.literal_eval(bytecode)
                    # xlat_entries.append(u)
                # else:
                    # break
                    
        # Each list of 8 bytecodes represents an 8x8 pixel matrix: 'A' = [ 0x10,0x28,0x44,0x82,0xAA,0x82,0x82 ]
        # Each list of 8 bytecodes must be converted to a list of bit-lists: 'A' = [ [0,0,0,1,0,0,0,0], ... ]
        return [ self._pixel_matrix(bytecodes[i:i+8]) for i in range(0, len(bytecodes), 8) ]
        
    def _next_bytecode(self, f):
        c = self._skip_ws(f)
        if c == "}":
            return None
        s = ""
        while c != ",":
            s += c
            c = f.read(1)
        return s.strip()
        
    def _skip_ws(self, f):
        in_comment = False
        while True:
            c = f.read(1)
            if c.isspace():
                continue
            elif c == "/":
                c = f.read(1)
                if c == "*" or in_comment:
                    in_comment = True
                    continue
                elif c == "/":
                    # eat line comment to EOL
                    while c != "\n":
                        c = f.read(1)
                    continue
            elif c == "*":
                c = f.read(1)
                if c == "/":
                    in_comment = False
                    continue
                elif in_comment:
                    continue
            elif in_comment:
                continue
            return c
            
    def _pixel_matrix(self, m):
        def binary(n):
            result = []
            for i in range(8):
                result.append(n & 1)
                n = n >> 1
            return list(reversed(result))
            
        return map(binary, m)
    
#-- end class FontGlyphs

class GlassTTY(QtGui.QWidget):

    lineFeed = QtCore.Signal()
    breakSignal = QtCore.Signal()
    returnPressed = QtCore.Signal()
    charTyped = QtCore.Signal(str)
    
    NCHARS = N_HORZ_CHARS
    NLINES = N_VERT_LINES
    MARGIN = 4
    
    CURSOR_BLOCK = 0
    CURSOR_LINE  = 5
    
    class RasterLine(list):
        def __init__(self, n):
            super(GlassTTY.RasterLine, self).__init__()
            self.extend([ chr(0) for i in range(n) ])
        def cleared(self):
            for i in range(len(self)):
                self[i] = chr(0)
            return self
    #-- end class RasterLine
    
    def __init__(self, phosphor_color=DEFAULT_PHOSPHOR_COLOR, aa=DEFAULT_AA_FLAG, parent=None):
        super(GlassTTY, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        
        self.aa = aa
        self.opacity = DEFAULT_BRIGHTNESS
        self.wincolor = QtGui.QColor(0, 0, 0)
        
        self.font = FontGlyphs(":/UiCrt2_Charset.bmp" if aa else ":/UiCrt2_Charset_noaa.bmp")
        self.font.createColoredGlyphs("vintage", QtGui.QColor(57, 255, 174)) #QtGui.QColor(50, 221, 151))
        self.font.createColoredGlyphs("green",   QtGui.QColor(96, 255, 96)) #QtGui.QColor("lightgreen"))
        self.font.createColoredGlyphs("amber",   QtGui.QColor(255, 215, 0)) #QtGui.QColor("gold"))
        self.font.createColoredGlyphs("white",   QtGui.QColor(240, 248, 255)) #QtGui.QColor("aliceblue"))
        
        self.setPhosphorColor(phosphor_color)
        
        self.raster_lines = [ GlassTTY.RasterLine(self.NCHARS) for i in range(self.NLINES) ]
        self.cursorx = 0
        self.cursory = 0
        self.cursor_blink = True
        self.cursor_visible = True
        self.cursor_glyph = self.CURSOR_BLOCK
        
        self.buffered = False
        self.input_buffer = ""
        self.autoLF = True
        self.autoCR = True
        
        self.setConnected(False)
        self.startTimer(500)
    
    def sizeHint(self):
        #== We are a fixed-size widget containing (NCHARS x NLINES) monospaced character cells
        #== and a small border margin
        w = (self.font.cell_width * self.NCHARS) + self.MARGIN * 2
        h = (self.font.cell_height * self.NLINES) + self.MARGIN * 2
        return QtCore.QSize(w, h)
        
    def setConnected(self, flag):
        self.connected = flag
        self.cursor_visible = flag
        self.update()
        
    def setEchoMode(self, mode):
        self.echoMode = mode
        
    def setPhosphorColor(self, phosphor_color):
        try:
            self.glyphs = self.font.colored_glyphs[phosphor_color]
        except:
            self.glyphs = self.font.glyphs
            
            fontcolor = self.font.glyphColor[phosphor_color]
            pixel = QtGui.QPen(fontcolor)
            if self.aa:
                dim = QtGui.QPen(fontcolor.darker(300)) # 400))
                dimmer = QtGui.QPen(fontcolor.darker(600)) # 800))
            else:
                dim = dimmer = QtGui.QPen(self.wincolor)
                
            self.aa_pen_matrix = [
                dimmer,  dim,  dimmer,
                   dim, pixel, dim,
                dimmer,  dim,  dimmer
            ]
        # end try
        self.update()
    
    def setBrightness(self, value):
        self.opacity = value
        self.update()
        self.repaint()
        
    #==================================#
    #== HIGH-LEVEL RASTER MANAGEMENT ==#
    #==================================#
    
    def addCharacters(self, text):
        """
        Add a string of characters, one at a time, to the display raster matrix.
        """
        for c in text:
            if ord(c) == self.font.ord_CR:
                self.cursorx = 0
                if self.autoLF:
                    self.cursory += 1
            elif ord(c) == self.font.ord_LF:
                self.cursory += 1
                if self.autoCR:
                    self.cursorx = 0
            elif ord(c) == self.font.ord_BS:
                self.delCharacters(1)
            else:
                self.raster_lines[self.cursory][self.cursorx] = c
                self.cursorx += 1
                if self.cursorx == self.NCHARS:
                    self.cursorx = 0
                    self.cursory += 1
                # end if
            # end if
            if self.cursory == self.NLINES:
                line = self.raster_lines.pop(0)
                self.raster_lines.append(line.cleared())
                self.cursory -= 1
            # end if
        # end for
        self.update()
        
    def delCharacters(self, nchars_to_delete):
        """
        Delete the last nchars_to_delete characters from the display raster matrix,
        relative to the current raster 'cursor' position.
        """
        prevx = self.cursorx - nchars_to_delete
        if prevx >= 0:
            self.raster_lines[self.cursory][prevx:self.cursorx] = [chr(0)] * nchars_to_delete
            self.cursorx = prevx
        # end if
        self.update()

    #==================================#
    #==       CURSOR MANAGEMENT      ==#
    #==================================#
    
    def cursorPos(self):
        return QtCore.QPoint(self.cursorx, self.cursory)
        
    def cursorRect(self):
        return QtCore.QRect(self.cursorx, self.cursory, self.font.cell_width, self.font.cell_height)
    
    def setCursorStyle(self, style):
        self.cursor_glyph = style
        
    def showCursor(self):
        self.cursor_visible = True
        self._repaint_cursor()
        
    def hideCursor(self):
        self.cursor_visible = False
        self._repaint_cursor()

    def toggleCursor(self):
        self.cursor_visible = not self.cursor_visible
        self._repaint_cursor()
        
    def _repaint_cursor(self):
        self.update(self.cursorRect())
        self.repaint()
    
    #================================#
    #== KEYBOARD BUFFER MANAGEMENT ==#
    #================================#
    
    def add_to_input_buffer(self, c):
        self.input_buffer += c
        
    def delete_from_input_buffer(self, n):
        self.input_buffer = self.input_buffer[:-n]
        
    def text(self):
        return self.input_buffer
        
    def clear(self):
        self.input_buffer = ""
        
    #===============================#
    #==     QT EVENT HANDLERS     ==#
    #===============================#
    
    def keyPressEvent(self, event):
        if not event.text():
            if event.key() == QtCore.Qt.Key_Down: # Linefeed key
                # print "Send LINEFEED"
                self.lineFeed.emit()
            elif event.key() == QtCore.Qt.Key_Pause: # Break key
                # print "Send BREAK"
                self.breakSignal.emit()
                
        for c in str(event.text()):
            if self.buffered:
                if ord(c) == self.font.ord_BS:
                    self.delete_from_input_buffer(1)
                    if self.echoMode == QtGui.QLineEdit.Normal:
                        self.delCharacters(1)
                    
                elif ord(c) == self.font.ord_CR:
                    if self.echoMode == QtGui.QLineEdit.Normal:
                        self.delCharacters(len(self.input_buffer))
                    self.returnPressed.emit()
                    
                elif chr(1) <= c < (' '):
                    pass
                    
                elif (' ') <= c <= ('~'):
                    self.add_to_input_buffer(c)
                    if self.echoMode == QtGui.QLineEdit.Normal:
                        self.addCharacters(c)
            else:
                # print "Send char: %r (%d)" % (c, ord(c))
                self.charTyped.emit(c)
                
        # print hex(event.key())
    
    def timerEvent(self, event):
        if not self.connected:
            self.hideCursor()
        elif self.cursor_blink:
            self.toggleCursor()
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), self.wincolor)
        painter.setOpacity(self.opacity)
        
        #== If we aren't just repainting the cursor, then redraw all the characters on the screen
        if event.rect() != self.cursorRect():
            cellx = celly = 0
            for line in self.raster_lines:
                cellx = 0
                for c in line:
                    if ord(c):
                        try:
                            self._draw_glyph(painter, self.glyphs[ord(c)], cellx, celly)
                        except:
                            print repr(c), ord(c)
                    cellx += 1
                # end for
                celly += 1
            # end for
        # end if
        
        if self.cursor_visible:
            self._draw_glyph(painter, self.glyphs[self.cursor_glyph], self.cursorx, self.cursory)
        else:
            self._draw_glyph(painter, self.glyphs[self.font.ord_SP], self.cursorx, self.cursory)
        
    def _draw_glyph(self, painter, glyph, cellx, celly):
        s = cellx * self.font.cell_width + self.MARGIN
        y = celly * self.font.cell_height + self.MARGIN
        
        if isinstance(glyph, QtGui.QPixmap):
            #== If the glyph is a pixmap, then just blit it to the viewport
            painter.drawPixmap(s, y, glyph)
        else:
            #== Otherwise we draw the glyph ourselves pixel by pixel
            painter.fillRect(QtCore.QRect(s, y, self.font.cell_width, self.font.cell_height), self.wincolor)
            mode = painter.compositionMode()
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Lighten)
            for row in glyph:
                x = s
                for pixel in row:
                    if pixel:
                        self._draw_pixel(painter, x, y)
                    x += 1
                # end for
                y += 2
            # end for
            painter.setCompositionMode(mode)
        
    def _draw_pixel(self, painter, x, y):
        #== x and y are the coordinates of the upper-right corner of
        #== the full 10x22 character cell. The 8x16 glyph pixel matrix
        #== needs to be centered within this cell, so we offset our
        #== pixel drawing by 1,3.
        pen = iter(self.aa_pen_matrix)
        for dy in [-1, 0, +1]:
            for dx in [-1, 0, +1]:
                painter.setPen(pen.next())
                painter.drawPoint(x + dx + 1, y + dy + 3)
    
    def as_str(self):
        return "\n".join(filter(None, [ "".join(filter(None, line)) for line in self.raster_lines ]))
    
#-- end class GlassTTY

class TerminalIO(QtGui.QWidget):
    
    setNormalStatus = QtCore.Signal(str)
    setConnectStatus = QtCore.Signal(str)
    setErrorStatus = QtCore.Signal(str)
    
    def __init__(self, phosphor_color, parent=None):
        super(TerminalIO, self).__init__(parent)
        self.ME = self.__class__.__name__
        
        self.name = QtNetwork.QHostInfo.localHostName()
        self.host = DEFAULT_SERVER_NAME
        self.port = DEFAULT_SERVER_PORT
        
        self.socket = QtNetwork.QTcpSocket(self)
        self.socket.error.connect(self.socket_error)
        self.socket.hostFound.connect(self.host_found)
        self.socket.connected.connect(self.connection_made)
        self.socket.disconnected.connect(self.connection_lost)
        self.socket.readyRead.connect(self.data_available)
        self.com_port = 0
        
        self.ttyio = GlassTTY(phosphor_color)
        
        self.output = self.ttyio
        self.input = self.ttyio
        self.input.setEnabled(False)
        self.input.charTyped.connect(self.send_char)
        self.input.returnPressed.connect(self.send_string)
        self.input.lineFeed.connect(self.send_linefeed)
        self.input.breakSignal.connect(self.send_break_signal)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.ttyio)
        
        self.setLayout(layout)
        
    def startup(self):
        self.socket.connectToHost(self.host, self.port)
        
    @QtCore.Slot("QAbstractSocket.SocketError")
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
        
    @QtCore.Slot(str)
    def send_char(self, c):
        # print self.ME, "charTyped:", c
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            # print self.ME, "sending:", repr(c)
            n = self.socket.write(DataPacket.Out(c))
            # print self.ME, n, "bytes sent"
            self.socket.flush()
        
    @QtCore.Slot()
    def send_string(self):
        s = self.input.text().strip() + "\r"
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
        self.output.setConnected(False)
        if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.socket.disconnectFromHost()
        
    @QtCore.Slot()
    def reconnect(self):
        self.socket.connectToHost(self.host, self.port)
        
    @QtCore.Slot(str)
    def display(self, txt):
        self.output.addCharacters(txt)
        
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
        self.ttyio.setPhosphorColor(phosphor_color)
        
    def set_brightness(self, brightness):
        self.ttyio.setBrightness(brightness)
        
#-- end class TerminalIO

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
        self.setWindowIcon(QtGui.QIcon(":/terminal.png"))
        self.setStyleSheet("QMainWindow { background: #444444; border: 1px solid #252525; }")
        
        self.palette = QtGui.QPalette()
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x444444))
        self.palette.setColor(QtGui.QPalette.Text,       QtCore.Qt.black)
        
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
        self.menuBar().setNativeMenuBar(False)
        self.menuBar().setStyleSheet(MENUBAR_STYLE_SHEET)
        
        self.options_menu = self.menuBar().addMenu("Options")
        self.options_menu.setStyleSheet(MENU_STYLE_SHEET)
        
        self.set_host_action = self.options_menu.addAction("Set Host...", self.set_host_dialog)
        self.set_port_action = self.options_menu.addAction("Set Port...", self.set_port_dialog)
        self.options_menu.addSeparator()
        self.phosphor_color_menu = self.options_menu.addMenu("Phosphor Color")
        self.brightness_action = self.options_menu.addAction("Brightness...", self.set_brightness)
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
        self.io.set_server_port(self.settings.value("port", DEFAULT_SERVER_PORT))
        self.io.set_phosphor_color(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR))
        self.io.set_brightness(float(self.settings.value("brightness", DEFAULT_BRIGHTNESS)))
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
        host, ok = QtGui.QInputDialog.getText(None, "Set Host", "Enter host address:", text=self.settings.value("host", DEFAULT_SERVER_NAME))
        if ok:
            self.settings.setValue("host", host)
            self.io.set_server_name(host)
            self.io.reset()
        
    @QtCore.Slot()
    def set_port_dialog(self):
        port, ok = QtGui.QInputDialog.getInt(None, "Set Port", "Enter port number:", value=self.settings.value("port", DEFAULT_SERVER_PORT))
        if ok:
            self.settings.setValue("port", port)
            self.io.set_server_port(port)
            self.io.reset()
    
    @QtCore.Slot()
    def set_brightness(self):
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(float(self.settings.value("brightness", DEFAULT_BRIGHTNESS)) * 100))
        slider.valueChanged[int].connect(self.on_brightness_changed)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(slider)
        
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle("Set Brightness")
        dialog.setLayout(layout)
        dialog.exec_()
    
    @QtCore.Slot(int)
    def on_brightness_changed(self, value):
        value /= 100.0
        self.settings.setValue("brightness", value)
        self.io.set_brightness(value)
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
#-- end class TerminalWindow

if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = TerminalWindow()
    win.show()
    app.exec_()
    