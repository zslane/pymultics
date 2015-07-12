import os
import re
import sys
import ast
import time
from pprint import pprint

from PySide import QtCore, QtGui, QtNetwork

import vt100_rc
import QTelnetSocket

N_HORZ_CHARS = 80
N_VERT_LINES = 24

SUPPORTED_PROTOCOLS    = ["pymultics", "telnet"]

DEFAULT_SERVER_NAME    = "localhost"
DEFAULT_SERVER_PORT    = 6800
DEFAULT_PROTOCOL       = "pymultics"
DEFAULT_ARROWKEY_MODE  = True # True is application mode, False is cursor mode
DEFAULT_WRAP_MODE      = True
DEFAULT_REPEAT_MODE    = True
DEFAULT_SCREEN_MODE    = False # True is reverse screen, False is normal screen
DEFAULT_NEWLINE_MODE   = False
DEFAULT_CRECHO_MODE    = True
DEFAULT_LFECHO_MODE    = True
DEFAULT_LOCALECHO_MODE = False
DEFAULT_PHOSPHOR_COLOR = "vintage"
DEFAULT_CHARSET        = "std"
DEFAULT_BRIGHTNESS     = 1.0
DEFAULT_CURSOR_BLINK   = True

UNKNOWN_CODE       = chr(0)
CONTROL_CODE       = chr(129)
ECHO_NORMAL_CODE   = chr(130)
ECHO_PASSWORD_CODE = chr(131)
ASSIGN_PORT_CODE   = chr(132)
WHO_CODE           = chr(133)
BREAK_CODE         = chr(134)
END_CONTROL_CODE   = chr(254)
NULL_CHAR_CODE     = chr(128)

NUL = chr(0)
BEL = chr(7)
BS  = chr(8)
TAB = chr(9)
LF  = chr(10)
CR  = chr(13)
CAN = chr(24)
SUB = chr(26)
ESC = chr(27)
SP  = chr(32)

NRM, BRI, DIM, _, UND, BLI, _, REV, HID, ALL = (0,1,2,4,8,16,32,64,128,256)
GLYPHSET_KEYS = [NRM, UND, REV, UND|REV, BRI, BRI|UND, BRI|REV, BRI|UND|REV, DIM, DIM|UND, DIM|REV, DIM|UND|REV, HID]

PHOSPHOR_COLORS = {
    'vintage': QtGui.QColor(57, 255, 174),
    'green':   QtGui.QColor(96, 255, 96),
    'amber':   QtGui.QColor(255, 215, 0),
    'white':   QtGui.QColor(200, 240, 255),
}

REVERSE_VIDEO_ATTRS = {
    NRM:         NRM|REV,     BRI:         NRM|REV,     DIM:         BRI|REV,
    NRM|UND:     NRM|REV|UND, BRI|UND:     NRM|REV|UND, DIM|UND:     BRI|REV|UND,
    NRM|REV:     NRM,         BRI|REV:     BRI,         DIM|REV:     DIM,
    NRM|REV|UND: NRM|UND,     BRI|REV|UND: BRI|UND,     DIM|REV|UND: DIM|UND,
}

def _debug(s):
    if False:
        sys.stdout.write(s)
        
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

    def __init__(self, path):
        self.cell_width = 10
        self.cell_height = 22
        
        self.glyphs = self.loadGlyphPixmaps(path)
        self.colored_glyphs = {}
        self.glyphColor = {}
        
    def createColoredGlyphs(self, name, color):
        self.glyphColor[name] = color
        try:
            self.colored_glyphs[name] = {}
            for glyphset in self.glyphs:
                self.colored_glyphs[name][glyphset] = []
                for glyph in self.glyphs[glyphset]:
                    colored_glyph = glyph.copy()
                    painter = QtGui.QPainter()
                    if painter.begin(colored_glyph):
                        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Multiply)
                        painter.fillRect(colored_glyph.rect(), color)
                        self.colored_glyphs[name][glyphset].append(colored_glyph)
                        painter.end()
                    # end if
                # end for
            # end for
        except:
            pass
        
    def loadGlyphPixmaps(self, path):
        glyphset_dict = {}
        pixmap = QtGui.QPixmap(path)
        ncells = pixmap.width() // self.cell_width
        nsets  = pixmap.height() // self.cell_height
        #== We ultimately create QImages so we can use the Multiply blending mode in createColoredGlyphs()
        for y in range(nsets):
            glyphset = [ pixmap.copy(QtCore.QRect(x * self.cell_width, y * self.cell_height, self.cell_width, self.cell_height)).toImage() for x in range(ncells) ]
            glyphset_dict[GLYPHSET_KEYS[y]] = glyphset
            # end for
        # end for
        return glyphset_dict
        
#-- end class FontGlyphs

