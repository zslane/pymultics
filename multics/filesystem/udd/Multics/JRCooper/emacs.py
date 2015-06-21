import os
import re
import stat

from multics.globals import *

include.iox_control

declare (get_wdir_ = entry . returns (char(168)))

NCHARS = 80
NLINES = 25

BS  = chr(8)
TAB = chr(9)
LF  = chr(10)
CR  = chr(13)
ESC = chr(27)
ARR = chr(28)

Character_Handled = True

def CTRL(s):
    return chr(ord(s.upper()) - 64)
    
ESC_CODES = {
    'normal_video':      ESC + "[0m",
    'reverse_video':     ESC + "[7m",
    'underline_mode':    ESC + "[4m",
    'bold_video':        ESC + "[1m",
    'clear_screen':      ESC + "[2J",
    'move_cursor_to':    ESC + "[%d;%dH",
    'erase_end_of_line': ESC + "[K",
    'set_scroll_range':  ESC + "[%d;%dr",
    'scroll_up':         ESC + "M",
    'scroll_down':       ESC + "D",
}

FORMAT_NORMAL = "0"
FORMAT_BOLD = "1"
FORMAT_DIM = "2"
FORMAT_UNDERLINE = "4"
FORMAT_BLINKING = "5"
FORMAT_REVERSE = "7"
FORMAT_HIDDEN = "8"

def _xlate(c):
    if c == ESC:
        return "ESC"
    elif c < ' ':
        return "^" + chr(ord(c) + 64)
    else:
        return c
        
def _is_readonly_file(multics_path):
    native_path = vfile_(multics_path)
    return os.path.exists(native_path) and (os.stat(native_path).st_mode & (stat.S_IWUSR|stat.S_IWGRP|stat.S_IWOTH) == 0)

def _is_directory(multics_path):
    native_path = vfile_(multics_path)
    return os.path.isdir(native_path)
    
def _write(tty_channel, s):
    call.iox_.write(tty_channel, str(s))
    
def _send_esc_code(tty_channel, name, *args):
    _write(tty_channel, ESC_CODES[name] % args)
    
def _normal_video(tty_channel):
    _send_esc_code(tty_channel, 'normal_video')
    
def _reverse_video(tty_channel):
    _send_esc_code(tty_channel, 'reverse_video')
    
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

def _underline(s):
    return CTRL('U') + s
    
def _bold(s):
    return CTRL('B') + s
    
def _reverse(s):
    return CTRL('R') + s
    
