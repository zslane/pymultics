
from multics.globals import *

include.iox_control

NCHARS = 80
NLINES = 25

BS  = chr(8)
CR  = chr(13)
ESC = chr(27)

def CTRL(s):
    return chr(ord(s.upper()) - 64)
    
ESC_CODES = {
    'clear_screen': "[2J",
    'move_cursor_to': "[%d;%dH",
    'erase_end_of_line': "[K",
    'erase_start_of_line': "[1K",
}
    
def _send_esc_code(tty_channel, name):
    call.iox_.put_chars(tty_channel, ESC + ESC_CODES[name])
    
def _clear_screen(tty_channel):
    _send_esc_code(tty_channel, 'clear_screen')
    
def _erase_end_of_line(tty_channel):
    _send_esc_code(tty_channel, 'erase_end_of_line')
    
def _move_cursor_to(tty_channel, row, col):
    call.iox_.put_chars(tty_channel, ESC + ESC_CODES['move_cursor_to'] % (row, col))

class Buffer(object):

    def __init__(self, tty_channel, name, screeny=0, vsize=NLINES-2):
        self._tty_channel = tty_channel
        self._name = name
        self._screeny = screeny
        self._vsize = vsize
        self._lines = []
        
    def _map_cursor(self, x, y):
        row = y - self._screeny
        col = x
        return (row, col)
    
    def next_line(self, y):
        row = min(self._screeny + self._vsize - 1, y - self._screeny + 1)
        return row
        
    def draw_lines(self):
        for i, line in enumerate(self._lines):
            _move_cursor_to(self._tty_channel, self._screeny + i, 0)
            _erase_end_of_line(self._tty_channel)
            call.iox_.put_chars(self._tty_channel, line[0:NCHARS])
        
        _move_cursor_to(self._tty_channel, self._screeny + self._vsize - len(self._lines), 0)
        rest_of_bar = "=" * (54 - len(self._name))
        call.iox_.put_chars(self._tty_channel, "=== Emacs (Fundamental): %s %s" % (self._name, rest_of_bar))
    
    def insert_character(self, c, cursorx, cursory):
        row, col = self._map_cursor(cursorx, cursory)
        try:
            self._lines[row] = self._lines[row][:col] + c + self._lines[row][col:]
        except:
            self._lines.append(c)
        # end try
        _erase_end_of_line(self._tty_channel)
        if c == CR:
            line_to_insert = self._lines[row][col + 1:]
            self._lines[row] = self._lines[row][:col]
            self._lines.append(line_to_insert)
            if row == self._screeny + self._vsize:
                # scroll up
                pass
            else:
                _move_cursor_to(self._tty_channel, self._screeny + row + 1, 0)
                call.iox_.put_chars(self._tty_channel, line_to_insert)
            # end if
        else:
            n = NCHARS - col + 1
            call.iox_.put_chars(self._tty_channel, self._lines[row][col:n])
    
class EmacsEditor(object):

    def __init__(self, file_path_list):
        self.tty = get_calling_process_().tty()
        self._cursorx = 0
        self._cursory = 0
        if not file_path_list:
            self._buffers = [Buffer(self.tty, "*scratch*")]
            self._current_buffer = self._buffers[0]
        else:
            for filepath in file_path_list:
                # load file
                pass
            self._current_buffer = filepath
        
    def open(self):
        self.redraw()
        self.enter_command_loop()
        
    def redraw(self):
        _clear_screen(self.tty)
        for buffer in self._buffers:
            buffer.draw_lines()
        _move_cursor_to(self.tty, self._cursory, self._cursorx)
        
    def wait_get_char(self):
        iox_control.echo_input_sw = False
        iox_control.enable_signals_sw = True
        iox_control.filter_chars = []
        buffer = parm()
        call.iox_.wait_get_char(self.tty, iox_control, buffer)
        return buffer.val

    def enter_command_loop(self):
        ESC_prefix = False
        CTRLX_prefix = False
        
        while True:
            c = self.wait_get_char()
            
            if ESC_prefix:
                ESC_prefix = False
                
            elif CTRLX_prefix:
                CTRLX_prefix = False
                _move_cursor_to(self.tty, NLINES-1, 0)
                _erase_end_of_line(self.tty)
                if c == CTRL('G'):
                    pass
                elif c == CTRL('C'):
                    break
                elif c == CTRL('S'):
                    self.save_current_buffer()
                else:
                    call.iox_.put_chars(self.tty, "Unknown command ^X-" + c)
                _move_cursor_to(self.tty, self._cursory, self._cursorx)
                    
            elif c == ESC:
                ESC_prefix = True
            
            elif c == CTRL('X'):
                CTRLX_prefix = True
                _move_cursor_to(self.tty, NLINES-1, 0)
                call.iox_.put_chars(self.tty, "^X-")
                
            elif c == CR:
                self.insert_character(c)
                self._cursorx = 0
                self._cursory = self._current_buffer.next_line(self._cursory)
                _move_cursor_to(self.tty, self._cursory, self._cursorx)
            elif c == BS:
                self.delete_previous_character()
            elif c == CTRL('D'):
                self.delete_current_character()
            else:
                self.insert_character(c)
        
    def save_current_buffer(self):
        print "\n".join(self._current_buffer._lines)
        
    def insert_character(self, c):
        self._current_buffer.insert_character(c, self._cursorx, self._cursory)
        self._cursorx = min(NCHARS-1, self._cursorx + 1)
        _move_cursor_to(self.tty, self._cursory, self._cursorx)
        
    def delete_previous_character(self):
        pass
        
    def delete_current_character(self):
        pass
        
def emacs():
    arg_list  = parm()
    code      = parm()
    
    call.cu_.arg_list(arg_list)
        
    editor = EmacsEditor(arg_list.args)
    editor.open()
    