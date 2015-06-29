from pprint import pprint
from PySide import QtCore, QtGui

import os
import sys
import ast
import cPickle as pickle

NRM, BRI, DIM, _, UND, BLI, _, REV, HID, ALL = (0,1,2,4,8,16,32,64,128,256)
GLYPHSET_KEYS = [NRM, UND, REV, UND|REV, BRI, BRI|UND, BRI|REV, BRI|UND|REV, DIM, DIM|UND, DIM|REV, DIM|UND|REV, HID]

class FontGlyphs(object):

    ord_BS = 8
    ord_CR = 13
    ord_LF = 10
    ord_SP = 32
    ord_BK = 128
    
    def __init__(self, path):
        self.cell_width = 10
        self.cell_height = 22
        
        if path.endswith(".glyphs"):
            self.glyphs = self.load(path)
        elif path.endswith(".bmp"):
            self.glyphs = self.loadGlyphPixmaps(path)
        else:
            self.glyphs = self.loadGlyphData(path)
            
    def load(self, path):
        with open(path, "r") as f:
            return pickle.load(f)
            
    def save(self, path):
        with open(path, "w") as f:
            pickle.dump(self.glyphs, f)
    
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
    
class GlyphViewer(QtGui.QWidget):

    def __init__(self, font_glyphs, aa=True, parent=None):
        super(GlyphViewer, self).__init__(parent)
        self.font = font_glyphs
        self.aa = aa
        self.wincolor = QtGui.QColor(0, 0, 0)
        self.fontcolor = QtGui.QColor(255, 255, 255)
        self.underline_pen = QtGui.QPen()
        self.underline_pen.setDashPattern([1, 1])
        self.underline_aa_pen = QtGui.QPen()
        self.underline_aa_pen.setDashPattern([1, 1])
        
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Window, self.wincolor)
        self.setPalette(pal)
        
        self.opacity = {
            NRM:         0.85, BRI:         1.00, DIM:         0.42,
            NRM|UND:     0.85, BRI|UND:     1.00, DIM|UND:     0.42,
            NRM|REV:     0.66, BRI|REV:     1.00, DIM|REV:     0.33,
            NRM|REV|UND: 0.66, BRI|REV|UND: 1.00, DIM|REV|UND: 0.33,
        }
        
        self.set_pen_matrix(NRM)
        
        self.image = {}
        
        self.image['Standard'] = QtGui.QImage(self.font.cell_width * len(self.font.glyphs), self.font.cell_height * len(GLYPHSET_KEYS), QtGui.QImage.Format_RGB32)
        self.render_glyphsets()
        
        FONT_NAME = "Glass TTY VT220"
        FONT_SIZE = 20 if sys.platform == "darwin" else 15
        self.altfont = QtGui.QFont(FONT_NAME, FONT_SIZE)
        fm = QtGui.QFontMetrics(self.altfont)
        self.altfont.cell_width = fm.width("M")
        self.altfont.cell_height = max(self.font.cell_height, fm.lineSpacing())
        
        self.image['Alternate'] = QtGui.QImage(self.altfont.cell_width * len(self.font.glyphs), self.altfont.cell_height * len(GLYPHSET_KEYS), QtGui.QImage.Format_RGB32)
        self.render_fontsprites()
        
        self.current_image = "Standard"
        
    def sizeHint(self):
        return self.image[self.current_image].size()
        
    def paintEvent(self, event):
        super(GlyphViewer, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image[self.current_image])
        
    def mouseDoubleClickEvent(self, event):
        if self.current_image == "Standard":
            self.image[self.current_image].save(".\\UiCrt2_StdCharset_Rom.png")
        elif self.current_image == "Alternate":
            self.image[self.current_image].save(".\\UiCrt2_AltCharset_Rom.png")
        QtGui.QMessageBox.information(self, "Info", "Font glyph set saved.")
    
    def set_pen_matrix(self, charattr):
        def invert(t): return map(lambda x: 255 - x, t)
        def scale(t, f): return map(lambda x: int(x * f), t)
        
        white = QtGui.QColor(QtCore.Qt.white)
        black = QtGui.QColor(QtCore.Qt.black)
        
        if charattr & REV:
            dim_by = 150
            dimmer_by = 300
        elif charattr & BRI:
            dim_by = 150
            dimmer_by = 300
        else:
            dim_by = 300
            dimmer_by = 600
        
        pixel_rgb = white.toTuple()[:3]
        dim_rgb = white.darker(dim_by).toTuple()[:3]
        dimmer_rgb = white.darker(dimmer_by).toTuple()[:3]
        bkgd_rgb = black.toTuple()[:3]
        
        if charattr & REV:
            pixel_rgb = invert(pixel_rgb)
            dim_rgb = invert(dim_rgb)
            dimmer_rgb = invert(dimmer_rgb)
            bkgd_rgb = invert(bkgd_rgb)
            
        factor = self.opacity.get(charattr, 0.00)
        pixel_rgb = scale(pixel_rgb, factor)
        dim_rgb = scale(dim_rgb, factor)
        dimmer_rgb = scale(dimmer_rgb, factor)
        bkgd_rgb = scale(bkgd_rgb, factor)
        
        bkgd = QtGui.QPen(QtGui.QColor(*bkgd_rgb))
        pixel = QtGui.QPen(QtGui.QColor(*pixel_rgb))
        if self.aa:
            dim = QtGui.QPen(QtGui.QColor(*dim_rgb))
            dimmer = QtGui.QPen(QtGui.QColor(*dimmer_rgb))
        else:
            dim = dimmer = bkgd
        
        self.pen_matrix = [
            dimmer,  dim,  dimmer,
               dim, pixel, dim,
            dimmer,  dim,  dimmer
        ]
        
        self.pixelcolor = pixel.color()
        self.dimcolor = dim.color()
        self.dimmercolor = dimmer.color()
        self.bkgdcolor = bkgd.color()
    
    def render_glyphsets(self):
        painter = QtGui.QPainter()
        if painter.begin(self.image['Standard']):
            painter.save()
            painter.fillRect(self.image['Standard'].rect(), QtGui.QColor(QtCore.Qt.black))
            
            celly = 0
            for charattr in GLYPHSET_KEYS:
                self.set_pen_matrix(charattr)
                self.underline_pen.setColor(self.pixelcolor)
                self.underline_aa_pen.setColor(self.dimcolor)
                
                if charattr & REV:
                    rev = True
                else:
                    rev = False
                
                cellx = 0
                for glyph in self.font.glyphs:
                    x = cellx * self.font.cell_width + self.documentMargin()
                    y = celly * self.font.cell_height + self.documentMargin()
                    
                    if charattr & HID:
                        # painter.fillRect(QtCore.QRect(x, y, self.font.cell_width, self.font.cell_height), self.wincolor)
                        pass
                    
                    else:
                        self._draw_glyph(painter, glyph, cellx, celly, rev=rev)
                        
                        if charattr & UND:
                            painter.save()
                            painter.setPen(self.underline_pen)
                            painter.drawLine(x, y + self.font.cell_height - 2, x + self.font.cell_width - 1, y + self.font.cell_height - 2)
                            painter.setPen(self.underline_aa_pen)
                            painter.drawLine(x + 1, y + self.font.cell_height - 2, x + self.font.cell_width, y + self.font.cell_height - 2)
                            painter.restore()
                    
                    cellx += 1
                # end for
                celly += 1
            # end for
            painter.restore()
            painter.end()
    
    def render_fontsprites(self):
        painter = QtGui.QPainter()
        if painter.begin(self.image['Alternate']):
            painter.save()
            painter.setFont(self.altfont)
            painter.fillRect(self.image['Alternate'].rect(), QtGui.QColor(QtCore.Qt.black))
            
            celly = 0
            for charattr in GLYPHSET_KEYS:
                self.set_pen_matrix(charattr)
                self.underline_pen.setColor(self.pixelcolor)
                
                if charattr & REV:
                    rev = True
                else:
                    rev = False
                
                cellx = 0
                for i in range(len(self.font.glyphs)):
                    x = cellx * self.altfont.cell_width + self.documentMargin()
                    y = celly * self.altfont.cell_height + self.documentMargin()
                    
                    if charattr & HID:
                        # painter.fillRect(QtCore.QRect(x, y, self.font.cell_width, self.font.cell_height), self.wincolor)
                        pass
                    
                    else:
                        self._draw_sprite(painter, chr(i), cellx, celly, rev=rev)
                        
                        if charattr & UND:
                            painter.save()
                            painter.setPen(self.underline_pen)
                            painter.drawLine(x, y + self.font.cell_height - 2, x + self.font.cell_width - 2, y + self.font.cell_height - 2)
                            painter.setPen(self.underline_pen)
                            painter.drawLine(x + 1, y + self.font.cell_height - 2, x + self.font.cell_width, y + self.font.cell_height - 2)
                            painter.restore()
                    
                    cellx += 1
                # end for
                celly += 1
            # end for
            painter.restore()
            painter.end()
    
    def documentMargin(self):
        return 0
        
    def _draw_glyph(self, painter, glyph, cellx, celly, rev=False):
        s = cellx * self.font.cell_width + self.documentMargin()
        y = celly * self.font.cell_height + self.documentMargin()
        painter.fillRect(QtCore.QRect(s, y, self.font.cell_width, self.font.cell_height), self.bkgdcolor)
        painter.save()
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Darken if rev else QtGui.QPainter.CompositionMode_Lighten)
        for row in glyph:
            x = s
            for pixel in row:
                if pixel:
                    self._draw_pixel(painter, x, y, rev)
                x += 1
            y += 2
        painter.restore()
        
    def _draw_pixel(self, painter, x, y, rev=False):
        pen = iter(self.pen_matrix)
        for dy in [-1, 0, +1]:
            for dx in [-1, 0, +1]:
                painter.setPen(pen.next())
                painter.drawPoint(x + dx + 1, y + dy + 3)
    
    def _draw_sprite(self, painter, c, cellx, celly, rev=False):
        x = cellx * self.altfont.cell_width + self.documentMargin()
        y = celly * self.altfont.cell_height + self.documentMargin()
        r = QtCore.QRect(x, y, self.altfont.cell_width, self.altfont.cell_height)
        painter.fillRect(r, self.bkgdcolor)
        painter.save()
        painter.setPen(QtGui.QPen(self.pixelcolor))
        painter.drawText(r, c, QtGui.QTextOption(QtCore.Qt.AlignTop))
        painter.restore()
        
    def switch_charset_to(self, charset):
        self.current_image = charset
        self.update()
    
