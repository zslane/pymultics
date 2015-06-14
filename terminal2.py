import os
import re
import sys

from PySide import QtCore, QtGui, QtNetwork

import terminal2_rc

N_HORZ_CHARS = 80
N_VERT_LINES = 25

DEFAULT_SERVER_NAME    = "localhost"
DEFAULT_SERVER_PORT    = 6800
DEFAULT_PHOSPHOR_COLOR = "vintage"
DEFAULT_BRIGHTNESS     = 1.0
DEFAULT_CURSOR_BLINK   = True
DEFAULT_AA_FLAG        = True

UNKNOWN_CODE       = chr(0)
CONTROL_CODE       = chr(128)
ECHO_NORMAL_CODE   = chr(129)
ECHO_PASSWORD_CODE = chr(130)
ASSIGN_PORT_CODE   = chr(131)
WHO_CODE           = chr(132)
BREAK_CODE         = chr(133)
END_CONTROL_CODE   = chr(254)

BEL = chr(7)
BS  = chr(8)
TAB = chr(9)
LF  = chr(10)
CR  = chr(13)
ESC = chr(27)

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
                painter = QtGui.QPainter()
                if painter.begin(colored_glyph):
                    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Multiply)
                    painter.fillRect(colored_glyph.rect(), color)
                    self.colored_glyphs[name].append(colored_glyph)
                    painter.end()
                # end if
            # end for
        except:
            pass
        
    def loadGlyphPixmaps(self, path):
        pixmap = QtGui.QPixmap(path)
        ncells = pixmap.width() // self.cell_width
        #== We ultimately create QImages so we can use the Multiply blending mode in createColoredGlyphs()
        return [ pixmap.copy(QtCore.QRect(x * self.cell_width, 0, self.cell_width, self.cell_height)).toImage() for x in range(ncells) ]
        
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

    breakSignal = QtCore.Signal()
    xmitChars = QtCore.Signal(str)
    
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
        def clear(self, start=0, end=-1):
            if end == -1:
                end = len(self)
            if end < start:
                start, end = end, start
            self[start:end] = [ chr(0) for i in range(end - start) ]
            
    #-- end class RasterLine
    
    def __init__(self, phosphor_color=DEFAULT_PHOSPHOR_COLOR, aa=DEFAULT_AA_FLAG, parent=None):
        super(GlassTTY, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        
        self.aa = aa
        self.opacity = DEFAULT_BRIGHTNESS
        
        self.font = FontGlyphs(":/UiCrt2_Charset.bmp" if aa else ":/UiCrt2_Charset_noaa.bmp")
        self.font.createColoredGlyphs("vintage", QtGui.QColor(57, 255, 174)) #QtGui.QColor(50, 221, 151))
        self.font.createColoredGlyphs("green",   QtGui.QColor(96, 255, 96)) #QtGui.QColor("lightgreen"))
        self.font.createColoredGlyphs("amber",   QtGui.QColor(255, 215, 0)) #QtGui.QColor("gold"))
        self.font.createColoredGlyphs("white",   QtGui.QColor(240, 248, 255)) #QtGui.QColor("aliceblue"))
        
        self.raster_lines = [ GlassTTY.RasterLine(self.NCHARS) for i in range(self.NLINES) ]
        
        self.cursorx = 0
        self.cursory = 0
        self.cursor_blink = True
        self.cursor_visible = True
        self.cursor_glyph = self.CURSOR_BLOCK
        self.cursor_line1 = QtCore.QLine(QtCore.QPoint(0, -1), QtCore.QPoint(8, -1))
        self.cursor_line2 = QtCore.QLine(QtCore.QPoint(1, 0), QtCore.QPoint(9, 0))
        self.cursor_pen = QtGui.QPen()
        self.cursor_pen.setDashPattern([1, 1])
        
        self.autoLF = True
        self.autoCR = True
        self.control_code_state = 0
        
        self.setPhosphorColor(phosphor_color)
        self.resetScrollRange()
        
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
        self.fontcolor = self.font.glyphColor[phosphor_color]
        self.wincolor = self.fontcolor.darker(1500)
        self.cursor_pen.setColor(self.fontcolor)
        
        try:
            self.glyphs = self.font.colored_glyphs[phosphor_color]
        except:
            self.glyphs = self.font.glyphs
            
            pixel = QtGui.QPen(self.fontcolor)
            if self.aa:
                dim = QtGui.QPen(self.fontcolor.darker(300)) # 400))
                dimmer = QtGui.QPen(self.fontcolor.darker(600)) # 800))
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
            #== Process control code
            if c == ESC or self.control_code_state:
                if self.process_control_code(c):
                    continue
                    
            #== CR/LF/backspace
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
                
            #== All other characters
            else:
                self.raster_lines[self.cursory][self.cursorx] = c
                self.cursorx += 1
                if self.cursorx == self.NCHARS:
                    self.cursorx = 0
                    self.cursory += 1
                # end if
            # end if
            
            #== Scroll display if necessary
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

    def resetScrollRange(self, first=1, last=NLINES):
        self.scroll_first = first
        self.scroll_last = last
        
    def scrollUp(self, n_lines=1):
        for i in range(n_lines):
            line = self.raster_lines.pop(self.scroll_first - 1)
            self.raster_lines.insert(self.scroll_last - 1, line.cleared())
        self.update()
        
    def scrollDown(self, n_lines=1):
        for i in range(n_lines):
            line = self.raster_lines.pop(self.scroll_last - 1)
            self.raster_lines.insert(self.scroll_first - 1, line.cleared())
        self.update()
    
    def eraseEndOfLine(self):
        self.raster_lines[self.cursory].clear(self.cursorx)
        
    def eraseStartOfLine(self):
        self.raster_lines[self.cursory].clear(0, self.cursorx + 1)
    
    def eraseLine(self):
        self.raster_lines[self.cursory].clear()
        
    def eraseDown(self):
        for line in self.raster_lines[self.cursory:self.NLINES]:
            line.clear()
            
    def eraseUp(self):
        for line in self.raster_lines[0:self.cursory + 1]:
            line.clear()
            
    def eraseScreen(self):
        # self.raster_lines = [ GlassTTY.RasterLine(self.NCHARS) for i in range(self.NLINES) ]
        for line in self.raster_lines:
            line.clear()
        self.moveCursorTo(0, 0)
        self.update()
    
    #==================================#
    #==       CURSOR MANAGEMENT      ==#
    #==================================#
    
    def cursorPos(self):
        x = self.cursorx * self.font.cell_width + self.MARGIN
        y = self.cursory * self.font.cell_height + self.MARGIN
        return QtCore.QPoint(x, y)
        
    def cursorRect(self):
        return QtCore.QRect(self.cursorPos(), QtCore.QSize(self.font.cell_width, self.font.cell_height))
    
    def setCursorStyle(self, style):
        self.cursor_glyph = style
        
    def setCursorBlink(self, blink):
        self.cursor_blink = blink
        if self.connected:
            self.showCursor()
        
    def showCursor(self):
        self.cursor_visible = True
        self._repaint_cursor()
        
    def hideCursor(self):
        self.cursor_visible = False
        self._repaint_cursor()
        
    def toggleCursor(self):
        self.cursor_visible = not self.cursor_visible
        self._repaint_cursor()
        
    def moveCursor(self, dx, dy):
        if self.cursor_visible:
            #== Erase from old position
            self.cursor_visible = False
            self._repaint_cursor()
            self.cursor_visible = True
        #== Draw in new position
        self.cursorx = min(self.NCHARS-1, max(0, self.cursorx + dx))
        self.cursory = min(self.NLINES-1, max(0, self.cursory + dy))
        self._repaint_cursor()
        
    def moveCursorTo(self, x, y):
        if self.cursor_visible:
            #== Erase from old position
            self.cursor_visible = False
            self._repaint_cursor()
            self.cursor_visible = True
        #== Draw in new position
        self.cursorx = min(self.NCHARS-1, max(0, x))
        self.cursory = min(self.NLINES-1, max(0, y))
        self._repaint_cursor()
        
    def _repaint_cursor(self):
        self.repaint(self.cursorRect())
    
    #==================================#
    #==  CONTROL CODE STATE MACHINE  ==#
    #==================================#
    
    def process_control_code(self, c):
        #== State machine for processing VT100 control codes
        
        (CC_NONE,
         CC_BEGIN,
         CC_TYPE1,
         CC_NUM1,
         CC_NUM2,
        ) = range(5)
        
        def start():
            self.control_code_state = CC_BEGIN
            return True
        def next(state):
            self.control_code_state = state
            return True
        def same():
            #== Don't change state
            return True
        def done():
            self.control_code_state = 0
            return True
        def failed():
            self.control_code_state = 0
            return False
        
        if self.control_code_state == 0:
            assert c == ESC
            return start()
            
        elif self.control_code_state == CC_BEGIN:
            self._cc_n1 = ""
            if c == '[':
                return next(CC_TYPE1)
            elif c == 'D':
                self.scrollDown()
                return done()
            elif c == 'M':
                self.scrollUp()
                return done()
            # end if
            
        elif self.control_code_state == CC_TYPE1:
            if c.isdigit():
                self._cc_n1 = c
                return next(CC_NUM1)
            elif c == 'A':
                self.moveCursor(0, -1)
                return done()
            elif c == 'B':
                self.moveCursor(0, 1)
                return done()
            elif c == 'C':
                self.moveCursor(1, 0)
                return done()
            elif c == 'c':
                # Respond with device code
                self.send_control_code_response("[x0c")
                return done()
            elif c == 'D':
                self.moveCursor(-1, 0)
                return done()
            elif c == 'H' or c == 'f':
                self.moveCursorTo(0, 0)
                return done()
            elif c == 'J':
                self.eraseDown()
                return done()
            elif c == 'K':
                self.eraseEndOfLine()
                return done()
            elif c == 'r' and not self._cc_n1:
                self.resetScrollRange()
                return done()
            # end if
            
        elif self.control_code_state == CC_NUM1:
            if c.isdigit():
                self._cc_n1 += c
                return same()
            elif c == ';':
                self._cc_n2 = ""
                return next(CC_NUM2)
            elif c == 'n':
                request_code = int(self._cc_n1)
                if request_code == 5:
                    # Respond with device status ok
                    self.send_control_code_response("[0n")
                    return done()
                elif request_code == 6:
                    # Respond with cursor position
                    self.send_control_code_response("[%d;%dR"%(self.cursory + 1, self.cursorx + 1))
                    return done()
                #end if
            elif c == 'A':
                count = int(self._cc_n1)
                self.moveCursor(0, -count)
                return done()
            elif c == 'B':
                count = int(self._cc_n1)
                self.moveCursor(0, count)
                return done()
            elif c == 'C':
                count = int(self._cc_n1)
                self.moveCursor(count, 0)
                return done()
            elif c == 'D':
                count = int(self._cc_n1)
                self.moveCursor(-count, 0)
                return done()
            elif c == 'J':
                code = int(self._cc_n1)
                if code == 1:
                    self.eraseUp()
                    return done()
                elif code == 2:
                    self.eraseScreen()
                    return done()
                # end if
            elif c == 'K':
                code = int(self._cc_n1)
                if code == 1:
                    self.eraseStartOfLine()
                    return done()
                elif code == 2:
                    self.eraseLine()
                    return done()
                # end if
            # end if
            
        elif self.control_code_state == CC_NUM2:
            if c.isdigit():
                self._cc_n2 += c
                return same()
            elif self._cc_n2:
                if c == 'H' or c == 'f':
                    row = int(self._cc_n1)
                    col = int(self._cc_n2)
                    self.moveCursorTo(row - 1, col - 1)
                    return done()
                elif c == 'r':
                    start = int(self._cc_n1)
                    end = int(self._cc_n2)
                    self.resetScrollRange(start, end)
                    return done()
                # end if
            # end if
        # end if
        
        #== Special case: failed the code parse on new ESC char;
        #== just begin control code parsing again from the start
        if c == ESC:
            return start()
            
        #== Otherwise stop parsing and process new char normally
        return failed()
        
    def send_control_code_response(self, code):
        self.xmitChars.emit(ESC + code)
        
    #===============================#
    #==     QT EVENT HANDLERS     ==#
    #===============================#
    
    def keyPressEvent(self, event):
        #== NON-ASCII KEYSTROKE ==#
        if not event.text():
            if event.key() == QtCore.Qt.Key_Pause: # Break key
                # print "Send BREAK"
                self.breakSignal.emit()
            elif event.key() == QtCore.Qt.Key_Down: # Linefeed key
                # print "Send LINEFEED"
                self.xmitChars.emit(LF)
                
        #== ASCII KEYSTROKE ==#
        for c in str(event.text()):
            if c == BEL:
                self.ring_bell()
                
            # print "Send char: %r (%d)" % (c, ord(c))
            self.xmitChars.emit(c)
            
    def timerEvent(self, event):
        if not self.connected:
            self.hideCursor()
        elif self.cursor_blink:
            self.toggleCursor()
        
    def paintEvent(self, event):
        #== Get a QImage of the widget's current pixel contents as our painting canvas
        canvas = QtGui.QPixmap.grabWindow(self.winId()).toImage()
        
        #== We paint on this QImage object instead of directly on the widget. Doing so gives us
        #== full access to all the Qt composition/blending modes.
        painter = QtGui.QPainter()
        if painter.begin(canvas):
            painter.fillRect(event.rect(), self.wincolor)
            
            painter.save()
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Lighten)
            painter.setOpacity(self.opacity) # <-- this is how phosphor brightness is implemented
            
            char_under_cursor = ord(self.raster_lines[self.cursory][self.cursorx]) or self.font.ord_SP
            
            #== If we aren't just repainting the cursor, then redraw all the characters on the screen
            if event.rect() == self.cursorRect():
                self._draw_glyph(painter, self.glyphs[char_under_cursor], self.cursorx, self.cursory)
                
            else:
                cellx = celly = 0
                for line in self.raster_lines:
                    cellx = 0
                    for c in line:
                        if ord(c):
                            try:
                                self._draw_glyph(painter, self.glyphs[ord(c)], cellx, celly)
                            except:
                                print "Bad character code for display:", repr(c), ord(c)
                            # end try
                        cellx += 1
                    # end for
                    celly += 1
                # end for
            # end if
            
            if self.cursor_visible:
                if self.cursor_glyph == self.CURSOR_BLOCK:
                    # painter.setCompositionMode(QtGui.QPainter.CompositionMode_Difference)     # solid
                    # painter.fillRect(self.cursorRect().adjusted(0, 1, 0, -3), self.fontcolor) # block
                    self._draw_glyph(painter, self.glyphs[0], self.cursorx, self.cursory) # glyph block
                else:
                    # painter.fillRect(self.cursorRect().adjusted(0, self.font.cell_height-3, 0, -1), self.fontcolor) # solid line
                    p = self.cursorRect().bottomLeft() # dotted
                    painter.setPen(self.cursor_pen)    # line
                    painter.drawLines([self.cursor_line1.translated(p), self.cursor_line2.translated(p)]) # dotted line
                # end if
            # end if
            
            painter.restore()
            painter.end()
        # endif
        
        #== Now blit the painted image to the widget
        if painter.begin(self):
            painter.drawImage(0, 0, canvas)
            painter.end()
        
    def _draw_glyph(self, painter, glyph, cellx, celly):
        s = cellx * self.font.cell_width + self.MARGIN
        y = celly * self.font.cell_height + self.MARGIN
        
        if isinstance(glyph, QtGui.QPixmap):
            #== If the glyph is a pixmap, then just blit it to the canvas
            painter.drawPixmap(s, y, glyph)
            
        elif isinstance(glyph, QtGui.QImage):
            #== If the glyph is an image, then just blit it to the canvas
            painter.drawImage(s, y, glyph)
            
        else:
            #== Otherwise we draw the glyph ourselves pixel by pixel
            painter.fillRect(QtCore.QRect(s, y, self.font.cell_width, self.font.cell_height), self.wincolor)
            for row in glyph:
                x = s
                for pixel in row:
                    if pixel:
                        self._draw_pixel(painter, x, y)
                    x += 1
                # end for
                y += 2
        
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
    
    def ring_bell(self):
        QtGui.QApplication.beep()
    
    def as_str(self):
        return "\n".join(filter(None, [ "".join(filter(None, line)) for line in self.raster_lines ]))
    
