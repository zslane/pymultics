
from multics.globals import *

include.iox_control

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

    def __init__(self, name, screeny=0, vsize=23):
        self._name = name
        self._screeny = screeny
        self._vsize = vsize
        self._lines = []
        
    def draw_lines(self, tty_channel):
        for i, line in enumerate(self._lines):
            _move_cursor_to(tty_channel, self._screeny + i, 0)
            _erase_end_of_line(tty_channel)
            call.iox_.put_chars(tty_channel, line[0:80])
        
        _move_cursor_to(tty_channel, self._screeny + self._vsize - len(self._lines), 0)
        rest_of_bar = "=" * (54 - len(self._name))
        call.iox_.put_chars(tty_channel, "=== Emacs (Fundamental): %s %s" % (self._name, rest_of_bar))
    
class EmacsEditor(object):

    def __init__(self, file_path_list):
        self.tty = get_calling_process_().tty()
        self._cursorx = 0
        self._cursory = 0
        if not file_path_list:
            self._buffers = [Buffer("*new*")]
            self._current_buffer = "*new*"
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
            buffer.draw_lines(self.tty)
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
                _move_cursor_to(self.tty, 24, 0)
                _erase_end_of_line(self.tty)
                if c == CTRL('C'):
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
                _move_cursor_to(self.tty, 24, 0)
                call.iox_.put_chars(self.tty, "^X-")
        
    def save_current_buffer(self):
        pass
        
def emacs():
    arg_list  = parm()
    code      = parm()
    
    call.cu_.arg_list(arg_list)
        
    editor = EmacsEditor(arg_list.args)
    editor.open()
    