class GlyphSaver(QtGui.QWidget):

    def __init__(self, parent=None):
        super(GlyphSaver, self).__init__(parent)
        
        BASE_DIR = ".\\"
        FILENAME = "UiCrt2_Charset"
        basepath = os.path.join(BASE_DIR, FILENAME)
        try:
            assert os.path.getmtime(basepath + ".glyphs") > os.path.getmtime(basepath + ".cpp")
            fg = FontGlyphs(basepath + ".glyphs")
            # fg = FontGlyphs(basepath + ".bmp")
        except:
            print "Rebuilding .glyphs file"
            fg = FontGlyphs(basepath + ".cpp")
            fg.save(basepath + ".glyphs")
        
        self.viewer = GlyphViewer(fg, aa=True)
        
        self.switch_button = QtGui.QPushButton("Switch Character Set")
        self.switch_button.clicked.connect(self.switch_charset)
        
        self.charset_label = QtGui.QLabel("(Currently showing %s)" % (self.viewer.current_image))
        
        self.controls = QtGui.QHBoxLayout()
        self.controls.addWidget(self.switch_button)
        self.controls.addWidget(self.charset_label)
        self.controls.addStretch(1)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.viewer)
        layout.addLayout(self.controls)
        
        self.setLayout(layout)
        
    @QtCore.Slot()
    def switch_charset(self):
        if self.viewer.current_image == "Standard":
            self.viewer.switch_charset_to("Alternate")
            self.charset_label.setText("(Currently showing Alternate)")
        elif self.viewer.current_image == "Alternate":
            self.viewer.switch_charset_to("Standard")
            self.charset_label.setText("(Currently showing Standard)")
        
if __name__ == "__main__":

    app = QtGui.QApplication([])
    
    saver = GlyphSaver()
    saver.show()
    
    app.exec_()
    