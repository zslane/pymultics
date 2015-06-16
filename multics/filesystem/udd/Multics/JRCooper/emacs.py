
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
    'set_scroll_range': "[%d;%dr",
    'scroll_up': "M",
    'scroll_down': "D",
}

def _xlate(c):
    if c < ' ':
        return "^" + chr(ord(c) + 64)
    elif c == ESC:
        return "ESC"
    else:
        return c
        
def _write(tty_channel, s):
    call.iox_.write(tty_channel, s)
    
def _send_esc_code(tty_channel, name, *args):
    _write(tty_channel, ESC + ESC_CODES[name] % args)
    
def _clear_screen(tty_channel):
    _send_esc_code(tty_channel, 'clear_screen')
    
def _set_scroll_range(tty_channel, start=0, end=NLINES-1):
    _send_esc_code(tty_channel, 'set_scroll_range', start, end)

def _scroll_up(tty_channel, nlines=1):
    for i in range(nlines):
        _send_esc_code(tty_channel, 'scroll_up')

def _scroll_down(tty_channel, nlines=1):
    for i in range(nlines):
        _send_esc_code(tty_channel, 'scroll_down')

def _erase_end_of_line(tty_channel):
    _send_esc_code(tty_channel, 'erase_end_of_line')
    
def _move_cursor_to(tty_channel, row, col):
    _send_esc_code(tty_channel, 'move_cursor_to', row, col)

def _minibuffer_write(tty_channel, s):
    _move_cursor_to(tty_channel, NLINES - 1, 0)
    _erase_end_of_line(tty_channel)
    _write(tty_channel, s)

def _minibuffer_get_line(tty_channel, prompt):
    _minibuffer_write(tty_channel, prompt)
    return ""

