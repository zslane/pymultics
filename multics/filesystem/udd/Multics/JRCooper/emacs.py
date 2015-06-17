
from multics.globals import *

include.iox_control

NCHARS = 80
NLINES = 25

BRICK = chr(1)
BS  = chr(8)
LF  = chr(10)
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
        self._dirty = False
        
    def set_window(self, window):
        self._window = window
        
    def set_read_only(self, flag):
        self._readonly = flag
        
    def get_contents(self):
        return "\n".join(self._lines)
        
    def clear_contents(self):
        self._lines = []
        self._top_row = 0
        self._lft_col = 0
        self._cursorx = 0
        self._cursory = 0
        self._marginx = 0
    
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
        if self._filepath:
            f = open(vfile_(self._filepath), "w")
            f.write(self.get_contents())
            f.close()
            self._dirty = False
            self._window.draw_status_bar(self)
            
    def clear(self, name):
        self._name = name
        self._readonly = False
        self._dirty = False
        self.clear_contents()
        self.draw_lines()
        self.restore_cursor()
        
    def _get_pos(self):
        return self._top_row + self._cursory, self._lft_col + self._cursorx - self._marginx
    
    def _update_dirty_state_to(self, state):
        if self._dirty != state and self._name != "*minibuffer*":
            self._dirty = state
            self._window.draw_status_bar(self)
            
    def restore_cursor(self):
        _move_cursor_to(self._tty_channel, self._window.screeny + self._cursory, self._cursorx)
        
    def draw_lines(self, starting_at=0):
        if self._window and self._window.visible:
            for i in range(starting_at, self._window.vsize - 1):
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
        if self._cursorx == self._marginx:
            if self._lft_col > 0:
                # scroll window right
                self._lft_col -= 1
                self.draw_lines()
                self.restore_cursor()
            else:
                self.prev_line_command()
                self.end_line_command()
        else:
            self._cursorx -= 1
            self.restore_cursor()
        
    def next_char_command(self):
        row, _ = self._get_pos()
        if self._lft_col + self._cursorx == len(self._lines[row]):
            self.begin_line_command()
            self.next_line_command()
        elif self._cursorx == NCHARS - 1:
            # scroll window left
            self._lft_col += 1
            self.draw_lines()
            self.restore_cursor()
        else:
            self._cursorx += 1
            self.restore_cursor()
        
    def prev_line_command(self):
        row, _ = self._get_pos()
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
                
            row, _ = self._get_pos()
            self._cursorx = min(self._cursorx, len(self._lines[row]))
        # end if
        self.restore_cursor()
        
    def next_line_command(self):
        row, _ = self._get_pos()
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
    
    def prev_page_command(self):
        new_top_row = max(self._top_row - self._window.vsize + 2, 0)
        if new_top_row != self._top_row:
            self._top_row = new_top_row
            row, _ = self._get_pos()
            n_visible_chars = len(self._lines[row][self._lft_col:self._lft_col + NCHARS])
            self._cursorx = min(self._cursorx, n_visible_chars)
            if self._lft_col > 0 and n_visible_chars == 0:
                self._lft_col = min(0, self._lft_col - NCHARS // 2)
            self.draw_lines()
            self.restore_cursor()
    
    def next_page_command(self):
        new_top_row = min(self._top_row + self._window.vsize - 2, len(self._lines) - self._window.vsize + 1)
        if new_top_row != self._top_row:
            self._top_row = new_top_row
            row, _ = self._get_pos()
            n_visible_chars = len(self._lines[row][self._lft_col:self._lft_col + NCHARS])
            self._cursorx = min(self._cursorx, n_visible_chars)
            if self._lft_col > 0 and n_visible_chars == 0:
                self._lft_col = min(0, self._lft_col - NCHARS // 2)
            self.draw_lines()
            self.restore_cursor()
    
    def begin_line_command(self):
        self._cursorx = self._marginx
        if self._lft_col > 0:
            self._lft_col = 0
            self.draw_lines()
        self.restore_cursor()
        
    def end_line_command(self):
        row, _ = self._get_pos()
        n_visible_chars = len(self._lines[row][self._lft_col:self._lft_col + NCHARS])
        if n_visible_chars >= NCHARS:
            self._lft_col = len(self._lines[row]) - NCHARS + 1
            self.draw_lines()
            self._cursorx = NCHARS - 1
        else:
            self._cursorx = n_visible_chars
        self.restore_cursor()
        
    def buffer_home_command(self):
        if self._top_row != 0 or self._lft_col != 0:
            self._top_row = 0
            self._lft_col = 0
            self.draw_lines()
        # end if
        self._cursorx = self._marginx
        self._cursory = 0
        self.restore_cursor()
        
    def buffer_end_command(self):
        self._cursory = self._window.vsize - 2
        row, _ = self._get_pos()
        new_top_row = len(self._lines) - self._window.vsize + 1
        new_lft_col = max(0, len(self._lines[row]) - NCHARS + 1)
        
        if new_top_row != self._top_row:
            self._top_row = new_top_row
            row, _ = self._get_pos()
            self._lft_col = max(0, len(self._lines[row]) - NCHARS + 1)
            self.draw_lines()
            
        elif new_lft_col != self._lft_col:
            self._lft_col = new_lft_col
            self.draw_lines()
        # end if
        
        n_visible_chars = len(self._lines[row][self._lft_col:self._lft_col + NCHARS])
        self._cursorx = n_visible_chars + self._marginx
        self.restore_cursor()
        
    def scroll_up_command(self):
        if self._top_row != len(self._lines) - self._window.vsize + 1:
            self._top_row += 1
            self._window.scroll_up()
            _move_cursor_to(self._tty_channel, self._window.screeny + self._window.vsize - 2, 0)
            _write(self._tty_channel, self._lines[self._top_row + self._window.vsize - 2][:NCHARS])
            self._cursory = max(0, self._cursory - 1)
            self.restore_cursor()
    
    def scroll_down_command(self):
        if self._top_row != 0:
            self._top_row -= 1
            self._window.scroll_down()
            _move_cursor_to(self._tty_channel, self._window.screeny, 0)
            _write(self._tty_channel, self._lines[self._top_row][:NCHARS])
            self._cursory = min(self._window.vsize - 2, self._cursory + 1)
            self.restore_cursor()
    
    def insert_character(self, c):
        if c == LF: c = CR
        
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
        self._update_dirty_state_to(True)
        self.restore_cursor()
    
    def insert_textblock(self, char_list):
        row, col = self._get_pos()
        textblock = "".join(char_list)
        lines = textblock.split(CR)
        rest_of_line = self._lines[row][col:]
        line = lines.pop(0)
        lines_inserted = len(lines)
        self._lines[row] = self._lines[row][:col] + line
        while lines:
            row += 1
            line = lines.pop(0)
            self._lines.insert(row, line)
        # end while
        self._lines[row] += rest_of_line
        if lines_inserted > 0:
            self.draw_lines(starting_at=self._cursory)
            self._cursory = min(self._cursory + lines_inserted, self._window.vsize - 2)
        else:
            _write(self._tty_channel, self._lines[row][col:NCHARS])
            self.end_line_command()
        
        self._update_dirty_state_to(True)
        self.restore_cursor()
        
    def delete_previous_character(self):
        row, col = self._get_pos()
        if col == 0:
            if row > 0:
                # delete a CR and merge lines
                self.prev_line_command()
                self.end_line_command()
                self.delete_current_character()
        else:
            self._lines[row] = self._lines[row][:col-1] + self._lines[row][col:]
            self._cursorx -= 1
            self.restore_cursor()
            _erase_end_of_line(self._tty_channel)
            _write(self._tty_channel, self._lines[row][col:NCHARS])
            self._update_dirty_state_to(True)
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
                self._update_dirty_state_to(True)
                self.restore_cursor()
                return CR
        else:
            c = self._lines[row][col]
            self._lines[row] = self._lines[row][:col] + self._lines[row][col+1:]
            _write(self._tty_channel, self._lines[row][col:NCHARS])
            if len(self._lines[row]) < NCHARS - 1:
                _erase_end_of_line(self._tty_channel)
            self._update_dirty_state_to(True)
            self.restore_cursor()
            return c
    
    def delete_to_line_end(self):
        row, col = self._get_pos()
        if col == len(self._lines[row]):
            # delete CR
            return self.delete_current_character()
        else:
            s = self._lines[row][col:]
            _erase_end_of_line(self._tty_channel)
            self._lines[row] = self._lines[row][:col]
            self._update_dirty_state_to(True)
            self.restore_cursor()
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
            mode_data.append("Python Mode")
        elif buffer._name.endswith(".pl1"):
            mode_data.append("PL1 Mode")
        else:
            mode_data.append("Fundamental Mode")
        if buffer._readonly:
            mode_data.append("Read Only")
        mode_string = ", ".join(mode_data)
        
        # dirty_flag = " -- (modified)" if buffer._dirty and not buffer._name.startswith("*scratch-") else ""
        # status_bar_text = "--- Emacs 1.0 (%s) -- %s%s " % (mode_string, buffer._name, dirty_flag)
        dirty_flag = "*" if buffer._dirty and not buffer._name.startswith("*scratch-") else ""
        status_bar_text = BRICK*3 + " %s (%s) " % (dirty_flag + buffer._name, mode_string)
        rest_of_bar = BRICK * (80 - len(status_bar_text))
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
        self._yes_no_callback = None
        self._yes_no_arg = None
        self._yes_no_prompt = None
        
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
        QUOTE_char = False
        
        self.done = False
        
        with on_quit(self._break_handler):
            while not self.done:
                if self._return_from_break:
                    self._return_from_break = False
                    self.redraw()
                    
                c = self.get_char()
                if not c:
                    continue
                
                if c not in [CTRL('D'), CTRL('K')]:
                    self._killing = False
                    
                if QUOTE_char:
                    QUOTE_char = False
                    self.insert_character(c)
                    
                elif ESC_prefix:
                    ESC_prefix = False
                    _move_cursor_to(self.tty, NLINES-1, 0)
                    _erase_end_of_line(self.tty)
                    
                    if c == CTRL('G'):
                        pass
                        
                    elif c == 'v':
                        self.prev_page_command()
                    elif c == 'z':
                        self.scroll_down_command()
                    elif c == '<':
                        self.buffer_home_command()
                    elif c == '>':
                        self.buffer_end_command()
                    else:
                        self.set_status_message("Unknown command ESC-" + _xlate(c))
                        
                    self._current_buffer.restore_cursor()
                    
                elif CTRLX_prefix:
                    CTRLX_prefix = False
                    _move_cursor_to(self.tty, NLINES-1, 0)
                    _erase_end_of_line(self.tty)
                    
                    if c == CTRL('G'):
                        pass
                        
                    elif c == CTRL('C'):
                        self.quit_command()
                        continue
                        
                    elif c == CTRL('B'):
                        print "Buffers:"
                        for buffer in self._buffers:
                            print " *" if buffer._dirty else "  ", buffer._name
                        
                    elif c == CTRL('F'):
                        self.find_file_command()
                    elif c == CTRL('S'):
                        self.save_file_command()
                    elif c == CTRL('W'):
                        self.write_file_command()
                    elif c == 'k':
                        self.kill_buffer_command()
                    elif c == 'n':
                        self.next_buffer_command()
                    elif c == 'p':
                        self.prev_buffer_command()
                    elif c == '1':
                        self.single_window_command()
                    elif c == '2':
                        self.split_window_command()
                    else:
                        self.set_status_message("Unknown command ^X-" + _xlate(c))
                        
                    self._current_buffer.restore_cursor()
                    
                elif c == ESC:
                    if self._current_buffer != self._minibuffer:
                        ESC_prefix = True
                        self._minibuffer.set_special_prompt("ESC-")
                
                elif c == CTRL('X'):
                    if self._current_buffer != self._minibuffer:
                        CTRLX_prefix = True
                        self._minibuffer.set_special_prompt("^X-")
                    
                elif c == CTRL('Q'):
                    if self._current_buffer != self._minibuffer:
                        QUOTE_char = True
                        
                elif c in [CR, LF]:
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
                elif c == CTRL('K'):
                    self.delete_to_line_end()
                elif c == CTRL('N'):
                    self.next_line_command()
                elif c == CTRL('P'):
                    self.prev_line_command()
                elif c == CTRL('V'):
                    self.next_page_command()
                elif c == CTRL('Y'):
                    self.yank_buffer()
                elif c == CTRL('Z'):
                    self.scroll_up_command()
                elif (' ') <= c <= ('~'):
                    self.insert_character(c)
                else:
                    self.set_status_message("Unknown command " + _xlate(c))
            
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
    
    def minibuffer_command(self, prompt, callback):
        self._cancel_to_buffer = self._current_buffer
        self._current_buffer = self._minibuffer
        self._minibuffer_callback = callback
        self._minibuffer.set_special_prompt(prompt + ": ")
    
    def minibuffer_yes_no(self, prompt, callback, arg):
        self._yes_no_prompt = prompt
        self._yes_no_callback = callback
        self._yes_no_arg = arg
        self.minibuffer_command(prompt + " (Y/N)", self._yes_no_handler)
    
    def cancel_minibuffer(self):
        if self._cancel_to_buffer:
            self._current_buffer = self._cancel_to_buffer
            self._current_buffer.restore_cursor()
            self._cancel_to_buffer = None
    
    def process_minibuffer_input(self):
        s = self._minibuffer.get_contents()
        self._minibuffer.clear_contents()
        self._minibuffer.set_special_prompt("")
        callback = self._minibuffer_callback
        self._minibuffer_callback = None
        self.cancel_minibuffer()
        callback(s)
        
    def _yes_no_handler(self, answer):
        if answer.lower() in ["yes", "y"]:
            self._yes_no_callback(self._yes_no_arg)
        elif answer.lower() in ["no", "n"]:
            self._current_buffer.restore_cursor()
        else:
            #== Reassert the existing prompt, callback, and arg
            self.minibuffer_yes_no(self._yes_no_prompt, self._yes_no_callback, self._yes_no_arg)
        
    def quit_command(self):
        if any([ buffer._dirty for buffer in self._buffers ]):
            self.minibuffer_yes_no("Modified buffers exist. Quit anyway?", self._set_done_flag, True)
        else:
            self._set_done_flag(True)
            
    def _set_done_flag(self, flag):
        self.done = flag
        _move_cursor_to(self.tty, NLINES-1, 0)
        _erase_end_of_line(self.tty)
        
    def find_file_command(self):
        self.minibuffer_command("Find file", self._load_file_into_buffer)
        
    def _load_file_into_buffer(self, filename):
        full = parm()
        directory = parm()
        file_name = parm()
        code = parm()
        call.sys_.get_abs_path(filename, full)
        call.sys_.split_path_(full.path, directory, file_name)
        call.hcs_.fs_file_exists(directory.val, file_name.val, code)
        if code.val == 0:
            cur_window = self._current_buffer._window
            self._current_buffer.set_window(None)
            new_buffer = Buffer(self.tty, file_name, cur_window)
            self._buffers.append(new_buffer)
            
            self._current_buffer = new_buffer
            self._current_buffer.load_file(full.path)
            self._current_buffer.draw_lines()
        else:
            self.set_status_message("Could not find file %s." % (full.path))
            
        self._current_buffer.restore_cursor()
    
    def kill_buffer_command(self):
        if self._current_buffer._dirty:
            self.minibuffer_yes_no("Modified buffer not saved. Kill anyway?", self._kill_buffer, None)
        else:
            self._kill_buffer()
        
    def _kill_buffer(self, *args):
        #== If the current buffer is an unsaved scratch buffer, then just clear it out
        if self._current_buffer._name.startswith("*scratch-"):
            self._current_buffer.clear(self._current_buffer._name)
            return
            
        cur_window = self._current_buffer._window
        
        switch_to = None
        for buffer in self._buffers[:]:
            if buffer is self._current_buffer:
                self._buffers.remove(buffer)
            elif not buffer._window:
                switch_to = buffer
            
        if not switch_to:
            switch_to = Buffer(self.tty, self._next_scratch(), cur_window)
            self._buffers.append(switch_to)
        else:
            switch_to.set_window(cur_window)
            
        self._current_buffer = switch_to
        self._current_buffer.draw_lines()
        self._current_buffer.restore_cursor()
        
    def save_file_command(self):
        if not self._current_buffer._filepath:
            self.minibuffer_command("Save file", self._save_file_as)
        else:
            self.save_current_buffer()
            # self._current_buffer.restore_cursor()
        
    def _save_file_as(self, filename):
        full = parm()
        directory = parm()
        file_name = parm()
        code = parm()
        call.sys_.get_abs_path(filename, full)
        call.sys_.split_path_(full.path, directory, file_name)
        call.hcs_.fs_file_exists(directory.val, file_name.val, code)
        if code.val == 0:
            self.minibuffer_yes_no("File already exists. Overwrite?", self._save_buffer_to_file, full.path)
        else:
            self._save_buffer_to_file(full.path)
            
    def _save_buffer_to_file(self, filepath):
        directory = parm()
        file_name = parm()
        call.sys_.split_path_(filepath, directory, file_name)
        self._current_buffer._name = file_name.val
        self._current_buffer._filepath = filepath
        self.save_current_buffer()
        
        self._current_buffer.restore_cursor()
    
    def save_current_buffer(self):
        self._current_buffer.save_file()
        self.set_status_message("File %s saved." % (self._current_buffer._filepath))
    
    def write_file_command(self):
        self.minibuffer_command("Write file", self._save_file_as)
    
    def clear_yank_buffer(self):
        self._yank_buffer = []
        self._killing = False
        
    def add_to_yank_buffer(self, c):
        if not self._killing:
            self.clear_yank_buffer()
        self._yank_buffer.extend(list(c))
        self._killing = True
        
    def yank_buffer(self):
        self._current_buffer.insert_textblock(self._yank_buffer)
        
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
        
    def prev_page_command(self):
        self._current_buffer.prev_page_command()
        
    def next_page_command(self):
        self._current_buffer.next_page_command()
        
    def begin_line_command(self):
        self._current_buffer.begin_line_command()
        
    def end_line_command(self):
        self._current_buffer.end_line_command()
        
    def buffer_home_command(self):
        self._current_buffer.buffer_home_command()
        
    def buffer_end_command(self):
        self._current_buffer.buffer_end_command()
        
    def scroll_up_command(self):
        self._current_buffer.scroll_up_command()
        
    def scroll_down_command(self):
        self._current_buffer.scroll_down_command()
        
    def prev_buffer_command(self):
        visible_buffers = sorted([ buffer for buffer in self._buffers if buffer._window and buffer._window.visible ], key=lambda buffer: buffer._window.screeny)
        index = visible_buffers.index(self._current_buffer)
        index = (index - 1) % len(visible_buffers)
        self._current_buffer = visible_buffers[index]
        
    def next_buffer_command(self):
        visible_buffers = sorted([ buffer for buffer in self._buffers if buffer._window and buffer._window.visible ], key=lambda buffer: buffer._window.screeny)
        index = visible_buffers.index(self._current_buffer)
        index = (index + 1) % len(visible_buffers)
        self._current_buffer = visible_buffers[index]
        
    def single_window_command(self):
        for buffer in self._buffers:
            if buffer is not self._current_buffer and buffer._window and buffer._window.visible:
                buffer._window.visible = False
        self._current_buffer._window.setup(0, NLINES-1, visible=True)
        self._current_buffer.draw_lines()
        
    def split_window_command(self):
        for window in self._windows:
            if not window.visible:
                window_to_use = window
                break
            # end if
        else:
            return
            
        for buffer in self._buffers:
            if buffer._window is window_to_use:
                buffer._window = None
                
        new_buffer = Buffer(self.tty, self._next_scratch(), window_to_use)
        self._buffers.append(new_buffer)
        
        visible_windows = [ w for w in self._windows if w.visible ]
        visible_windows.insert(visible_windows.index(self._current_buffer._window) + 1, window_to_use)
        
        screeny = 0
        vsize = (NLINES - 1) // len(visible_windows)
        for w in visible_windows:
            w.setup(screeny, vsize, visible=True)
            screeny += vsize
            
        for buffer in self._buffers:
            if buffer._window and buffer._window.visible:
                buffer.draw_lines()
        
def emacs():
    arg_list  = parm()
    code      = parm()
    
    call.cu_.arg_list(arg_list)
        
    editor = EmacsEditor(arg_list.args)
    editor.open()
    