class BufferLine(object):

    def __init__(self, parent_buffer, text, attrs=[]):
        self._tty_channel = parent_buffer._tty_channel
        self._buffer = parent_buffer
        self._text = text
        # video attributes apply to the entire line of characters.
        self._attrs = attrs
        
    def __len__(self):
        return len(self._text)
        
    def __getitem__(self, index):
        return BufferLine(self._buffer, self._text[index], self._attrs)
        
    def __add__(self, s):
        return BufferLine(self._buffer, self._text + str(s), self._attrs)
        
    def __iadd__(self, s):
        self._text += str(s)
        return self
        
    def __str__(self):
        return self._text
        
    def _write_attrs_begin(self):
        if self._attrs:
            attr_esc_string = ESC + "[" + ";".join(self._attrs) + "m"
            _write(self._tty_channel, attr_esc_string)
            
    def _write_attrs_end(self):
        if self._attrs:
            _write(self._tty_channel, ESC_CODES['normal_video'])
        
    def write(self, starting_at=0, cursorx=0):
        if starting_at == 0:
            starting_at = self._buffer._lft_col
        # end if
        max_chars = NCHARS - cursorx
        n_chars_to_write = max(0, len(self._text) - starting_at)
        if n_chars_to_write:
            self._write_attrs_begin() # video attributes apply to the entire line of characters.
            _write(self._tty_channel, self._text[starting_at:starting_at + max_chars])
            self._write_attrs_end()
    
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
        self._marginy = 0
        self._dirty = False
        self._readonly = False
        self._selectonly = False
        self._selections = {}
        self._select_callback = None
        self._select_cancel_to_buffer = None
        
    def filepath(self):    return self._filepath
    def name(self):        return self._name
    def window(self):      return self._window
    def cancel_to(self):   return self._select_cancel_to_buffer
    def is_readonly(self): return self._readonly
    def is_select(self):   return self._selectonly
    def is_modified(self): return self._dirty
    def is_visible(self):  return self._window and self._window.visible
    
    def set_window(self, window):
        self._window = window
        
    def set_read_only(self, flag):
        self._readonly = flag
        
    def set_file_path(self, file_path, name_resolver=None):
        self._filepath = file_path
        
        file_name = parm()
        call.sys_.split_path_(file_path, null(), file_name)
        if name_resolver:
            file_name.val = name_resolver(file_name.val)
        # end if
        self._name = file_name.val
        
    def set_name(self, name):
        self._name = name
        
    def get_contents(self):
        return "\n".join(map(str, self._lines))
        
    def clear_contents(self):
        self._lines = []
        self._top_row = 0
        self._lft_col = 0
        self._cursorx = 0
        self._cursory = 0
        self._marginx = 0
        self._marginy = 0
    
    def visit_file(self, filepath, name_resolver=None):
        self.set_file_path(filepath, name_resolver)
        self.clear_contents()
    
    def load_file(self, filepath, name_resolver=None):
        self.set_file_path(filepath, name_resolver)
        
        f = open(vfile_(filepath))
        file_text = f.read()
        f.close()
        
        self._lines = [ BufferLine(self, line) for line in file_text.split("\n") ]
        
        self._top_row = 0
        self._lft_col = 0
        self._cursorx = 0
        self._cursory = 0
        self._readonly = _is_readonly_file(filepath)
    
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
        self._selectonly = False
        self._selections = {}
        self._select_callback = None
        self._select_cancel_to_buffer = None
        
        self.clear_contents()
        self.draw_lines()
        self.restore_cursor()
        
    def set_selections(self, title, lines, selections, callback):
        self._selections = dict(enumerate(selections))
        self._select_callback = callback
        self._selectonly = True
        self._readonly = True
        self._top_row = 0
        self._lft_col = 0
        self._cursorx = 0
        self._cursory = 0
        
        FORMATTING = { CTRL('B'):FORMAT_BOLD, CTRL('R'):FORMAT_REVERSE, CTRL('U'):FORMAT_UNDERLINE }
        format_regexp = re.compile("[%s]" % ("".join(FORMATTING)))
        
        self._lines = [BufferLine(self, title, [FORMAT_UNDERLINE])]
        for line in lines:
            attrs = [ FORMATTING[format_byte] for format_byte in format_regexp.findall(line) ]
            self._lines.append(BufferLine(self, line[len(attrs):], attrs))
        # end for
        
        self._marginy = 1
        self._cursory = 1 # start the user someplace useful, first line below the title
        self.draw_lines()
    
    def set_cancel_to_buffer(self, buffer):
        self._select_cancel_to_buffer = buffer
    
    def do_select(self):
        index, selection = self.get_selection()
        if index != -1:
            self._select_callback(selection)
            return True
        else:
            return False
            
    def get_selection(self):
        row = -1
        if self.is_select():
            row, _ = self._get_pos()
            row -= 1
        # end if
        return row, self._selections.get(row)
        
    def _get_pos(self):
        return self._top_row + self._cursory, self._lft_col + self._cursorx - self._marginx
    
    def _get_buffer_pos(self, cx=None, cy=None):
        row = self._top_row + (self._cursory if cy is None else cy)
        col = self._lft_col + (self._cursorx if cx is None else cx) - self._marginx
        
        if cx is None and cy is None:
            return row, col
            
        row = max(0, min(len(self._lines     ) - 1, row))
        col = max(0, min(len(self._lines[row]) - 1, col))
        
        return row, col
    
    def _get_window_pos(self, dx=0, dy=(0, 0), wrap=True):
        def get_cy(dy):
            dy1, dy2 = dy
            cy = self._cursory + dy1
            tr = self._top_row
            if cy > self._window.bottomy:
                tr = min(len(self._lines) - self._window.vsizeb, self._top_row + dy2)
                cy = self._window.bottomy
            elif cy < 0:
                tr = max(0, self._top_row + dy2)
                cy = self._marginy if tr == 0 else 0
            return cy, tr
            
        def get_cx(dx, cy=None):
            row, col = self._get_buffer_pos(cy=cy)
            line_len = len(self._lines[row])
            cx = self._cursorx + dx
            if cx > NCHARS - 1:
                n_available_cols = NCHARS - self._marginx - 1
                lc = min(line_len - n_available_cols, self._lft_col + dx)
                cx = NCHARS - 1
            elif cx < self._marginx:
                lc = max(0, self._lft_col + dx)
                cx = self._marginx
            else:
                cx = min(cx, len(self._lines[row]) + self._marginx)
                lc = self._lft_col
            return cx, lc
        
        def get_cx_wrap(dx):
            row, col = self._get_buffer_pos()
            line_len = len(self._lines[row])
            dy = 1 if dx > 0 else -1 # direction of wrapping in Y
            cy = self._cursory
            while col + dx > line_len or col + dx < 0:
                new_row, _ = self._get_buffer_pos(cy=cy + dy)
                if new_row == row: # no prev or next line to wrap to
                    dy = cy - self._cursory # delta lines we wrapped
                    cy, tr = get_cy(dy=(dy, dy))
                    cx, lc = get_cx(dx, cy)
                    return (cy, tr, cx, lc)
                # end if
                cy += dy
                row = new_row
                line_len = len(self._lines[row])
                if dx > 0:
                    dx = col + dx - line_len
                    col = 0
                else:
                    dx = dx + col + 1
                    col = line_len
            # end while
            dy = cy - self._cursory
            cy, tr = get_cy(dy=(dy, dy))
            cx, lc = get_cx(dx, cy)
            return (cy, tr, cx, lc)
            
        if dx != 0:
            if wrap:
                cy, tr, cx, lc = get_cx_wrap(dx)
            else:
                cy, tr = self._cursory, self._top_row
                cx, lc = get_cx(dx)
            # end if
        elif dy != (0, 0):
            cy, tr = get_cy(dy)
            cx, lc = get_cx(dx, cy)
        else:
            cy, tr, cx, lc = self._cursory, self._top_row, self._cursorx, self._lft_col
            
        return (cy, tr, cx, lc)
    
    def _update_dirty_state_to(self, state):
        if self._dirty != state and self._name != "*minibuffer*":
            self._dirty = state
            self._window.draw_status_bar(self)
            
    def restore_cursor(self):
        _move_cursor_to(self._tty_channel, self._window.screeny + self._cursory, self._cursorx)
        
    def draw_lines(self, starting_at=0):
        if self.is_visible():
            for i in range(starting_at, self._window.vsize - 1):
                _move_cursor_to(self._tty_channel, self._window.screeny + i, 0)
                _erase_end_of_line(self._tty_channel)
                try:
                    row = self._top_row + i
                    self._lines[row].write()
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
        row, _ = self._get_pos()
        if self._cursorx == self._marginx:
            if self._lft_col > 0:
                # scroll window right
                self._lft_col -= 1
                self.draw_lines()
                self.restore_cursor()
            elif row > self._marginy:
                self.prev_line_command()
                self.end_line_command()
        else:
            self._cursorx -= 1
            self.restore_cursor()
        
    def next_char_command(self):
        row, _ = self._get_pos()
        if self._lft_col + self._cursorx == len(self._lines[row]):
            if row < len(self._lines) - 1:
                self.begin_line_command()
                self.next_line_command()
            # end if
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
        if row > self._marginy:
            self._cursory -= 1
            if self._cursory < 0:
                for i in range(self._window.vsize // 2 - 1):
                    if self._top_row > 0:
                        self._top_row -= 1
                        self._window.scroll_down()
                        _move_cursor_to(self._tty_channel, self._window.screeny, 0)
                        # _write(self._tty_channel, self._lines[self._top_row][:NCHARS])
                        self._lines[self._top_row].write()
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
                        # _write(self._tty_channel, self._lines[row + i + 1][:NCHARS])
                        self._lines[row + i + 1].write()
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
            self._cursorx = self._marginx + n_visible_chars
        self.restore_cursor()
        
    def buffer_home_command(self):
        if self._top_row != 0 or self._lft_col != 0:
            self._top_row = 0
            self._lft_col = 0
            self.draw_lines()
        # end if
        self._cursorx = self._marginx
        self._cursory = self._marginy
        self.restore_cursor()
        
    def buffer_end_command(self):
        self._cursory = min(len(self._lines) - 1, self._window.vsize - 2)
        row, _ = self._get_pos()
        new_top_row = max(0, len(self._lines) - self._window.vsize + 1)
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
            # _write(self._tty_channel, self._lines[self._top_row + self._window.vsize - 2][:NCHARS])
            self._lines[self._top_row + self._window.vsize - 2].write()
            self._cursory = max(self._marginy, self._cursory - 1)
            self.restore_cursor()
    
    def scroll_down_command(self):
        if self._top_row != 0:
            self._top_row -= 1
            self._window.scroll_down()
            _move_cursor_to(self._tty_channel, self._window.screeny, 0)
            # _write(self._tty_channel, self._lines[self._top_row][:NCHARS])
            self._lines[self._top_row].write()
            self._cursory = min(self._window.vsize - 2, self._cursory + 1)
            self.restore_cursor()
    
    def insert_character(self, c):
        if self.is_readonly():
            return
            
        if c == LF: c = CR
        
        row, col = self._get_pos()
        try:
            self._lines[row] = self._lines[row][:col] + c + self._lines[row][col:]
        except:
            self._lines.append(BufferLine(self, c))
        # end try
        _erase_end_of_line(self._tty_channel)
        if c == CR:
            line_to_insert = self._lines[row][col + 1:]
            self._lines[row] = self._lines[row][:col]
            self._lines.append(BufferLine(self, line_to_insert))
            if self._cursory == self._window.screeny + self._window.vsize - 1:
                # scroll up
                pass
            else:
                self._cursory += 1
                if row + 1 < len(self._lines):
                    self._window.scroll_down(self._cursory)
                _move_cursor_to(self._tty_channel, self._window.screeny + self._cursory, 0)
                # _write(self._tty_channel, line_to_insert[:NCHARS])
                line_to_insert.write()
            # end if
            self._cursorx = self._marginx
        else:
            n = NCHARS - col
            # _write(self._tty_channel, self._lines[row][col:n])
            self._lines[row].write(col, self._cursorx)
            self._cursorx += 1
        # end if
        self._update_dirty_state_to(True)
        self.restore_cursor()
    
    def insert_textblock(self, char_list):
        if self.is_readonly():
            return
            
        row, col = self._get_pos()
        textblock = "".join(char_list)
        lines = textblock.split("\n")
        rest_of_line = self._lines[row][col:]
        line = lines.pop(0)
        lines_inserted = len(lines)
        self._lines[row] = self._lines[row][:col] + line
        while lines:
            row += 1
            line = lines.pop(0)
            self._lines.insert(row, BufferLine(self, line))
        # end while
        self._lines[row] += rest_of_line
        if lines_inserted > 0:
            self.draw_lines(starting_at=self._cursory)
            self._cursory = min(self._cursory + lines_inserted, self._window.vsize - 2)
        else:
            # _write(self._tty_channel, self._lines[row][col:NCHARS])
            self._lines[row].write(col, self._cursorx)
            self.end_line_command()
        
        self._update_dirty_state_to(True)
        self.restore_cursor()
        
    def delete_previous_character(self):
        if self.is_readonly():
            return
            
        row, col = self._get_pos()
        if col == 0:
            if row > self._marginy:
                # delete a CR and merge lines
                self.prev_line_command()
                self.end_line_command()
                self.delete_current_character()
        else:
            self._lines[row] = self._lines[row][:col-1] + self._lines[row][col:]
            self._cursorx -= 1
            self.restore_cursor()
            _erase_end_of_line(self._tty_channel)
            # _write(self._tty_channel, self._lines[row][col:NCHARS])
            self._lines[row].write(col, self._cursorx)
            self._update_dirty_state_to(True)
            self.restore_cursor()
    
    def delete_current_character(self):
        if self.is_readonly():
            return
            
        row, col = self._get_pos()
        if col == len(self._lines[row]):
            if row < len(self._lines):
                # delete a CR and merge lines
                line_to_merge = self._lines.pop(row + 1)
                self._lines[row] += line_to_merge
                # _write(self._tty_channel, self._lines[row][col:NCHARS])
                self._lines[row].write(col, self._cursorx)
                self._window.scroll_up(self._cursory + 1)
                if row + self._window.vsize - 1 < len(self._lines):
                    _move_cursor_to(self._tty_channel, self._window.screeny + self._window.vsize - 1, 0)
                    # _write(self._tty_channel, self._lines[row + self._window.vsize - 1][:NCHARS])
                    self._lines[row + self._window.vsize - 1].write()
                self._update_dirty_state_to(True)
                self.restore_cursor()
                return CR
        else:
            c = self._lines[row][col]
            self._lines[row] = self._lines[row][:col] + self._lines[row][col+1:]
            # _write(self._tty_channel, self._lines[row][col:NCHARS])
            self._lines[row].write(col, self._cursorx)
            if len(self._lines[row]) < NCHARS - 1:
                _erase_end_of_line(self._tty_channel)
            self._update_dirty_state_to(True)
            self.restore_cursor()
            return c
    
    def delete_to_line_end(self):
        if self.is_readonly():
            return
            
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
        self.has_status_bar = has_status_bar
        self.screeny = 0
        self.vsize = 0
        self.vsizeb = 0
        self.bottomy = 0
        self.visible = False
        
    def setup(self, screeny, vsize, visible=True):
        self.screeny = screeny
        self.vsize = vsize
        self.vsizeb = vsize - (1 if self.has_status_bar else 0)
        self.bottomy = self.vsizeb - 1
        self.visible = visible
    
    def show(self):
        self.visible = True
        
    def hide(self):
        self.visible = False
        
    def draw_status_bar(self, buffer):
        if self.has_status_bar:
            if buffer.is_select():
                mode_data = ["Selection"]
            else:
                mode_data = []
                if buffer.name().endswith(".py"):
                    mode_data.append("Python Mode")
                elif buffer.name().endswith(".pl1"):
                    mode_data.append("PL1 Mode")
                else:
                    mode_data.append("Fundamental Mode")
                # end if
                
                if buffer.is_readonly():
                    mode_data.append("Read Only")
                # end if
            # end if
            
            mode_string = ", ".join(mode_data)
            
            dirty_flag = "*" if buffer.is_modified() and not buffer.name().startswith("*scratch*") else ""
            status_bar_text = "    %s (%s) " % (dirty_flag + buffer.name(), mode_string)
            status_bar_text = "%-80s" % (status_bar_text)
            
            _move_cursor_to(self._tty_channel, self.screeny + self.vsize - 1, 0)
            _reverse_video(self._tty_channel)
            _write(self._tty_channel, status_bar_text)
            _normal_video(self._tty_channel)
    
    def scroll_up(self, starting_at=0):
        _set_scroll_range(self._tty_channel, self.screeny + starting_at, self.screeny + self.vsize - 2) # don't scroll the status bar
        _scroll_up(self._tty_channel)
        _set_scroll_range(self._tty_channel)
    
    def scroll_down(self, starting_at=0):
        _set_scroll_range(self._tty_channel, self.screeny + starting_at, self.screeny + self.vsize - 2) # don't scroll the status bar
        _scroll_down(self._tty_channel)
        _set_scroll_range(self._tty_channel)
    
class EmacsEditor(object):

    MAX_WINDOWS = 3
    
    def __init__(self, file_path_list):
        self.tty = get_calling_process_().tty()
        self._return_from_break = False
        self._cursorx = 0
        self._cursory = 0
        self._buffers = []
        self._windows = []
        self._yank_buffer = []
        self._killing = False
        
        dedicated_minibuffer_window = Window(self.tty, has_status_bar=False)
        dedicated_minibuffer_window.setup(NLINES - 1, 1)
        self._minibuffer = Buffer(self.tty, "*minibuffer*", dedicated_minibuffer_window)
        
        for i in range(self.MAX_WINDOWS):
            self._windows.append(Window(self.tty))
        # end for
        
        if not file_path_list:
            self._windows[0].setup(0, NLINES - 1)
            self.new_buffer("*scratch*", self._windows[0])
            
        else:
            file_path = parm()
            directory = parm()
            file_name = parm()
            code = parm()
            
            nbuffers = min(self.MAX_WINDOWS, len(file_path_list))
            wsize = (NLINES - 1) // nbuffers
            for i, path in enumerate(file_path_list):
                if i < len(self._windows):
                    w = self._windows[i]
                    w.setup(i * wsize, wsize)
                else:
                    w = None
                # end if
                
                b = self.new_buffer(window=w)
                
                call.sys_.get_abs_path(path, file_path)
                call.sys_.split_path_(file_path.val, directory, file_name)
                call.hcs_.fs_file_exists(directory.val, file_name.val, code)
                if code.val == 0:
                    b.load_file(file_path.val, self._next_name)
                else:
                    b.visit_file(file_path.val, self._next_name)
                # end if
            # end for
        # end if
        
        self._current_buffer = self._buffers[0]
        self._cancel_to_buffer = None
        self._minibuffer_callback = None
        self._minibuffer_kwargs = {}
        self._yes_no_callback = None
        self._yes_no_args = []
        self._yes_no_prompt = None
        
    def new_buffer(self, name="", window=None):
        if name:
            name = self._next_name(name)
        # end if
        b = Buffer(self.tty, name, window)
        self._buffers.append(b)
        return b
        
    def get_visible_buffers(self):
        return sorted([ buffer for buffer in self._buffers if buffer.is_visible() ], key=lambda buffer: buffer.window().screeny)
        
    def _next_name(self, name):
        basename, _, _ = name.partition(" ")
        
        highest = 0
        for buffer in self._buffers:
            bufname, _, nstr = buffer.name().partition(" ")
            if bufname == basename:
                highest = max(highest, int(nstr.strip("()") or 1))
            # end if
        # end for
        
        if highest == 0:
            return name
        else:
            return basename + " (%d)" % (highest + 1)
    
    def open(self):
        self.redraw()
        self.enter_command_loop()
        
    def redraw(self):
        _clear_screen(self.tty)
        for buffer in self._buffers:
            buffer.draw_lines()
        self._current_buffer.restore_cursor()
        
    def get_char(self):
        iox_control.echo_input_sw = False
        iox_control.enable_signals_sw = True
        iox_control.filter_chars = []
        buffer = parm()
        call.iox_.get_char(self.tty, iox_control, buffer)
        #== Special handling of arrow key escape codes. We don't want to
        #== treat them like normal Emacs ESC- commands, so filter them
        #== and convert them to an internal ARROW- command prefix.
        if buffer.val == ESC:
            next = parm()
            call.iox_.peek_char(self.tty, next)
            if next.val == 'O':
                #== Eat the 'O' byte and leave the byte indicating arrow direction still in the iox_ buffer
                call.iox_.get_char(self.tty, iox_control, next)
                buffer.val = ARR
            # end if
        # end if
        return buffer.val

    def enter_command_loop(self):
        ESC_prefix = False
        ARROW_prefix = False
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
                    
                elif ARROW_prefix:
                    ARROW_prefix = False
                    if c == 'A':
                        self.prev_line_command()
                    elif c == 'B':
                        self.next_line_command()
                    elif c == 'C':
                        self.next_char_command()
                    elif c == 'D':
                        self.prev_char_command()
                    else:
                        self.insert_character(c)
                        
                elif ESC_prefix:
                    ESC_prefix = False
                    _move_cursor_to(self.tty, NLINES - 1, 0)
                    _erase_end_of_line(self.tty)
                    
                    if c == 'v':
                        self.prev_page_command()
                    elif c == 'z':
                        self.scroll_down_command()
                    elif c == '<':
                        self.buffer_home_command()
                    elif c == '>':
                        self.buffer_end_command()
                    else:
                        self.set_status_message("ESC-" + _xlate(c) + " undefined")
                        
                    self._current_buffer.restore_cursor()
                    
                elif CTRLX_prefix:
                    CTRLX_prefix = False
                    _move_cursor_to(self.tty, NLINES - 1, 0)
                    _erase_end_of_line(self.tty)
                    
                    if c == CTRL('C'):
                        self.quit_command()
                        continue
                    elif c == CTRL('B'):
                        self.select_buffer_command()
                    elif c == CTRL('F'):
                        self.find_file_command()
                    elif c == CTRL('S'):
                        self.save_file_command()
                    elif c == CTRL('V'):
                        self.visit_file_command()
                    elif c == CTRL('W'):
                        self.write_file_command()
                    elif c == 'b':
                        self.swap_buffer_command()
                    elif c == 'k':
                        self.kill_buffer_command()
                    elif c == 'n' or c == 'o':
                        self.next_buffer_command()
                    elif c == 'p':
                        self.prev_buffer_command()
                    elif c == '1':
                        self.single_window_command()
                    elif c == '2':
                        self.split_window_command()
                    else:
                        self.set_status_message("^X-" + _xlate(c) + " undefined")
                        
                    self._current_buffer.restore_cursor()
                    
                elif self.process_minibuffer_input(c):
                    pass
                    
                elif c == ARR:
                    ARROW_prefix = True
                    
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
                    if self._current_buffer.is_select():
                        self._current_buffer.do_select()
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
                        self.cancel_minibuffer()
                    elif self._current_buffer.is_select():
                        self.close_selection_buffer()
                    self.set_status_message("Quit")
                elif c == CTRL('K'):
                    self.delete_to_line_end()
                elif c == CTRL('L'):
                    self.redraw_command()
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
                elif self._current_buffer != self._minibuffer:
                    self.set_status_message(_xlate(c) + " undefined")
            
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
    
    def minibuffer_command(self, prompt, callback, **kwargs):
        self._cancel_to_buffer = self._current_buffer
        self._current_buffer = self._minibuffer
        self._minibuffer_input_fn = kwargs.pop('special_input_fn', None)
        self._minibuffer_callback = callback
        self._minibuffer_kwargs = kwargs
        self._minibuffer.set_special_prompt(prompt + ": ")
    
    def minibuffer_yes_no(self, prompt, callback, *args):
        self._yes_no_prompt = prompt
        self._yes_no_callback = callback
        self._yes_no_args = args
        self.minibuffer_command(prompt + " (Y/N)", self._yes_no_handler)
    
    def cancel_minibuffer(self):
        if self._cancel_to_buffer:
            self._current_buffer = self._cancel_to_buffer
            self._current_buffer.restore_cursor()
            self._cancel_to_buffer = None
    
    def process_minibuffer_input(self, c):
        if self._current_buffer == self._minibuffer:
            if c in [CR, LF]:
                s = self._minibuffer.get_contents().strip()
                if s:
                    self._minibuffer.clear_contents()
                    self._minibuffer.set_special_prompt("")
                    callback = self._minibuffer_callback
                    kwargs = self._minibuffer_kwargs
                    self._minibuffer_callback = None
                    self._minibuffer_kwargs = {}
                    self.cancel_minibuffer()
                    callback(s, **kwargs)
                # end if
                return Character_Handled
                
            elif self._minibuffer_input_fn:
                return self._minibuffer_input_fn(c)
            # end if
        # end if
        return not Character_Handled
        
    def _yes_no_handler(self, answer):
        if answer.lower() in ["yes", "y"]:
            self._yes_no_callback(*self._yes_no_args)
        elif answer.lower() in ["no", "n"]:
            self._current_buffer.restore_cursor()
        else:
            #== Reassert the existing prompt, callback, and arg
            self.minibuffer_yes_no(self._yes_no_prompt, self._yes_no_callback, *self._yes_no_args)
        
    def autocomplete(self, prefix, choices):
        candidates = sorted([ choice for choice in choices if choice.startswith(prefix) ], key=len)
        if candidates:
            clist = map(lambda s: s.pop(), filter(lambda s: len(s) == 1, [ set([ item[i] for item in candidates ]) for i in range(len(candidates[0])) ]))
            return "".join(clist)[len(prefix):]
        else:
            return ""
        
    def open_selection_buffer(self, name, title, selection_list, entry_list, selection_callback):
        for buffer in self._buffers:
            if buffer.name() == name:
                selection_buffer = buffer
                break
            # end if
        else:
            selection_buffer = self.new_buffer(name)
        # end for
        
        if selection_buffer.is_visible():
            #== If the selection buffer is already visible, then just make sure
            #== self._current_buffer refers to it.
            self._current_buffer = selection_buffer
        else:
            visible_buffers = self.get_visible_buffers()
            if len(visible_buffers) == 1:
                selection_buffer.set_cancel_to_buffer(None)
                self.split_window_command(selection_buffer)
                self._current_buffer = selection_buffer
            else:
                self._current_buffer = visible_buffers[-1]
                selection_buffer.set_cancel_to_buffer(self._current_buffer)
                self._swap_to_buffer(selection_buffer.name())
            # end if
        # end if
        selection_buffer.set_selections(title, selection_list, entry_list, selection_callback)
        
        self._current_buffer.restore_cursor()
    
    def close_selection_buffer(self):
        if self._current_buffer.is_select():
            cancel_to = self._current_buffer.cancel_to()
            if cancel_to:
                self._swap_to_buffer(cancel_to.name())
            else:
                cur_window = self._current_buffer.window()
                cur_window.hide()
                self._current_buffer.set_window(None)
                
                visible_buffers = self.get_visible_buffers()
                
                screeny = 0
                vsize = (NLINES - 1) // len(visible_buffers)
                for buffer in visible_buffers:
                    buffer.window().setup(screeny, vsize)
                    buffer.draw_lines()
                    screeny += vsize
                # end for
                
                self._current_buffer = visible_buffers[0]
    
    def quit_command(self):
        if any([ buffer.is_modified() for buffer in self._buffers ]):
            self.minibuffer_yes_no("Modified buffers exist. Quit anyway?", self._set_done_flag, True)
        else:
            self._set_done_flag(True)
            
    def _set_done_flag(self, flag):
        self.done = flag
        _clear_screen(self.tty)
        
    def visit_file_command(self):
        self.minibuffer_command("Visit file", self._load_file_into_buffer, create_new=True, special_input_fn=self._find_file_input)
        
    def find_file_command(self):
        self.minibuffer_command("Find file", self._load_file_into_buffer, special_input_fn=self._find_file_input)
        
    def _load_file_into_buffer(self, filename, create_new=False):
        file_path = parm()
        directory = parm()
        file_name = parm()
        code      = parm()
        
        call.sys_.get_abs_path(filename, file_path)
        call.sys_.split_path_(file_path.val, directory, file_name)
        
        if _is_directory(file_path.val):
            # self.set_status_message("Can't load file. %s is a directory." % (filename))
            self.open_dired_buffer(file_path.val)
            return
        # end if
        
        for buffer in self._buffers:
            if buffer.filepath() == file_path.val:
                self._swap_to_buffer(file_name.val)
                return
            # end if
        # end for
        
        call.hcs_.fs_file_exists(directory.val, file_name.val, code)
        if code.val == 0 or create_new:
            cur_window = self._current_buffer.window()
            self._current_buffer.set_window(None)
            self._current_buffer = self.new_buffer(window=cur_window)
        # end if
        
        if code.val == 0:
            self._current_buffer.load_file(file_path.val, name_resolver=self._next_name)
            self._current_buffer.draw_lines()
        elif create_new:
            self._current_buffer.visit_file(file_path.val, name_resolver=self._next_name)
            self._current_buffer.draw_lines()
        else:
            self.set_status_message("Could not find file %s." % (file_path.val))
        # end if
        
        self._current_buffer.restore_cursor()
    
    def _find_file_input(self, c):
        if c == '?' and self._current_buffer.get_contents().strip() == "":
            self._minibuffer.set_special_prompt("")
            self.cancel_minibuffer()
            self.open_dired_buffer(get_wdir_())
            return Character_Handled
        elif c == TAB and self._current_buffer.get_contents().strip() != "":
            # auto-complete buffer name
            return Character_Handled
        else:
            return not Character_Handled
    
    def open_dired_buffer(self, dir_name):
        EXCLUDED_EXTENSIONS = (".pyc", ".pyo")
        
        full_path   = parm()
        directory   = parm()
        parent_dir  = parm()
        branch      = parm()
        segment     = parm()
        code        = parm()
        entry_list  = []
        select_list = []
        
        call.sys_.get_abs_path(dir_name, full_path)
        if full_path.val != ">":
            call.sys_.split_path_(full_path.val, directory, null())
            call.sys_.split_path_(directory.val, null(), parent_dir)
            entry_list.append(directory.val)
            select_list.append(_bold(" < " + parent_dir.val))
        # end if
        
        call.hcs_.get_directory_contents(dir_name, branch, segment, code)
        for directory in branch.list:
            entry_list.append(dir_name + ">" + directory)
            select_list.append(_bold(" > " + directory))
        # end for
        for filename in segment.list:
            if not filename.endswith(EXCLUDED_EXTENSIONS):
                entry_list.append(dir_name + ">" + filename)
                select_list.append(" : " + filename)
            # end if
        # end for
        
        self.open_selection_buffer("*dir-ed*", "Contents of %s:" % (dir_name), select_list, entry_list, self._load_file_into_buffer)
    
    def kill_buffer_command(self):
        if self._current_buffer.is_modified():
            self.minibuffer_yes_no("Modified buffer not saved. Kill anyway?", self._kill_buffer)
        else:
            self._kill_buffer()
        
    def _kill_buffer(self, *args):
        #== If the current buffer is an unsaved scratch buffer, then just clear it out
        if self._current_buffer.name().startswith("*scratch*"):
            self._current_buffer.clear(self._current_buffer.name())
            return
        elif self._current_buffer.is_select():
            self.close_selection_buffer()
            return
        # end if
        
        cur_window = self._current_buffer.window()
        
        switch_to = None
        for buffer in self._buffers[:]:
            if buffer is self._current_buffer:
                self._buffers.remove(buffer)
            elif not buffer.is_visible():
                switch_to = buffer
            # end if
        # end for
        
        if not switch_to:
            switch_to = self.new_buffer("*scratch*", cur_window)
        else:
            switch_to.set_window(cur_window)
        # end if
        
        self._current_buffer = switch_to
        self._current_buffer.draw_lines()
        self._current_buffer.restore_cursor()
        
    def save_file_command(self):
        if self._current_buffer.is_readonly():
            self.set_status_message("File is read-only.")
        elif not self._current_buffer.filepath():
            self.minibuffer_command("Save file", self._save_file_as)
        else:
            self.save_current_buffer()
        
    def _save_file_as(self, filename):
        file_path = parm()
        directory = parm()
        file_name = parm()
        code      = parm()
        
        call.hcs_.fs_valid_name(filename, code)
        if code.val != 0:
            self.set_status_message("Invalid file name %s." % (filename))
            return
        # end if
        
        call.sys_.get_abs_path(filename, file_path)
        call.sys_.split_path_(file_path.val, directory, file_name)
        call.hcs_.fs_file_exists(directory.val, file_name.val, code)
        if code.val == 0:
            if _is_directory(file_path.val):
                self.set_status_message("Can't write file. %s is a directory." % (file_name.val))
            else:
                self.minibuffer_yes_no("File already exists. Overwrite?", self._save_buffer_to_file, file_path.val)
            # end if
        else:
            self._save_buffer_to_file(file_path.val)
            
    def _save_buffer_to_file(self, filepath):
        if _is_readonly_file(filepath):
            self.set_status_message("File is read-only.")
        else:
            self._current_buffer.set_file_path(filepath, name_resolver=self._next_name)
            self.save_current_buffer()
            self._current_buffer.restore_cursor()
    
    def save_current_buffer(self):
        self._current_buffer.save_file()
        self.set_status_message("File %s saved." % (self._current_buffer.filepath()))
    
    def write_file_command(self):
        self.minibuffer_command("Write file", self._save_file_as)
    
    def swap_buffer_command(self):
        self.minibuffer_command("Swap to buffer", self._swap_to_buffer, special_input_fn=self._swap_buffer_input)
        
    def select_buffer_command(self):
        buffer_list = []
        select_list = []
        select_line = parm()
        
        for buffer in self._buffers:
            #== Don't put any selection buffer on the list.
            if not buffer.is_select():
                buffer_list.append(buffer.name())
                call.ioa_.rsnnl("^[ *^;  ^]^20a^a", select_line, buffer.is_modified(), buffer.name(), buffer.filepath())
                select_list.append(select_line.val)
            # end if
        # end for
        
        self.open_selection_buffer("*buffers*", "Select a buffer:", select_list, buffer_list, self._swap_to_buffer)
    
    def _swap_to_buffer(self, buffer_name):
        buffer1 = self._current_buffer
        window1 = self._current_buffer.window()
        
        for buffer in self._buffers:
            if buffer.name() == buffer_name:
                buffer2 = buffer
                window2 = buffer.window()
                
                if not buffer.is_visible():
                    buffer1.set_window(window2)
                    buffer2.set_window(window1)
                    
                    buffer1.draw_lines()
                    buffer2.draw_lines()
                    
                elif buffer1.is_select():
                    self.close_selection_buffer()
                # end if
                
                self._current_buffer = buffer2
                break
            # end if
        else:
            self.set_status_message("No buffer named %s." % (buffer_name))
        # end for
        
        self._current_buffer.restore_cursor()
    
    def _swap_buffer_input(self, c):
        if c == '?' and self._current_buffer.get_contents().strip() == "":
            self._minibuffer.set_special_prompt("")
            self.select_buffer_command()
            return Character_Handled
        elif c == TAB and self._current_buffer.get_contents().strip() != "":
            # auto-complete buffer name
            choices = [ buffer.name() for buffer in self._buffers if not buffer.is_select() ]
            added_chars = self.autocomplete(self._current_buffer.get_contents(), choices)
            self._current_buffer.insert_textblock(added_chars)
            return Character_Handled
        else:
            return not Character_Handled
    
    def redraw_command(self):
        self.redraw()
        
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
        visible_buffers = self.get_visible_buffers()
        index = visible_buffers.index(self._current_buffer)
        index = (index - 1) % len(visible_buffers)
        self._current_buffer = visible_buffers[index]
        
    def next_buffer_command(self):
        visible_buffers = self.get_visible_buffers()
        index = visible_buffers.index(self._current_buffer)
        index = (index + 1) % len(visible_buffers)
        self._current_buffer = visible_buffers[index]
        
    def single_window_command(self):
        for buffer in self._buffers:
            if buffer is not self._current_buffer and buffer.is_visible():
                buffer.window().hide()
            # end if
        # end for
        self._current_buffer.window().setup(0, NLINES - 1)
        self._current_buffer.draw_lines()
        
    def split_window_command(self, new_buffer=None):
        for window in self._windows:
            if not window.visible:
                window_to_use = window
                break
            # end if
        else:
            return
        # end for
        
        for buffer in self._buffers:
            if buffer.window() is window_to_use:
                buffer.set_window(None)
            # end if
        # end for
        
        if new_buffer:
            new_buffer.set_window(window_to_use)
        else:
            new_buffer = self.new_buffer("*scratch*", window_to_use)
        # end if
        
        visible_windows = [ w for w in self._windows if w.visible ]
        visible_windows.insert(visible_windows.index(self._current_buffer.window()) + 1, window_to_use)
        
        screeny = 0
        vsize = (NLINES - 1) // len(visible_windows)
        for w in visible_windows:
            w.setup(screeny, vsize)
            screeny += vsize
        # end for
        
        for buffer in self._buffers:
            buffer.draw_lines()
        
def emacs():
    arg_list = parm()
    call.cu_.arg_list(arg_list)
    
    editor = EmacsEditor(arg_list.args)
    editor.open()
    