class GlassTTY(QtGui.QWidget):

    breakSignal = QtCore.Signal()
    xmitChars = QtCore.Signal(str)
    
    NCHARS = N_HORZ_CHARS
    NLINES = N_VERT_LINES
    
    CURSOR_BLOCK = 0
    CURSOR_LINE  = 5
    
    ABSOLUTE_ORIGIN = 0
    RELATIVE_ORIGIN = 1
    
    n_blinkers = 0
    @classmethod
    def add_blinkers(cls, chars):
        n = len(filter(lambda (c, a): a & BLI, chars))
        cls.n_blinkers += n
    @classmethod
    def deduct_blinkers(cls, chars):
        n = len(filter(lambda (c, a): a & BLI, chars))
        cls.n_blinkers -= n
    
    class RasterLine(list):
        NULL = ( chr(0), 0 )
        def __init__(self, n):
            super(GlassTTY.RasterLine, self).__init__()
            self.extend([ self.NULL for i in range(n) ])
        def pop(self, index):
            line = super(GlassTTY.RasterLine, self).pop(index)
            GlassTTY.deduct_blinkers(line)
            return line
        def cleared(self):
            GlassTTY.deduct_blinkers(self)
            for i in range(len(self)):
                self[i] = self.NULL
            return self
        def clear(self, start=0, end=-1):
            if end == -1:
                end = len(self)
            if end < start:
                start, end = end, start
            GlassTTY.deduct_blinkers(self[start:end])
            self[start:end] = [ self.NULL for i in range(end - start) ]
    #-- end class RasterLine
    
    def __init__(self, phosphor_color=DEFAULT_PHOSPHOR_COLOR, charset=DEFAULT_CHARSET, parent=None):
        super(GlassTTY, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        
        self.opacity = DEFAULT_BRIGHTNESS
        
        self.glyphsets = {
            'std': FontGlyphs(":/UiCrt2_StdCharset_Rom.png"),
            'alt': FontGlyphs(":/UiCrt2_AltCharset_Rom.png"),
        }
        for phosphor_color_name, color in PHOSPHOR_COLORS.items():
            self.glyphsets['std'].createColoredGlyphs(phosphor_color_name, color)
            self.glyphsets['alt'].createColoredGlyphs(phosphor_color_name, color)
        # end for
        self.charset = charset
        
        self.raster_image = QtGui.QImage(self.NCHARS * self.cell_width, self.NLINES * self.cell_height, QtGui.QImage.Format_RGB32)
        self.raster_lines = [ GlassTTY.RasterLine(self.NCHARS) for i in range(self.NLINES) ]
        self.charattrs = 0
        self.blink_state = True
        
        self.origin_mode = self.ABSOLUTE_ORIGIN
        self.tab_stops = []
        
        self.cursorx = 0
        self.cursory = 0
        self.cursor_blink = True
        self.cursor_visible = True
        self.cursor_glyph = self.CURSOR_BLOCK
        
        self.arrowkey_mode = DEFAULT_ARROWKEY_MODE
        self.autowrap = DEFAULT_WRAP_MODE
        self.autorepeat = DEFAULT_REPEAT_MODE
        self.screen_mode = DEFAULT_SCREEN_MODE
        self.newline_mode = DEFAULT_NEWLINE_MODE
        
        self.lfecho = DEFAULT_LFECHO_MODE
        self.crecho = DEFAULT_CRECHO_MODE
        self.localecho = DEFAULT_LOCALECHO_MODE
        self.esc_code_state = 0
        
        self.status_bar_rect = QtCore.QRect(0, self.NLINES * self.cell_height + 2, self.NCHARS * self.cell_width, self.cell_height)
        
        self.setPhosphorColor(phosphor_color)
        self.resetScrollRange()
        
        self.setConnected(False)
        self.startTimer(500)
        self.clock_minute_now = QtCore.QTime.currentTime().minute()
    
    @property
    def font(self):
        return self.glyphsets[self.charset]
        
    @property
    def cell_width(self):
        return self.font.cell_width
        
    @property
    def cell_height(self):
        return self.font.cell_height
        
    def sizeHint(self):
        #== We are a fixed-size widget containing (NCHARS x NLINES) monospaced character cells
        #== and a small border margin
        w = self.cell_width * self.NCHARS
        h = self.cell_height * (self.NLINES + 1)
        return QtCore.QSize(w, h)
        
    def setConnected(self, flag):
        self.connected = flag
        self.cursor_visible = flag
        self.repaint_cursor()
        self.update(self.status_bar_rect)
        
    def setEchoMode(self, *args):
        try:
            mode, flag = args
            setattr(self, mode, flag)
            self.update(self.status_bar_rect)
        except:
            pass
        
    def setPhosphorColor(self, phosphor_color):
        self.phosphor_color = phosphor_color
        self.fontcolor = PHOSPHOR_COLORS[phosphor_color]
        self.wincolor = self.fontcolor.darker(1500)
        self.glyphs = self.font.colored_glyphs[phosphor_color]
        
        if self.screen_mode:
            self.compmode = QtGui.QPainter.CompositionMode_Darken
        else:
            self.compmode = QtGui.QPainter.CompositionMode_Lighten
        # end if
        
        painter = QtGui.QPainter()
        if painter.begin(self.raster_image):
            self.paint_background(painter, self.raster_image.rect())
            painter.end()
            
        self.repaint_all()
    
    def setCharSet(self, charset):
        self.charset = charset
        self.glyphs = self.font.colored_glyphs[self.phosphor_color]
        # self.repaint_all()
        self.update()
        
    def setBrightness(self, value):
        self.opacity = value
        self.update()
        
    def sendCharacters(self, text):
        self.xmitChars.emit(text)
        
    #==================================#
    #== HIGH-LEVEL RASTER MANAGEMENT ==#
    #==================================#
    
    def addCharacters(self, text):
        """
        Add a string of characters, one at a time, to the display raster matrix.
        """
        self.hideCursor()
        for c in text:
            #== Process control characters
            if c not in [ESC, CAN, SUB] and 0 <= ord(c) < 32:
                self.process_ctl_char(c)
                continue
                
            #== Process escape code sequence
            elif c in [ESC, CAN, SUB] or self.esc_code_state:
                if self.process_esc_code(c):
                    continue
                    
            #== All other characters ('graphical characters')
            GlassTTY.add_blinkers([(c, self.charattrs)])
            self.raster_lines[self.cursory][self.cursorx] = (c, self.charattrs)
            self.repaint_cell(self.cursory, self.cursorx)
            
            #== Advance to next position
            if self.cursorx + 1 == self.NCHARS:
                if self.autowrap:
                    #== Wrap around
                    self.cursorx = 0
                    if self.moveCursor(0, +1, redraw_immediately=False):
                        #== Scroll display if necessary
                        self.scrollUp()
                    # end if
                # end if
            else:
                self.cursorx += 1
            # end if
        # end for
        self.showCursor()
        
    # def delCharacters(self, nchars_to_delete):
        # """
        # Delete the last nchars_to_delete characters from the display raster matrix,
        # relative to the current raster 'cursor' position.
        # """
        # prevx = self.cursorx - nchars_to_delete
        # if prevx >= 0:
            # self.raster_lines[self.cursory].clear(prevx, self.cursorx)
            # self.cursorx = prevx
        # # end if
        # self.repaint_line(self.cursory)

    def process_ctl_char(self, c):
        needs_scrolling = False
        
        if c == NUL:
            pass
            
        elif c == CR:
            self.cursorx = 0
            if self.lfecho:
                needs_scrolling = self.moveCursor(0, +1, redraw_immediately=False)
                
        elif c == LF:
            if self.crecho or self.newline_mode:
                self.cursorx = 0
            needs_scrolling = self.moveCursor(0, +1, redraw_immediately=False)
            
        elif c == BS:
            self.cursorx = max(0, self.cursorx - 1)
            
        elif c == TAB:
            self.cursorx = self.nextTabStopX()
            
        elif c == BEL:
            self.ring_bell()
            
        else:
            print "Received unexpected control character: ^%s %r (%d) \\%03o" % (chr(ord(c)+64), c, ord(c), ord(c))
            
        #== Scroll display if necessary
        if needs_scrolling:
            self.scrollUp()
    
    def valid_row_coord(self, n):
        return 0 <= n < self.NLINES
        
    def valid_col_coord(self, n):
        return 0 <= n < self.NCHARS
        
    def resetScrollRange(self, first=0, last=NLINES-1):
        if last > first < self.NLINES - 2:
            self.scroll_first = first
            self.scroll_last = max(first + 2, last)
        
    def scrollUp(self, n_lines=1):
        for i in range(n_lines):
            line = self.raster_lines.pop(self.scroll_first)
            self.raster_lines.insert(self.scroll_last, line.cleared())
        # end for
        rect = QtCore.QRect(0, self.scroll_first * self.cell_height, self.NCHARS * self.cell_width, (self.scroll_last + 1) * self.cell_height)
        self.repaint_all(rect)
        
    def scrollDown(self, n_lines=1):
        for i in range(n_lines):
            line = self.raster_lines.pop(self.scroll_last)
            self.raster_lines.insert(self.scroll_first, line.cleared())
        # end for
        rect = QtCore.QRect(0, self.scroll_first * self.cell_height, self.NCHARS * self.cell_width, (self.scroll_last + 1) * self.cell_height)
        self.repaint_all(rect)
        
    def eraseEndOfLine(self):
        self.raster_lines[self.cursory].clear(self.cursorx)
        self.repaint_line(self.cursory, self.cursorx)
        
    def eraseStartOfLine(self):
        self.raster_lines[self.cursory].clear(0, self.cursorx + 1)
        self.repaint_line(self.cursory)
        
    def eraseLine(self):
        self.raster_lines[self.cursory].clear()
        self.repaint_line(self.cursory)
        
    def eraseDown(self):
        for line in self.raster_lines[self.cursory:]:
            line.clear()
        # end for
        erase_rect = QtCore.QRect(0, self.cursory * self.cell_height, self.NCHARS * self.cell_width, (self.NLINES - self.cursory) * self.cell_height)
        self.repaint_all(erase_rect)
        
    def eraseUp(self):
        for line in self.raster_lines[0:self.cursory + 1]:
            line.clear()
        # end for
        erase_rect = QtCore.QRect(0, 0, self.NCHARS * self.cell_width, self.cursory * self.cell_height)
        self.repaint_all(erase_rect)
        
    def eraseScreen(self):
        for line in self.raster_lines:
            line.clear()
        # end for
        self.homeCursor()
        self.repaint_all()
    
    #==================================#
    #==      TAB STOP MANAGEMENT     ==#
    #==================================#
    
    def clearAllTabStops(self):
        self.tab_stops = []
        
    def clearTabStop(self, at=None):
        if at is None:
            at = self.cursorx
            
        if at in self.tab_stops:
            self.tab_stops.remove(at)
        
    def setTabStop(self, at=None):
        if at is None:
            at = self.cursorx
            
        if at not in self.tab_stops:
            self.tab_stops.append(at)
            self.tab_stops.sort()
        
    def nextTabStopX(self, at=None):
        if at is None:
            at = self.cursorx
            
        return ([ stopx for stopx in self.tab_stops if stopx > at ] or [at])[0]
    
    #==================================#
    #==       CURSOR MANAGEMENT      ==#
    #==================================#
    
    def cursorPos(self):
        x = self.cursorx * self.cell_width
        y = self.cursory * self.cell_height
        return QtCore.QPoint(x, y)
        
    def cursorRect(self):
        return QtCore.QRect(self.cursorPos(), QtCore.QSize(self.cell_width, self.cell_height))
    
    def setCursorStyle(self, style):
        self.cursor_glyph = style
        
    def setCursorBlink(self, blink):
        self.cursor_blink = blink
        if self.connected:
            self.showCursor()
        
    def showCursor(self):
        self.cursor_visible = True
        self.repaint_cursor()
        
    def hideCursor(self):
        self.cursor_visible = False
        self.repaint_cursor()
        
    def toggleCursor(self):
        self.cursor_visible = self.blink_state
        self.repaint_cursor()
        
    def saveCursor(self):
        self.saved_cursorx = self.cursorx
        self.saved_cursory = self.cursory
        self.saved_charattrs = self.charattrs
        
    def restoreCursor(self):
        try:
            self.cursorx = self.saved_cursorx
            self.cursory = self.saved_cursory
            self.charattrs = self.charattrs
        except:
            pass # ignore request if saveCursor() was never called
        
    def moveCursor(self, dx, dy, redraw_immediately=True):
        if redraw_immediately and self.cursor_visible:
            #== Erase from old position
            self.cursor_visible = False
            self.repaint_cursor()
            self.cursor_visible = True
            
        #== Draw in new position
        needs_scrolling = (self.cursory + dy < self.scroll_first) or (self.cursory + dy > self.scroll_last)
        self.cursorx = min(self.NCHARS - 1, max(0, self.cursorx + dx))
        self.cursory = min(self.scroll_last, max(self.scroll_first, self.cursory + dy))
        
        if redraw_immediately:
            self.repaint_cursor()
        # end if
        
        return needs_scrolling
        
    def moveCursorTo(self, x, y, redraw_immediately=True):
        _debug(" -> %d, %d" % (y, x))
        if redraw_immediately and self.cursor_visible:
            #== Erase from old position
            self.cursor_visible = False
            self.repaint_cursor()
            self.cursor_visible = True
            
        #== Draw in new position
        if self.origin_mode == self.ABSOLUTE_ORIGIN:
            self.cursorx = min(self.NCHARS - 1, max(0, x))
            self.cursory = min(self.NLINES - 1, max(0, y))
            needs_scrolling = (y < 0) or (y > self.NLINES - 1)
            
        elif self.origin_mode == self.RELATIVE_ORIGIN:
            self.cursorx = min(self.NCHARS - 1, max(0, x))
            self.cursory = min(self.scroll_last, max(self.scroll_first, self.scroll_first + y))
            needs_scrolling = (y < self.scroll_first) or (y > self.scroll_last)
        # end if
        
        if redraw_immediately:
            self.repaint_cursor()
        # end if
        
        return needs_scrolling
        
    def homeCursor(self, redraw_immediately=True):
        self.moveCursorTo(0, 0, redraw_immediately)
    
    #=================================#
    #==  ESCAPE CODE STATE MACHINE  ==#
    #=================================#
    
    def process_esc_code(self, c):
        #== State machine for processing VT100 escape codes. Returns True
        #== whenever c is a character recognized as the next one in the
        #== escape sequence being processed. This tells the caller not to
        #== do anything with that character since it has been consumed
        #== by this state machine. Returns False if c does not fit
        #== anywhere in the current sequence, typically aborting the
        #== sequence and informing the caller to process the character
        #== normally.
        
        (
         CC_BEGIN,
         CC_TYPE1,
         CC_SETDEC,
         CC_NUM1,
         CC_NUMLIST,
        ) = range(1, 6)
        
        def start():
            self.esc_code_state = CC_BEGIN
            _debug("^[")
            return True
        def next(state):
            self.esc_code_state = state
            return True
        def same():
            #== Don't change state
            return True
        def done():
            self.esc_code_state = 0
            _debug("\n")
            return True
        def failed():
            self.esc_code_state = 0
            _debug("\n")
            return False
            
        def defaultTo1(s):
            return int(s) or 1
        
        if self.esc_code_state == 0:
            if c in [CAN, SUB]:
                return done()
            assert c == ESC
            return start()
            
        elif self.esc_code_state == CC_BEGIN:
            _debug(c)
            self._cc_n1 = ""
            if c == '[':
                return next(CC_TYPE1)
            elif c == '<':
                #== Ignore request to enter/exit VT52/ANSI mode
                _debug("\nIgnoring 'Enter VT100 Mode' request (already in VT100 Mode)")
                return done()
            elif c == '7':
                self.saveCursor()
                return done()
            elif c == '8':
                self.restoreCursor()
                return done()
            elif c == 'D':
                if self.moveCursor(0, +1):
                    self.scrollUp()
                return done()
            elif c == 'E':
                # CR/LF and scroll up if necessary
                if self.moveCursorTo(0, self.cursory + 1):
                    self.scrollUp()
                return done()
            elif c == 'M':
                if self.moveCursor(0, -1):
                    self.scrollDown()
                return done()
            elif c == 'H':
                self.setTabStop()
                return done()
            # end if
            
        elif self.esc_code_state == CC_TYPE1:
            _debug(c)
            if c.isdigit():
                self._cc_n1 = c
                return next(CC_NUM1)
            elif c == ';':
                self._cc_nl = ["0", "0"]
                return next(CC_NUMLIST)
            elif c == '?':
                return next(CC_SETDEC)
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
                #== Respond with device code
                self.send_esc_code_response("[?1;0c")
                return done()
            elif c == 'D':
                self.moveCursor(-1, 0)
                return done()
            elif c == 'g':
                self.clearTabStop()
                return done()
            elif c == 'H' or c == 'f':
                self.homeCursor()
                return done()
            elif c == 'J':
                self.eraseDown()
                return done()
            elif c == 'K':
                self.eraseEndOfLine()
                return done()
            elif c == 'r':
                self.resetScrollRange()
                # self.homeCursor()
                return done()
            # end if
            
        elif self.esc_code_state == CC_SETDEC:
            _debug(c)
            if c.isdigit():
                self._cc_n1 = c
                return same()
            #== SM (Set Mode)
            elif c == 'h' and self._cc_n1:
                code = int(self._cc_n1)
                if code == 1:
                    self.arrowkey_mode = True
                elif code == 5:
                    self.screen_mode = True
                    self.compmode = QtGui.QPainter.CompositionMode_Darken
                    self.update()
                elif code == 6:
                    self.origin_mode = self.RELATIVE_ORIGIN
                    self.homeCursor()
                elif code == 7:
                    self.autowrap = True
                elif code == 8:
                    self.autorepeat = True
                else:
                    _debug("\nIgnoring DEC private '%dh'" % (code))
                # end if
                return done()
            #== RM (Reset Mode)
            elif c == 'l' and self._cc_n1:
                code = int(self._cc_n1)
                if code == 1:
                    self.arrowkey_mode = False
                elif code == 5:
                    self.screen_mode = False
                    self.compmode = QtGui.QPainter.CompositionMode_Lighten
                    self.update()
                elif code == 6:
                    self.origin_mode = self.ABSOLUTE_ORIGIN
                    self.homeCursor()
                elif code == 7:
                    self.autowrap = False
                elif code == 8:
                    self.autorepeat = False
                else:
                    _debug("\nIgnoring DEC private '%dl'" % (code))
                # end if
                return done()
            # end if
            
        elif self.esc_code_state == CC_NUM1:
            _debug(c)
            if c.isdigit():
                self._cc_n1 += c
                return same()
            elif c == ';':
                self._cc_nl = [self._cc_n1, "0"]
                return next(CC_NUMLIST)
            elif c == 'c' and self._cc_n1 == '0':
                #== Respond with device code
                self.send_esc_code_response("[?1;0c")
                return done()
            elif c == 'g':
                code = int(self._cc_n1)
                if code == 0:
                    self.clearTabStop()
                    return done()
                elif code == 3:
                    self.clearAllTabStops()
                    return done()
                # end if
            elif c == 'h': # Set a mode
                n = int(self._cc_n1)
                if n == 20:
                    self.newline_mode = True
                    return done()
                # end if
            elif c == 'l': # Reset a mode
                n = int(self._cc_n1)
                if n == 20:
                    self.newline_mode = False
                    return done()
                # end if
            elif c == 'm':
                n = int(self._cc_n1)
                if n == 0:
                    charattrs = 0
                elif n in [1,2,4,5,7,8]:
                    charattrs = self.charattrs | (2 ** (n - 1))
                else:
                    return failed()
                try:
                    glyphset = self.glyphs[charattrs & ~BLI]
                    self.charattrs = charattrs
                except:
                    print "No glyphset for attributes", charattrs
                    pass
                return done()
            elif c == 'n':
                code = int(self._cc_n1)
                if code == 5:
                    #== Respond with device status ok
                    self.send_esc_code_response("[0n")
                    return done()
                elif code == 6:
                    #== Respond with cursor position
                    self.send_esc_code_response("[%d;%dR"%(self.cursory + 1, self.cursorx + 1))
                    return done()
                #end if
            elif c == 'A':
                count = defaultTo1(self._cc_n1)
                self.moveCursor(0, -count)
                return done()
            elif c == 'B':
                count = defaultTo1(self._cc_n1)
                self.moveCursor(0, count)
                return done()
            elif c == 'C':
                count = defaultTo1(self._cc_n1)
                self.moveCursor(count, 0)
                return done()
            elif c == 'D':
                count = defaultTo1(self._cc_n1)
                self.moveCursor(-count, 0)
                return done()
            elif c == 'H' or c == 'f':
                row = defaultTo1(self._cc_n1) - 1
                if self.valid_row_coord(row):
                    self.moveCursorTo(0, row)
                    return done()
                else:
                    print "^[[%d;%dH (invalid position)" % (row, 0)
            elif c == 'J':
                code = int(self._cc_n1)
                if code == 0:
                    self.eraseDown()
                    return done()
                elif code == 1:
                    self.eraseUp()
                    return done()
                elif code == 2:
                    self.eraseScreen()
                    return done()
                # end if
            elif c == 'K':
                code = int(self._cc_n1)
                if code == 0:
                    self.eraseEndOfLine()
                    return done()
                elif code == 1:
                    self.eraseStartOfLine()
                    return done()
                elif code == 2:
                    self.eraseLine()
                    return done()
                # end if
            # end if
            
        elif self.esc_code_state == CC_NUMLIST:
            _debug(c)
            if c.isdigit():
                self._cc_nl[-1] += c
                return same()
            elif c == ';':
                self._cc_nl.append("0")
                return same()
            else:
                if (c == 'H' or c == 'f') and len(self._cc_nl) == 2:
                    nums = map(defaultTo1, self._cc_nl)
                    row, col = nums
                    row -= 1 ; col -= 1
                    if self.valid_row_coord(row) and self.valid_col_coord(col):
                        self.moveCursorTo(col, row)
                        return done()
                    else:
                        print "^[[%d;%dH (invalid position)" % (row, col)
                elif c == 'r' and len(self._cc_nl) == 2:
                    nums = map(defaultTo1, self._cc_nl)
                    start, end = nums
                    start -= 1 ; end -= 1
                    if self.valid_row_coord(start) and self.valid_row_coord(end):
                        self.resetScrollRange(start, end)
                        self.homeCursor()
                        return done()
                    else:
                        print "^[[%d;%dr (invalid range)" % (row, col)
                elif c == 'm':
                    nums = map(int, self._cc_nl)
                    nums = set(nums)
                    #== Dim(1) + Bright(2) cancel each other out
                    if set([1,2]) <= nums:
                        nums -= set([1,2])
                    charattrs = self.charattrs
                    for n in nums:
                        if n == 0:
                            #== Reset all attribute bits
                            charattrs = 0
                        elif n in [1,2,4,5,7] and (charattrs & HID == 0):
                            #== All others set the corresponding attribute bit
                            charattrs |= 2 ** (n - 1)
                        elif n == 8:
                            #== Hidden attribute overrides all others
                            charattrs = HID
                        else:
                            return failed()
                    try:
                        glyphset = self.glyphs[charattrs & ~BLI]
                        self.charattrs = charattrs
                    except:
                        print "No glyphset for attributes", charattrs
                        pass
                    return done()
                # end if
                
        # end if
        
        #== Special case: failed the code parse on new ESC char;
        #== just begin control code parsing again from the start
        if c == ESC:
            return start()
        #== Special case: abort code sequence in progress when
        #== CAN (ctrl-X) or SUB (ctrl-Z) is encountered
        elif c in [CAN, SUB]:
            return done()
            
        #== Otherwise stop parsing and process new char normally
        return failed()
        
    def send_esc_code_response(self, code):
        self.sendCharacters(ESC + code)
        
    #===============================#
    #==     QT EVENT HANDLERS     ==#
    #===============================#
    
    def keyPressEvent(self, event):
        special = {'2':NULL_CHAR_CODE, '@':NULL_CHAR_CODE, '6':chr(30), '-':chr(31)}
        
        #== Ignore auto-repeated keystrokes if auto-repeat mode is off
        if event.isAutoRepeat() and not self.autorepeat:
            event.ignore()
            return
            
        #== KEYPAD 'ENTER' KEY ==#
        if event.key() == QtCore.Qt.Key_Enter: # Linefeed key
            # print "Send LINEFEED"
            if self.newline_mode:
                self.sendCharacters(CR + LF)
            else:
                self.sendCharacters(LF)
            return
            
        #== NON-ASCII KEYSTROKE ==#
        if not event.text():
            if event.key() == QtCore.Qt.Key_Pause: # Break key
                # print "Send BREAK"
                self.breakSignal.emit()
                
            elif event.key() == QtCore.Qt.Key_Up:
                self.send_esc_code_response("OA" if self.arrowkey_mode else "A")
            elif event.key() == QtCore.Qt.Key_Down:
                self.send_esc_code_response("OB" if self.arrowkey_mode else "B")
            elif event.key() == QtCore.Qt.Key_Right:
                self.send_esc_code_response("OC" if self.arrowkey_mode else "C")
            elif event.key() == QtCore.Qt.Key_Left:
                self.send_esc_code_response("OD" if self.arrowkey_mode else "D")
                
        #== ASCII KEYSTROKE ==#
        for c in str(event.text()):
            if c == BEL:
                self.ring_bell()
                
            elif c == LF and self.newline_mode:
                c = CR + LF
                
            #== Turn Alt+key into ESC+char
            if event.modifiers() & QtCore.Qt.AltModifier:
                self.sendCharacters(ESC + c)
                
            elif event.modifiers() & QtCore.Qt.ControlModifier and (c in special):
                self.sendCharacters(special[c])
                
            else:
                if self.localecho:
                    self.addCharacters(c)
                # print "Send char: %r (%d)" % (c, ord(c))
                self.sendCharacters(c)
            
    def timerEvent(self, event):
        if self.clock_minute_now != QtCore.QTime.currentTime().minute():
            self.clock_minute_now = QtCore.QTime.currentTime().minute()
            self.update(self.status_bar_rect)
            
        self.blink_state = not self.blink_state
        if GlassTTY.n_blinkers > 0:
            #== Only trigger a full-screen update if there are blinking characters
            #== that need to be toggled on/off.
            self.repaint_all()
        
        if not self.connected:
            self.hideCursor()
            
        elif self.cursor_blink:
            self.toggleCursor()
        
    def paintEvent(self, event):
        #== Blit the painted image to the widget
        painter = QtGui.QPainter()
        if painter.begin(self):
            painter.setOpacity(self.opacity) # <-- this is how phosphor brightness is implemented
            painter.drawImage(event.rect(), self.raster_image, event.rect())
            
            if True:
                self.paint_status_bar(painter)
            
            painter.end()
        
    def paint_background(self, painter, rect):
        if self.screen_mode:
            opacity = 0.66
            color = self.fontcolor
        else:
            opacity = 1.0
            color = self.wincolor
        # end if
        
        painter.save()
        painter.fillRect(rect, QtCore.Qt.black)
        painter.setOpacity(opacity)
        painter.fillRect(rect, color)
        painter.restore()
        
        painter.setCompositionMode(self.compmode)
        
    def paint_status_bar(self, painter):
        painter.save()
        
        painter.fillRect(self.status_bar_rect, self.wincolor)
        
        status_list = [
            ("ONLINE"     if self.connected else "OFFLINE",   9),
            ("",                                              10),
            ("WRAP"       if self.autowrap else "",           6),
            ("CR ECHO"    if self.crecho else "",             9),
            ("LF ECHO"    if self.lfecho else "",             9),
            ("LOCAL ECHO" if self.localecho else "",          12),
            ("REPEAT"     if self.autorepeat else "",         8),
            ("",                                              7),
            (QtCore.QTime.currentTime().toString("hh:mm AP"), 10),
        ]
        status_text = ("").join([" %-*s" % (w - 1, s) for (s, w) in status_list])
        
        cell_rect = self.status_bar_rect.adjusted(1, 1, 0, 0)
        for c in status_text:
            painter.drawImage(cell_rect.topLeft(), self.glyphs[NRM|REV][ord(c)])
            cell_rect.translate(self.cell_width, 0)
        # end for
        
        box_rect = self.status_bar_rect.adjusted(0, 0, 0, 0)
        painter.setPen(self.wincolor)
        for (_, w) in status_list:
            box_rect.setWidth(self.cell_width * w)
            painter.drawRect(box_rect)
            box_rect.translate(self.cell_width * w, 0)
        # end for
        
        painter.restore()
    
    def repaint_cursor(self):
        def drawit(attr):
            return (attr & BLI) == 0 or self.blink_state
            
        cursor_rect = self.cursorRect()
        
        painter = QtGui.QPainter()
        if painter.begin(self.raster_image):
            # painter.fillRect(cursor_rect, self.wincolor)
            # painter.setCompositionMode(self.compmode)
            self.paint_background(painter, cursor_rect)
            
            c, attr = self.raster_lines[self.cursory][self.cursorx]
            if drawit(attr):
                char_under_cursor = ord(c) or ord(SP)
                painter.drawImage(cursor_rect.topLeft(), self.glyphs[self._glyph_index(attr)][char_under_cursor])
                
            if self.cursor_visible:
                if self.cursor_glyph == self.CURSOR_BLOCK:
                    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Difference)
                    painter.fillRect(cursor_rect.adjusted(0, 0, 0, 0), self.fontcolor)
                else:
                    painter.fillRect(cursor_rect.adjusted(0, self.cell_height-3, 0, 0), self.fontcolor)
                # end if
            # end if
            
            painter.end()
            
            self.update(cursor_rect)
            
    def repaint_cell(self, celly, cellx):
        def drawit(c, attr):
            return ord(c) and ((attr & BLI) == 0 or self.blink_state)
            
        cell_rect = QtCore.QRect(cellx * self.cell_width, celly * self.cell_height, self.cell_width, self.cell_height)
        
        painter = QtGui.QPainter()
        if painter.begin(self.raster_image):
            # painter.fillRect(cell_rect, self.wincolor)
            # painter.setCompositionMode(self.compmode)
            self.paint_background(painter, cell_rect)
            
            c, attr = self.raster_lines[celly][cellx]
            if drawit(c, attr):
                try:
                    painter.drawImage(cell_rect.topLeft(), self.glyphs[self._glyph_index(attr)][ord(c)])
                except:
                    print "Bad character code for display:", repr(c), ord(c)
                # end try
            # end if
            
            painter.end()
            
            self.update(cell_rect)
        
    def repaint_line(self, liney, cellx=0):
        def drawit(c, attr):
            return ord(c) and ((attr & BLI) == 0 or self.blink_state)
            
        line_rect = QtCore.QRect(cellx * self.cell_width, liney * self.cell_height, self.NCHARS * self.cell_width, self.cell_height)
        cell_rect = QtCore.QRect(cellx * self.cell_width, liney * self.cell_height, self.cell_width, self.cell_height)
        
        painter = QtGui.QPainter()
        if painter.begin(self.raster_image):
            # painter.fillRect(line_rect, self.wincolor)
            # painter.setCompositionMode(self.compmode)
            self.paint_background(painter, line_rect)
            
            for c, attr in self.raster_lines[liney][cellx:]:
                if drawit(c, attr):
                    try:
                        painter.drawImage(cell_rect.topLeft(), self.glyphs[self._glyph_index(attr)][ord(c)])
                    except:
                        print "Bad character code for display:", repr(c), ord(c)
                    # end try
                # end if
                cell_rect.translate(self.cell_width, 0)
            # end for
            
            painter.end()
            
            self.update(line_rect)
    
    def repaint_all(self, rect=None):
        def drawit(attr):
            return (attr & BLI) == 0 or self.blink_state
            
        screen_rect = rect or self.raster_image.rect()
        
        #== We paint on this QImage object instead of directly on the widget. Doing so gives us
        #== full access to all the Qt composition/blending modes.
        painter = QtGui.QPainter()
        if painter.begin(self.raster_image):
            # painter.fillRect(screen_rect, self.wincolor)
            # painter.setCompositionMode(self.compmode)
            self.paint_background(painter, screen_rect)
            
            #== Draw the character under the cursor if we are only drawing the cursor in this paint event
            c, attr = self.raster_lines[self.cursory][self.cursorx]
            if screen_rect == self.cursorRect() and drawit(attr):
                print "*** CURSOR ONLY ***"
                char_under_cursor = ord(c) or ord(SP)
                painter.drawImage(self.cursorRect().topLeft(), self.glyphs[self._glyph_index(attr)][char_under_cursor])
                
            #== If we aren't just repainting the cursor, then redraw all the characters on the screen
            else:
                cell_rect = QtCore.QRect(0, 0, self.cell_width, self.cell_height)
                for line in self.raster_lines:
                    for c, attr in line:
                        if ord(c) and drawit(attr):
                            try:
                                painter.drawImage(cell_rect.topLeft(), self.glyphs[self._glyph_index(attr)][ord(c)])
                            except:
                                print "Bad character code for display:", repr(c), ord(c)
                            # end try
                        # end if
                        cell_rect.translate(self.cell_width, 0)
                    # end for
                    cell_rect.setLeft(0) ; cell_rect.translate(0, self.cell_height)
                # end for
            # end if
            
            if self.cursor_visible:
                if self.cursor_glyph == self.CURSOR_BLOCK:
                    painter.setCompositionMode(QtGui.QPainter.CompositionMode_Difference)
                    painter.fillRect(self.cursorRect().adjusted(0, 0, 0, 0), self.fontcolor)
                else:
                    painter.fillRect(self.cursorRect().adjusted(0, self.cell_height-3, 0, 0), self.fontcolor)
                # end if
            # end if
            
            painter.end()
            
            self.update(screen_rect)
    
    def _glyph_index(self, attr):
        if self.screen_mode:
            return REVERSE_VIDEO_ATTRS[attr & ~BLI]
        else:
            return attr & ~BLI
    
    # def shift_raster_image(self, n):
        # if n == 0:
            # return
            
        # bounds_width = self.NCHARS * self.cell_width
        # origin_height = (self.NLINES - abs(n)) * self.cell_height
        # target_height = abs(n) * self.cell_height
        
        # painter = QtGui.QPainter()
        # if painter.begin(self.raster_image):
            # if n < 0:
                # n = 0 - n
                # origin = QtCore.QRect(0, target_height, bounds_width, origin_height)
                # eraser = QtCore.QRect(0, origin_height, bounds_width, target_height)
                # target = origin.translated(0, -target_height)
            # else:
                # origin = QtCore.QRect(0, 0, bounds_width, origin_height)
                # eraser = QtCore.QRect(0, 0, bounds_width, target_height)
                # target = origin.translated(0, target_height)
            # # end if
            
            # painter.drawImage(target, self.raster_image, origin)
            # painter.fillRect(eraser, self.wincolor)
            
            # self.update(self.raster_image.rect())
    
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
        painter = QtGui.QPainter()
        
        canvas = self.image.copy()
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
    
    connected = QtCore.Signal()
    disconnected = QtCore.Signal()
    error = QtCore.Signal(int)
    
    def __init__(self, phosphor_color, charset, parent=None):
        super(TerminalIO, self).__init__(parent)
        self.ME = self.__class__.__name__
        
        self.name = QtNetwork.QHostInfo.localHostName()
        self.host = DEFAULT_SERVER_NAME
        self.port = DEFAULT_SERVER_PORT
        self.protocol = DEFAULT_PROTOCOL
        
        # if self.protocol == "pymultics":
            # self.socket = QtNetwork.QTcpSocket(self)
            
        # elif self.protocol == "telnet":
            # self.socket = QTelnetSocket.QTelnetSocket(self)
            # self.parent().closed.connect(self.socket._thread.stop)
            
        # self.socket.error.connect(self.socket_error)
        # self.socket.hostFound.connect(self.host_found)
        # self.socket.connected.connect(self.connection_made)
        # self.socket.disconnected.connect(self.connection_lost)
        # self.socket.readyRead.connect(self.data_available)
        # self.com_port = 0
        
        self.ttyio = GlassTTY(phosphor_color, charset)
        
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
        if self.protocol == "pymultics":
            self.socket = QtNetwork.QTcpSocket(self)
            
        elif self.protocol == "telnet":
            self.socket = QTelnetSocket.QTelnetSocket(self)
            self.parent().closed.connect(self.hard_exit)
            
        self.socket.error.connect(self.socket_error)
        self.socket.hostFound.connect(self.host_found)
        self.socket.connected.connect(self.connection_made)
        self.socket.disconnected.connect(self.connection_lost)
        self.socket.readyRead.connect(self.data_available)
        self.com_port = 0
        # self.host = "batmud.bat.org"
        # self.port = 23
        # self.host = "73.221.10.251"
        # self.port = 6180
        self.socket.connectToHost(self.host, self.port)
        # pass
        
    @QtCore.Slot()
    def hard_exit(self):
        if self.socket and self.socket._thread.isRunning():
            self.socket._thread.stop()
            self.socket = None
    
    @QtCore.Slot(int)
    def socket_error(self, error):
        if error == QtNetwork.QAbstractSocket.SocketError.ConnectionRefusedError:
            self.setErrorStatus.emit("Host Server %s not Active" % (self.host))
        elif error != QtNetwork.QAbstractSocket.SocketError.RemoteHostClosedError:
            self.setErrorStatus.emit(self.socket.errorString())
            print self.ME, "socket_error:", error
        self.error.emit(error)
        
    @QtCore.Slot()
    def host_found(self):
        self.setNormalStatus.emit("Waiting for Host Server %s" % (self.host))
        
    @QtCore.Slot()
    def connection_made(self):
        self.connected.emit()
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
        self.disconnected.emit()
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
        if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.socket.disconnectFromHost()
        
    @QtCore.Slot()
    def reconnect(self):
        # self.socket.connectToHost(self.host, self.port)
        self.startup()
        
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
        
    def send_text_file(self, path):
        with open(path) as f:
            for line in f:
                #self.send_chars(line.replace(LF, CR+LF))
                #QtCore.QThread.msleep(250)
                for c in line:
                    QtCore.QThread.msleep(100)
                    self.send_chars(c)
                #self.send_chars(CR + LF)
    
    def set_server_name(self, host):
        self.host = host
        
    def set_server_port(self, port):
        self.port = port
        
    def set_protocol(self, protocol):
        self.protocol = protocol
        
    def set_echo_mode(self, mode, flag):
        self.ttyio.setEchoMode(mode, flag)
        
    def set_phosphor_color(self, phosphor_color):
        self.ttyio.setPhosphorColor(phosphor_color)
        self.update()
        
    def set_brightness(self, brightness):
        self.ttyio.setBrightness(brightness)
        
    def set_cursor_style(self, style):
        self.ttyio.setCursorStyle(style)
        
    def set_cursor_blink(self, flag):
        self.ttyio.setCursorBlink(flag)
        
    def set_character_set(self, charset):
        self.ttyio.setCharSet(charset)
        
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

    MAX_RECENT_CONNECTIONS = 10
    
    transmitString = QtCore.Signal(str)
    shutdown = QtCore.Signal()
    closed = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(TerminalWindow, self).__init__(parent)
        
        self.settings = QtCore.QSettings("pymultics", "Multics.Terminal")
        self.recent_connections = ast.literal_eval(self.settings.value("recent_connections", "[]"))
        
        self.io = TerminalIO(DEFAULT_PHOSPHOR_COLOR, DEFAULT_CHARSET, self)
        self.io.setNormalStatus.connect(self.set_normal_status)
        self.io.setConnectStatus.connect(self.set_connect_status)
        self.io.setErrorStatus.connect(self.set_error_status)
        self.io.connected.connect(self.disable_reconnect)
        self.io.disconnected.connect(self.enable_reconnect)
        self.io.error.connect(self.enable_reconnect)
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
        self.menuBar().setNativeMenuBar(False)
        
        #== Create menus
        self.file_menu = self.menuBar().addMenu("File")
        self.file_menu.setStyleSheet(MENU_STYLE_SHEET)
        
        self.options_menu = self.menuBar().addMenu("Options")
        self.options_menu.setStyleSheet(MENU_STYLE_SHEET)
        
        self.connect_action = self.menuBar().addAction("Connect", self.do_connect)
        
        #== Create menu items
        self.send_file_action = self.file_menu.addAction("Send Text File...", self.send_text_file)
        self.file_menu.addSeparator()
        self.file_menu.addAction("Quit", self.close)
        
        self.phosphor_color_menu = self.options_menu.addMenu("Phosphor Color")
        self.brightness_action = self.options_menu.addAction("Brightness...", self.set_brightness)
        self.options_menu.addSeparator()
        self.cursor_style_menu = self.options_menu.addMenu("Cursor Style")
        self.cursor_blink_action = self.options_menu.addAction("Cursor Blink", self.set_cursor_blink)
        self.options_menu.addSeparator()
        self.charset_menu = self.options_menu.addMenu("Character Set")
        self.options_menu.addSeparator()
        self.mode_options_menu = self.options_menu.addMenu("Modes")
        self.options_menu.addSeparator()
        self.set_server_action = self.options_menu.addAction("Server Settings...", self.set_server_info)
        self.recent_connections_menu = self.options_menu.addMenu("Recent Connections")
        
        self.set_crecho_action = self.mode_options_menu.addAction("Add CRs To Incoming LFs", self.set_crecho_mode)
        self.set_lfecho_action = self.mode_options_menu.addAction("Add LFs To Incoming CRs", self.set_lfecho_mode)
        self.set_localecho_action = self.mode_options_menu.addAction("Local Echo Typed Characters", self.set_localecho_mode)
        
        self.set_crecho_action.setCheckable(True)
        self.set_lfecho_action.setCheckable(True)
        self.set_localecho_action.setCheckable(True)
        
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
        
        self.set_std_charset = self.charset_menu.addAction("Standard", lambda: self.set_character_set("std"))
        self.set_alt_charset = self.charset_menu.addAction("Alternate", lambda: self.set_character_set("alt"))
        
        self.charset_group = QtGui.QActionGroup(self)
        self.charset_group.addAction(self.set_std_charset)
        self.charset_group.addAction(self.set_alt_charset)
        
        self.set_std_charset.setCheckable(True)
        self.set_alt_charset.setCheckable(True)
        
        self.build_recent_connections_menu()
        
        self.set_crecho_action.setChecked(int(self.settings.value("crecho_mode", DEFAULT_CRECHO_MODE)))
        self.set_lfecho_action.setChecked(int(self.settings.value("lfecho_mode", DEFAULT_LFECHO_MODE)))
        self.set_localecho_action.setChecked(int(self.settings.value("localecho_mode", DEFAULT_LOCALECHO_MODE)))
        
        self.set_phosphor_vintg.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "vintage")
        self.set_phosphor_green.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "green")
        self.set_phosphor_amber.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "amber")
        self.set_phosphor_white.setChecked(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "white")
        
        self.set_cursor_block.setChecked(int(self.settings.value("cursor_style", GlassTTY.CURSOR_BLOCK)) == GlassTTY.CURSOR_BLOCK)
        self.set_cursor_line.setChecked(int(self.settings.value("cursor_style", GlassTTY.CURSOR_BLOCK)) == GlassTTY.CURSOR_LINE)
        
        self.cursor_blink_action.setChecked(int(self.settings.value("cursor_blink", DEFAULT_CURSOR_BLINK)))
        
        self.set_std_charset.setChecked(self.settings.value("character_set", DEFAULT_CHARSET) == "std")
        self.set_alt_charset.setChecked(self.settings.value("character_set", DEFAULT_CHARSET) == "alt")
        
        self.send_file_action.setEnabled(False)
        self.connect_action.setEnabled(True)
        self.set_connect_action_tooltip()
    
    def startup(self):
        self.setFixedSize(self.size())
        self.io.set_server_name(self.settings.value("host", DEFAULT_SERVER_NAME))
        self.io.set_server_port(int(self.settings.value("port", DEFAULT_SERVER_PORT)))
        self.io.set_protocol(self.settings.value("protocol", DEFAULT_PROTOCOL))
        self.io.set_echo_mode("crecho", bool(int(self.settings.value("crecho_mode", DEFAULT_CRECHO_MODE))))
        self.io.set_echo_mode("lfecho", bool(int(self.settings.value("lfecho_mode", DEFAULT_LFECHO_MODE))))
        self.io.set_echo_mode("localecho", bool(self.settings.value("localecho_mode", DEFAULT_LOCALECHO_MODE)))
        self.io.set_phosphor_color(self.settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR))
        self.io.set_brightness(float(self.settings.value("brightness", DEFAULT_BRIGHTNESS)))
        self.io.set_cursor_style(int(self.settings.value("cursor_style", GlassTTY.CURSOR_BLOCK)))
        self.io.set_cursor_blink(bool(int(self.settings.value("cursor_blink", DEFAULT_CURSOR_BLINK))))
        self.io.set_character_set(self.settings.value("character_set", DEFAULT_CHARSET))
        # self.io.startup()
        
    def set_connect_action_tooltip(self):
        self.connect_action.setToolTip("Connect to " + self.connection_label())
        
    def connection_label(self, host=None, port=None, protocol=None):
        host = host or self.settings.value("host", DEFAULT_SERVER_NAME)
        port = port or int(self.settings.value("port", DEFAULT_SERVER_PORT))
        protocol = protocol or self.settings.value("protocol", DEFAULT_PROTOCOL)
        return "%s: %s %d" % (protocol, host, port)
        
    def build_recent_connections_menu(self):
        self.recent_connections_menu.clear()
        self.recent_connections_actions = []
        for (host, port, protocol) in self.recent_connections:
            self.recent_connections_actions.append(self.recent_connections_menu.addAction(self.connection_label(host, port, protocol),
                                                                                          lambda host=host, port=port, protocol=protocol: self.connect_to_recent(host, port, protocol)))
        
    def update_recent_connections(self, host, port, protocol):
        connection = (host, port, protocol)
        #== Move the connection to the top of the MRU list
        if connection in self.recent_connections:
            self.recent_connections.remove(connection)
        if len(self.recent_connections) == self.MAX_RECENT_CONNECTIONS:
            self.recent_connections.pop()
        self.recent_connections.insert(0, connection)
        self.settings.setValue("recent_connections", str(self.recent_connections))
        
        self.build_recent_connections_menu()
        
    def do_connect(self):
        if self.connect_action.text() == "Connect":
            self.io.set_server_name(self.settings.value("host", DEFAULT_SERVER_NAME))
            self.io.set_server_port(int(self.settings.value("port", DEFAULT_SERVER_PORT)))
            self.io.set_protocol(self.settings.value("protocol", DEFAULT_PROTOCOL))
            
            self.io.reconnect()
            
        elif self.connect_action.text() == "Disconnect":
            self.io.shutdown()
    
    def connect_to_recent(self, host, port, protocol):
        self.io.set_server_name(host)
        self.io.set_server_port(port)
        self.io.set_protocol(protocol)
        
        self.io.reconnect()
    
    def set_phosphor_color(self, color):
        self.io.set_phosphor_color(color)
        self.settings.setValue("phosphor_color", color)
        
    def set_cursor_style(self, style):
        self.io.set_cursor_style(style)
        self.settings.setValue("cursor_style", style)
        
    def set_character_set(self, charset):
        self.io.set_character_set(charset)
        self.settings.setValue("character_set", charset)
        
    def set_status(self, txt):
        self.statusBar().setPalette(self.palette)
        self.status_label.setPalette(self.palette)
        self.status_label.setText(txt)
    
    @QtCore.Slot()
    def enable_reconnect(self):
        self.send_file_action.setEnabled(False)
        self.connect_action.setText("Connect")
        for connect_action in self.recent_connections_actions:
            connect_action.setEnabled(True)
        
    @QtCore.Slot()
    def disable_reconnect(self):
        self.send_file_action.setEnabled(True)
        self.update_recent_connections(self.io.host, self.io.port, self.io.protocol)
        self.connect_action.setText("Disconnect")
        for connect_action in self.recent_connections_actions:
            connect_action.setEnabled(False)
    
    @QtCore.Slot(str)
    def set_normal_status(self, txt):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x444444)) # gray
        self.palette.setColor(QtGui.QPalette.WindowText, self.palette.text().color())
        self.set_status(txt)
        
    @QtCore.Slot(str)
    def set_connect_status(self, txt):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x445e44)) # green
        self.palette.setColor(QtGui.QPalette.WindowText, self.palette.text().color())
        self.set_status(txt)
        
    @QtCore.Slot(str)
    def set_error_status(self, txt):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x935353)) # red
        self.palette.setColor(QtGui.QPalette.WindowText, self.palette.text().color())
        self.set_status(txt)
    
    @QtCore.Slot(int, int)
    def set_progress_status(self, n, total):
        self.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0x444444)) # gray
        self.palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("deepskyblue"))
        text = "%*d/%d " % (len(str(total)), n, total)
        how_many = (n / total) * (N_HORZ_CHARS - len(text))
        self.set_status(text + "=" * int(how_many))
    
    @QtCore.Slot()
    def disconnect(self):
        QtCore.QTimer.singleShot(0, self.close)
        
    @QtCore.Slot()
    def send_text_file(self):
        path, _ = QtGui.QFileDialog.getOpenFileName(self, "Send Text File")
        if path:
            self.io.send_text_file(path)
        
    @QtCore.Slot()
    def set_server_info(self):
        dlg = ServerInfoDialog(self.settings, self)
        if dlg.exec_():
            self.set_connect_action_tooltip()
    
    @QtCore.Slot()
    def set_crecho_mode(self):
        flag = self.set_crecho_action.isChecked()
        self.io.set_echo_mode("crecho", flag)
        self.settings.setValue("crecho_mode", int(flag))
    
    @QtCore.Slot()
    def set_lfecho_mode(self):
        flag = self.set_lfecho_action.isChecked()
        self.io.set_echo_mode("lfecho", flag)
        self.settings.setValue("lfecho_mode", int(flag))
    
    @QtCore.Slot()
    def set_localecho_mode(self):
        flag = self.set_localecho_action.isChecked()
        self.io.set_echo_mode("localecho", flag)
        self.settings.setValue("localecho_mode", int(flag))
    
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