class Buffer(object):

    def __init__(self, tty_channel, name, window=None):
        self._tty_channel = tty_channel
        self._filepath = ""
        self._name = name
        self._window = window
        self._lines = []
        self._top_row = 0
        self._lft_col = 0
        self._cursorx = 0
        self._cursory = 0
        self._marginx = 0
        self._readonly = False
        
    def set_window(self, window):
        self._window = window
        
    def set_read_only(self, flag):
        self._readonly = flag
        
    def get_contents(self):
        return "\n".join(self._lines)
    
    def load_file(self, filepath):
        directory = parm()
        file_name = parm()
        
        self._filepath = filepath
        call.sys_.split_path_(filepath, directory, file_name)
        self._name = file_name.val
        
        f = open(vfile_(filepath))
        file_text = f.read()
        f.close()
        self._lines = file_text.split("\n")
        
        self._top_row = 0
        self._lft_col = 0
        self._cursorx = 0
        self._cursory = 0
    
    def save_file(self):
        if not self._filepath:
            path = _minibuffer_get_line(self._tty_channel, "Save file: ")
            if path:
                self._filepath = path
            # end if
        # end if
        if self._filepath:
            f = open(vfile_(self._filepath), "w")
            f.write(self.get_contents())
            f.close()
            _minibuffer_write(self._tty_channel, "File %s saved." % (self._filepath))
            self.restore_cursor()
            
    def clear(self, name):
        self._name = name
        self._lines = []
        self._top_row = 0
        self._lft_col = 0
        self._cursorx = 0
        self._cursory = 0
        self._marginx = 0
        self._readonly = False
        self.draw_lines()
        self.restore_cursor()
        
    def _get_pos(self):
        return self._top_row + self._cursory, self._lft_col + self._cursorx - self._marginx
    
    def restore_cursor(self):
        _move_cursor_to(self._tty_channel, self._window.screeny + self._cursory, self._cursorx)
        
    def draw_lines(self):
        if self._window.visible:
            for i in range(self._window.vsize - 1):
                _move_cursor_to(self._tty_channel, self._window.screeny + i, 0)
                _erase_end_of_line(self._tty_channel)
                try:
                    row = self._top_row + i
                    line = self._lines[row]
                    _write(self._tty_channel, line[self._lft_col:self._lft_col + NCHARS])
                except:
                    pass
            
            self._window.draw_status_bar(self)
    
    def set_special_prompt(self, prompt):
        _move_cursor_to(self._tty_channel, self._window.screeny + self._cursory, 0)
        _erase_end_of_line(self._tty_channel)
        _write(self._tty_channel, prompt)
        self._marginx = len(prompt)
        self._cursorx = self._marginx
        
    def prev_char_command(self):
        self._cursorx -= 1
        if self._cursorx < self._marginx:
            self._cursory -= 1
            if self._cursory < 0:
                if self._top_row > 0:
                    # scroll down
                    pass
                self._cursory = 0
            # end if
            self._cursorx = self._marginx + len(self._lines[self._top_row + self._cursory])
        # end if
        _move_cursor_to(self._tty_channel, self._window.screeny + self._cursory, self._cursorx)
        
    def next_char_command(self):
        row, col = self._get_pos()
        self._cursorx += 1
        if self._cursorx == NCHARS:
            # scroll window left
            pass
        elif self._cursorx > len(self._lines[row]):
            #== Move to beginning of next line...
            if row < len(self._lines) - 1:
                #== ...but only if there is a next line
                self._cursorx = self._marginx
                self._cursory += 1
                if self._cursory == self._window.vsize - 1:
                    self._window.scroll_up()
                    if row + self._window.vsize - 1 < len(self._lines):
                        _move_cursor_to(self._tty_channel, self._window.screeny + self._window.vsize - 1, 0)
                        _write(self._tty_channel, self._lines[row + self._window.vsize - 1][:NCHARS])
                    self._cursory -= 1
            else:
                self._cursorx -= 1
                return
                
        self.restore_cursor()
        
    def prev_line_command(self):
        row, col = self._get_pos()
        if row > 0:
            self._cursory -= 1
            if self._cursory < 0:
                for i in range(self._window.vsize // 2 - 1):
                    if self._top_row > 0:
                        self._top_row -= 1
                        self._window.scroll_down()
                        _move_cursor_to(self._tty_channel, self._window.screeny, 0)
                        _write(self._tty_channel, self._lines[self._top_row][:NCHARS])
                        self._cursory += 1
                
        self.restore_cursor()
        
    def next_line_command(self):
        row, col = self._get_pos()
        if row < len(self._lines) - 1:
            #== Move to next line...
            n_visible_chars = len(self._lines[row + 1][self._lft_col:self._lft_col + NCHARS])
            self._cursorx = min(self._cursorx, n_visible_chars)
            if self._lft_col > 0 and n_visible_chars == 0:
                self._lft_col = min(0, self._lft_col - NCHARS // 2)
                self.draw_lines()
                self._cursorx = min(self._cursorx, len(self._lines[row + 1][self._lft_col:self._lft_col + NCHARS]))
            self._cursory += 1
            if self._cursory == self._window.vsize - 1:
                for i in range(self._window.vsize // 2 - 1):
                    if row + i + 1 < len(self._lines):
                        self._top_row += 1
                        self._window.scroll_up()
                        _move_cursor_to(self._tty_channel, self._window.screeny + self._window.vsize - 2, 0)
                        _write(self._tty_channel, self._lines[row + i + 1][:NCHARS])
                        self._cursory -= 1
                
        self.restore_cursor()

    def begin_line_command(self):
        self._cursorx = 0
        if self._lft_col > 0:
            self._lft_col = 0
            self.draw_lines()
        self.restore_cursor()
        
    def end_line_command(self):
        row, col = self._get_pos()
        if len(self._lines[row][self._lft_col:self._lft_col + NCHARS]) >= NCHARS:
            self._lft_col = len(self._lines[row]) - NCHARS + 1
            self.draw_lines()
            self._cursorx = NCHARS - 1
        else:
            self._cursorx = len(self._lines[row][self._lft_col:self._lft_col + NCHARS])
        self.restore_cursor()
        
    def insert_character(self, c):
        row, col = self._get_pos()
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
            if self._cursory == self._window.screeny + self._window.vsize - 1:
                # scroll up
                pass
            else:
                self._cursory += 1
                if row + 1 < len(self._lines):
                    self._window.scroll_down(self._cursory)
                _move_cursor_to(self._tty_channel, self._window.screeny + self._cursory, 0)
                _write(self._tty_channel, line_to_insert[:NCHARS])
            # end if
            self._cursorx = self._marginx
        else:
            n = NCHARS - col
            _write(self._tty_channel, self._lines[row][col:n])
            self._cursorx += 1
        # end if
        self.restore_cursor()
    
    def delete_previous_character(self):
        row, col = self._get_pos()
        if col == 0:
            if row > 0:
                # delete a CR and merge lines
                pass
        else:
            self._lines[row] = self._lines[row][:col-1] + self._lines[row][col:]
            self._cursorx -= 1
            self.restore_cursor()
            _erase_end_of_line(self._tty_channel)
            _write(self._tty_channel, self._lines[row][col:NCHARS])
            self.restore_cursor()
    
    def delete_current_character(self):
        row, col = self._get_pos()
        if col == len(self._lines[row]):
            if row < len(self._lines):
                # delete a CR and merge lines
                line_to_merge = self._lines.pop(row + 1)
                self._lines[row] += line_to_merge
                _write(self._tty_channel, self._lines[row][col:NCHARS])
                self._window.scroll_up(self._cursory + 1)
                if row + self._window.vsize - 1 < len(self._lines):
                    _move_cursor_to(self._tty_channel, self._window.screeny + self._window.vsize - 1, 0)
                    _write(self._tty_channel, self._lines[row + self._window.vsize - 1][:NCHARS])
                self.restore_cursor()
                return CR
        else:
            c = self._lines[row][col]
            self._lines[row] = self._lines[row][:col] + self._lines[row][col+1:]
            _write(self._tty_channel, self._lines[row][col:NCHARS])
            if len(self._lines[row]) < NCHARS - 1:
                _erase_end_of_line(self._tty_channel)
            self.restore_cursor()
            return c
    
    def delete_to_line_end(self):
        row, col = self._get_pos()
        if col == len(self._lines[row]):
            # delete CR
            return self.delete_current_character()
        else:
            s = self._lines[row][col:]
            self._lines[row] = self._lines[row][:col]
            _erase_end_of_line(self._tty_channel)
            return s
    
class Window(object):

    def __init__(self, tty_channel, has_status_bar=True):
        self._tty_channel = tty_channel
        self.screeny = 0
        self.vsize = 0
        self.has_status_bar = has_status_bar
        self.visible = False
        
    def setup(self, screeny, vsize, visible):
        self.screeny = screeny
        self.vsize = vsize
        self.visible = visible
    
    def draw_status_bar(self, buffer):
        mode_data = []
        if buffer._name.endswith(".py"):
            mode_data.append("Python")
        elif buffer._name.endswith(".pl1"):
            mode_data.append("PL1")
        else:
            mode_data.append("Fundamental")
        if buffer._readonly:
            mode_data.append("Read Only")
            
        status_bar_text = "=== Emacs 1.0 (%s): %s --- (%d, %d) " % (", ".join(mode_data), buffer._name, buffer._cursorx, buffer._cursory + buffer._top_row)
        rest_of_bar = "=" * (80 - len(status_bar_text))
        status_bar_text += rest_of_bar
        
        _move_cursor_to(self._tty_channel, self.screeny + self.vsize - 1, 0)
        _write(self._tty_channel, status_bar_text)
    
    def scroll_up(self, starting_at=0):
        _set_scroll_range(self._tty_channel, self.screeny + starting_at, self.screeny + self.vsize - 2) # don't scroll the status bar
        _scroll_up(self._tty_channel)
        _set_scroll_range(self._tty_channel)
    
    def scroll_down(self, starting_at=0):
        _set_scroll_range(self._tty_channel, self.screeny + starting_at, self.screeny + self.vsize - 2) # don't scroll the status bar
        _scroll_down(self._tty_channel)
        _set_scroll_range(self._tty_channel)
    
class EmacsEditor(object):

    def __init__(self, file_path_list):
        self.tty = get_calling_process_().tty()
        self._return_from_break = False
        self._cursorx = 0
        self._cursory = 0
        self._buffers = []
        self._windows = []
        self._yank_buffer = []
        self._killing = False
        self._scratch_n = 0
        
        w = Window(self.tty, has_status_bar=False)
        w.setup(NLINES - 1, 1, visible=True)
        self._minibuffer = Buffer(self.tty, "*minibuffer*", w)
        
        for i in range(3):
            w = Window(self.tty)
            self._windows.append(w)
            
        if not file_path_list:
            self._windows[0].setup(0, NLINES-1, visible=True)
            self._buffers = [Buffer(self.tty, self._next_scratch(), self._windows[0])]
        else:
            full = parm()
            directory = parm()
            file_name = parm()
            code = parm()
            
            valid_files = []
            for i, filepath in enumerate(file_path_list):
                call.sys_.get_abs_path(filepath, full)
                call.sys_.split_path_(full.path, directory, file_name)
                call.hcs_.fs_file_exists(directory.val, file_name.val, code)
                if code.val == 0:
                    valid_files.append((file_name.val, full.path))
                    
            nbuffers = min(3, len(valid_files))
            wsize = (NLINES - 1) // nbuffers
            for i, (filename, filepath) in enumerate(valid_files):
                if i < len(self._windows):
                    w = self._windows[i]
                    w.setup(i * wsize, wsize, visible=True)
                else:
                    w = None
                    
                b = Buffer(self.tty, "", w)
                b.load_file(filepath)
                self._buffers.append(b)
                
        self._current_buffer = self._buffers[0]
        self._cancel_to_buffer = None
        self._minibuffer_callback = None
        
    def _next_scratch(self):
        self._scratch_n += 1
        return "*scratch-%d*" % (self._scratch_n)
        
    def open(self):
        self.redraw()
        self.enter_command_loop()
        
    def redraw(self):
        _clear_screen(self.tty)
        for buffer in self._buffers:
            buffer.draw_lines()
        self._current_buffer.restore_cursor()
        
    def wait_get_char(self):
        iox_control.echo_input_sw = False
        iox_control.enable_signals_sw = True
        iox_control.filter_chars = []
        buffer = parm()
        call.iox_.wait_get_char(self.tty, iox_control, buffer)
        return buffer.val

    def get_char(self):
        iox_control.echo_input_sw = False
        iox_control.enable_signals_sw = True
        iox_control.filter_chars = []
        buffer = parm()
        call.iox_.get_char(self.tty, iox_control, buffer)
        return buffer.val

    def enter_command_loop(self):
        ESC_prefix = False
        CTRLX_prefix = False
        done = False
        
        with on_quit(self._break_handler):
            while not done:
                if self._return_from_break:
                    self._return_from_break = False
                    self.redraw()
                    
                c = self.get_char()
                if not c:
                    continue
                
                if c not in [CTRL('D'), CTRL('K')]:
                    self._killing = False
                    
                if ESC_prefix:
                    ESC_prefix = False
                    if c == 'v':
                        pass
                    else:
                        self.set_status_message("Unkown command ESC-" + _xlate(c))
                    
                elif CTRLX_prefix:
                    CTRLX_prefix = False
                    _move_cursor_to(self.tty, NLINES-1, 0)
                    _erase_end_of_line(self.tty)
                    if c == CTRL('G'):
                        self.cancel_minibuffer()
                    elif c == CTRL('C'):
                        self._minibuffer.set_special_prompt("")
                        done = True
                    elif c == CTRL('F'):
                        self.find_file_command()
                    elif c == 'k':
                        self.clear_buffer_command()
                    elif c == CTRL('S'):
                        self.save_current_buffer()
                    else:
                        self.cancel_minibuffer()
                        self.set_status_message("Unkown command ^X-" + _xlate(c))
                    self._current_buffer.restore_cursor()
                    
                elif c == ESC:
                    ESC_prefix = True
                
                elif c == CTRL('X'):
                    CTRLX_prefix = True
                    self._minibuffer.set_special_prompt("^X-")
                    self._cancel_to_buffer = self._current_buffer
                    self._current_buffer = self._minibuffer
                    
                elif c == CR:
                    if self._current_buffer == self._minibuffer:
                        self.process_minibuffer_input()
                    else:
                        self.insert_character(c)
                elif c == BS:
                    self.delete_previous_character()
                elif c == CTRL('A'):
                    self.begin_line_command()
                elif c == CTRL('B'):
                    self.prev_char_command()
                elif c == CTRL('D'):
                    self.delete_current_character()
                elif c == CTRL('E'):
                    self.end_line_command()
                elif c == CTRL('F'):
                    self.next_char_command()
                elif c == CTRL('G'):
                    if self._current_buffer == self._minibuffer:
                        self._minibuffer.set_special_prompt("")
                        self.cancel_minibuffer()
                    # end if
                elif c == CTRL('K'):
                    self.delete_to_line_end()
                elif c == CTRL('N'):
                    self.next_line_command()
                elif c == CTRL('P'):
                    self.prev_line_command()
                elif c == CTRL('Y'):
                    self.yank_buffer()
                elif c:
                    self.insert_character(c)
            
    def _break_handler(self):
        _move_cursor_to(self.tty, NLINES - 1, 0)
        self._return_from_break = True
        raise BreakCondition
        
    def set_status_message(self, msg):
        self._minibuffer.set_special_prompt(msg)
        self._current_buffer.restore_cursor()
        call.timer_manager_.alarm_call(1.5, self.clear_status_message)
    
    def clear_status_message(self):
        call.timer_manager_.reset_alarm_call(self.clear_status_message)
        self._minibuffer.set_special_prompt("")
        self._current_buffer.restore_cursor()
    
    def cancel_minibuffer(self):
        if self._cancel_to_buffer:
            self._current_buffer = self._cancel_to_buffer
            self._current_buffer.restore_cursor()
            self._cancel_to_buffer = None
    
    def process_minibuffer_input(self):
        s = self._minibuffer.get_contents()
        self._minibuffer.set_special_prompt("")
        callback = self._minibuffer_callback
        self._minibuffer_callback = None
        self.cancel_minibuffer()
        callback(s)
        
    def find_file_command(self):
        self._minibuffer_callback = self.load_file_into_buffer
        self._minibuffer.set_special_prompt("Find file: ")
        
    def load_file_into_buffer(self, filename):
        full = parm()
        directory = parm()
        file_name = parm()
        code = parm()
        call.sys_.get_abs_path(filename, full)
        call.sys_.split_path_(full.path, directory, file_name)
        call.hcs_.fs_file_exists(directory.val, file_name.val, code)
        if code.val == 0:
            self._current_buffer.load_file(full.path)
            self._current_buffer.draw_lines()
            self._current_buffer.restore_cursor()
    
    def clear_buffer_command(self):
        self.cancel_minibuffer()
        self._current_buffer.clear(self._next_scratch())
        
    def save_current_buffer(self):
        self.cancel_minibuffer()
        self._current_buffer.save_file()
        
    def clear_yank_buffer(self):
        self._yank_buffer = []
        self._killing = False
        
    def add_to_yank_buffer(self, c):
        if not self._killing:
            self.clear_yank_buffer()
        self._yank_buffer.extend(list(c))
        self._killing = True
        
    def yank_buffer(self):
        for c in self._yank_buffer:
            self.insert_character(c)
            
    def insert_character(self, c):
        self._current_buffer.insert_character(c)
        
    def delete_previous_character(self):
        self._current_buffer.delete_previous_character()
        
    def delete_current_character(self):
        c = self._current_buffer.delete_current_character()
        self.add_to_yank_buffer(c)
        
    def delete_to_line_end(self):
        s = self._current_buffer.delete_to_line_end()
        self.add_to_yank_buffer(s)
        
    def prev_char_command(self):
        self._current_buffer.prev_char_command()
        
    def next_char_command(self):
        self._current_buffer.next_char_command()
        
    def prev_line_command(self):
        self._current_buffer.prev_line_command()
        
    def next_line_command(self):
        self._current_buffer.next_line_command()
        
    def begin_line_command(self):
        self._current_buffer.begin_line_command()
        
    def end_line_command(self):
        self._current_buffer.end_line_command()
        
def emacs():
    arg_list  = parm()
    code      = parm()
    
    call.cu_.arg_list(arg_list)
        
    editor = EmacsEditor(arg_list.args)
    editor.open()
    