#-- end class GlassTTY

class TerminalEnclosure(QtGui.QFrame):

    def __init__(self, ttyio, parent=None):
        super(TerminalEnclosure, self).__init__(parent)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.ttyio = ttyio
        self.image = QtGui.QImage(":/terminal_enclosure.png")
        
    def sizeHint(self):
        return self.image.size()
        
    def paintEvent(self, event):
        canvas = self.image.copy()
        painter = QtGui.QPainter()
        if painter.begin(canvas):
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Lighten)
            painter.fillRect(event.rect(), self.ttyio.wincolor)
            painter.end()
        if painter.begin(self):
            painter.drawImage(0, 0, canvas)
            painter.end()
        
#-- end class TerminalEnclosure

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
        
        self.enclosure = TerminalEnclosure(self.ttyio)
        
        tty_layout = QtGui.QHBoxLayout()
        tty_layout.setContentsMargins(0, 0, 0, 0)
        tty_layout.addWidget(self.ttyio, QtCore.Qt.AlignCenter)
        self.enclosure.setLayout(tty_layout)
        
        self.output = self.ttyio
        self.input = self.ttyio
        self.input.setEnabled(False)
        self.input.xmitChars.connect(self.send_chars)
        self.input.breakSignal.connect(self.send_break_signal)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.enclosure)
        
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
    def send_chars(self, c):
        # print self.ME, "xmitChars:", c
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            # print self.ME, "sending:", repr(c)
            n = self.socket.write(DataPacket.Out(c))
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
        self.update()
        
    def set_brightness(self, brightness):
        self.ttyio.setBrightness(brightness)
        
    def set_cursor_style(self, style):
        self.ttyio.setCursorStyle(style)
        
    def set_cursor_blink(self, flag):
        self.ttyio.setCursorBlink(flag)
        
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
        self.setStyleSheet("QMainWindow { background: transparent; border: 0px; }")
        
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
        
        self.options_menu = self.menuBar().addMenu("Options")
        self.options_menu.setStyleSheet(MENU_STYLE_SHEET)
        
        self.set_host_action = self.options_menu.addAction("Set Host...", self.set_host_dialog)
        self.set_port_action = self.options_menu.addAction("Set Port...", self.set_port_dialog)
        self.options_menu.addSeparator()
        self.phosphor_color_menu = self.options_menu.addMenu("Phosphor Color")
        self.brightness_action = self.options_menu.addAction("Brightness...", self.set_brightness)
        self.options_menu.addSeparator()
        self.cursor_style_menu = self.options_menu.addMenu("Cursor Style")
        self.cursor_blink_action = self.options_menu.addAction("Cursor Blink", self.set_cursor_blink)
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
        
        self.set_cursor_block = self.cursor_style_menu.addAction("Block", lambda: self.set_cursor_style(GlassTTY.CURSOR_BLOCK))
        self.set_cursor_line = self.cursor_style_menu.addAction("Line", lambda: self.set_cursor_style(GlassTTY.CURSOR_LINE))
        
        self.cursor_style_group = QtGui.QActionGroup(self)
        self.cursor_style_group.addAction(self.set_cursor_block)
        self.cursor_style_group.addAction(self.set_cursor_line)
        
        self.set_cursor_block.setCheckable(True)
        self.set_cursor_line.setCheckable(True)
        
        self.cursor_blink_action.setCheckable(True)
        
        self.set_phosphor_vintg.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "vintage")
        self.set_phosphor_green.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "green")
        self.set_phosphor_amber.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "amber")
        self.set_phosphor_white.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "white")
        
        self.set_cursor_block.setChecked(self.settings.value("cursor_style", GlassTTY.CURSOR_BLOCK) == GlassTTY.CURSOR_BLOCK)
        self.set_cursor_line.setChecked(self.settings.value("cursor_style", GlassTTY.CURSOR_BLOCK) == GlassTTY.CURSOR_LINE)
        
        self.cursor_blink_action.setChecked(bool(self.settings.value("cursor_blink", DEFAULT_CURSOR_BLINK)))
        
        self.reconnect_action.setEnabled(False)
    
    def startup(self):
        self.setFixedSize(self.size())
        self.io.set_server_name(self.settings.value("host", DEFAULT_SERVER_NAME))
        self.io.set_server_port(self.settings.value("port", DEFAULT_SERVER_PORT))
        self.io.set_phosphor_color(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR))
        self.io.set_brightness(float(self.settings.value("brightness", DEFAULT_BRIGHTNESS)))
        self.io.set_cursor_style(self.settings.value("cursor_style", GlassTTY.CURSOR_BLOCK))
        self.io.set_cursor_blink(bool(self.settings.value("cursor_blink", DEFAULT_CURSOR_BLINK)))
        self.io.startup()
        
    def set_phosphor_color(self, color):
        self.io.set_phosphor_color(color)
        self.settings.setValue("phosphor_color", color)
        
    def set_cursor_style(self, style):
        self.io.set_cursor_style(style)
        self.settings.setValue("cursor_style", style)
        
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
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x444444)) # gray
        self.set_status(txt)
        
    @QtCore.Slot(str)
    def set_connect_status(self, txt):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x445e44)) # green
        self.set_status(txt)
        
    @QtCore.Slot(str)
    def set_error_status(self, txt):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x935353)) # red
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
    
    @QtCore.Slot()
    def set_cursor_blink(self):
        flag = self.cursor_blink_action.isChecked()
        self.io.set_cursor_blink(flag)
        self.settings.setValue("cursor_blink", int(flag))
        
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
#-- end class TerminalWindow

if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = TerminalWindow()
    win.show()
    app.exec_()
    