class ServerInfoDialog(QtGui.QDialog):

    def __init__(self, settings, parent=None):
        super(ServerInfoDialog, self).__init__(parent)
        self.setWindowTitle("Server Settings")
        
        self.settings = settings
        
        self.server_name_edit = QtGui.QLineEdit("Server")
        self.server_name_edit.setText(settings.value("host", DEFAULT_SERVER_NAME))
        
        self.server_port_edit = QtGui.QLineEdit("Port")
        self.server_port_edit.setValidator(QtGui.QIntValidator(1, 2**16, self))
        self.server_port_edit.setText(str(settings.value("port", DEFAULT_SERVER_PORT)))
        
        self.protocol_combobox = QtGui.QComboBox()
        self.protocol_combobox.addItems(SUPPORTED_PROTOCOLS)
        self.protocol_combobox.setCurrentIndex(self.protocol_combobox.findText(settings.value("protocol", DEFAULT_PROTOCOL)))
        
        protocol_form = QtGui.QFormLayout()
        protocol_form.addRow("Protocol", self.protocol_combobox)
        
        host_port_layout = QtGui.QHBoxLayout()
        host_port_layout.addWidget(self.server_name_edit)
        host_port_layout.addWidget(self.server_port_edit)
        
        self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(host_port_layout)
        main_layout.addLayout(protocol_form)
        main_layout.addWidget(self.buttons)
        
        self.setLayout(main_layout)
        
        self.buttons.accepted.connect(self.update_settings)
        self.buttons.rejected.connect(self.reject)
        
    def update_settings(self):
        self.settings.setValue("host", self.server_name_edit.text())
        self.settings.setValue("port", int(self.server_port_edit.text()))
        self.settings.setValue("protocol", self.protocol_combobox.currentText())
        self.accept()
        
#-- end class ServerInfoDialog
        
if __name__ == "__main__":
    app = QtGui.QApplication([])
    win = TerminalWindow()
    win.show()
    app.exec_()
    
