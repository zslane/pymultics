
from multics.globals import *
from iox_control import *

BS = chr(8)
LF = chr(10)
CR = chr(13)
ESC = chr(27)

def _is_cc(c):
    return 0 <= ord(c) <= 31

def _xlate_cc(c):
    if _is_cc(c) and (c not in [BS, LF, CR, ESC]):
        # return "^" + chr(ord(c) + ord('@'))
        return r"\%03o" % ord(c)
    else:
        return c
        
class iox_(Subroutine):
    def __init__(self):
        super(iox_, self).__init__(self.__class__.__name__)
        self._buffer = {}
        
    @property
    def hardware(self):
        return GlobalEnvironment.hardware
        
    @property
    def supervisor(self):
        return GlobalEnvironment.supervisor
        
    @property
    def user_io(self):
        return get_calling_process_().tty()
    @property
    def user_input(self):
        return get_calling_process_().tty()
    @property
    def user_output(self):
        return get_calling_process_().tty()
        
    def _fetchbyte(self, tty_channel, ioxctl, ioxbuffer=None):
        self.supervisor.check_conditions(tty_channel, get_calling_process_())
        
        #== Add the next available byte to the end of the internal buffer
        self._buffer.setdefault(tty_channel, "")
        c = self.hardware.io.get_input(tty_channel)
        c = c if c and c not in ioxctl.filter_chars else ""
        self._buffer[tty_channel] += c
        
        #== Pop the next available byte from the front of the internal buffer
        try:
            c = self._buffer[tty_channel][0]
            self._buffer[tty_channel] = self._buffer[tty_channel][1:]
        except:
            c = ""
        # end try
        
        if c and ioxctl.echo_input_sw:
            if c == BS:
                if ioxbuffer:
                    n = 4 if _is_cc(ioxbuffer[-1]) else 1
                    self.write(tty_channel, (BS * n) + (' ' * n) + (BS * n))
            else:
                self.write(tty_channel, _xlate_cc(c))
            
        return c
        
    def _xlate_string(self, s):
        return "".join([ _xlate_cc(c) if _is_cc(c) else c for c in s ])
        
    def get_char(self, tty_channel, ioxctl, buffer):
        buffer.val = self._fetchbyte(tty_channel, ioxctl)
    
    def wait_get_char(self, tty_channel, ioxctl, buffer):
        buffer.val = ""
        while not buffer.val:
            buffer.val = self._fetchbyte(tty_channel, ioxctl)
        
    def get_chars(self, iocb, buffer, n, n_read, code):
        tty_channel = iocb
        ioxctl = iox_control_structure()
        ioxctl.echo_input_sw = True
        
        buffer.val = ""
        while len(buffer.val) < n:
            buffer.val += self._fetchbyte(tty_channel, ioxctl)
        # end while
        n_read.val = n
        code.val = 0
        
    def peek_char(self, tty_channel, buffer):
        try:
            buffer.val = self._buffer[tty_channel][0]
        except:
            buffer.val = self.hardware.io.peek_input(tty_channel) or ""
        
    def xlate_(self, inb, outb):
        outb.val = self._xlate_string(inb)
        
    def inline_edit_(self, s):
        result = []
        escape_next = False
        for c in s:
            if c == "\\" and not escape_next:
                escape_next = True
                continue
            elif c == "#" and not escape_next and result:
                result.pop()
            elif c == "@" and not escape_next:
                result = []
            elif escape_next:
                result.append("\\" + c)
            else:
                result.append(c)
            escape_next = False
        # end for
        return "".join(result)
    
    def get_line(self, tty_channel, ioxctl, buffer):
        buf = ""
        while self.hardware.io.has_input(tty_channel):
            c = self._fetchbyte(tty_channel, ioxctl, buf)
            if c == CR or c == LF:
                self._buffer[tty_channel] = ""
                buffer.val = self.inline_edit_(buf)
                return
            elif c == BS:
                buf = buf[:-1]
            elif c:
                buf += c
            # end if
        # end while
        
        #== If we run out of characters to retrieve from the tty channel
        #== then just stuff what we have so far back into the line buffer
        #== and return an empty string
        self._buffer[tty_channel] = list(buf)
        buffer.val = ""
    
    def wait_get_line(self, tty_channel, ioxctl, buffer):
        buf = ""
        while True:
            c = self._fetchbyte(tty_channel, ioxctl, buf)
            if c == CR or c == LF:
                self._buffer[tty_channel] = ""
                buffer.val = self.inline_edit_(buf)
                return
            elif c == BS:
                buf = buf[:-1]
            elif c:
                buf += c
    
    def _has_line_input(self, tty_channel):
        return set([CR, LF]) <= set(self._buffer.get(tty_channel) or "")
        
    def _filter_line_endings(self, in_s):
        #== Get these from the process data stack (set by the set_tty command) someday!
        crecho = True
        lfecho = True
        
        hold_for_LF = False
        hold_for_CR = False
        out_s = ""
        for c in in_s:
            if hold_for_LF:
                hold_for_LF = (c == CR)
                out_s += (CR+LF)
                if c not in [CR, LF]:
                    out_s += c
                # end if
            elif hold_for_CR:
                hold_for_CR = (c == LF)
                out_s += (CR+LF)
                if c not in [CR, LF]:
                    out_s += c
                # end if
            elif c == CR and lfecho:
                hold_for_LF = True
            elif c == LF and crecho:
                hold_for_CR = True
            else:
                out_s += c
            # end if
        # end for
        if hold_for_LF or hold_for_CR:
            out_s += (CR+LF)
        # end if
        
        return out_s
    
    def write(self, tty_channel, s):
        self.hardware.io.put_output(self._xlate_string(self._filter_line_endings(s)), tty_channel)
        
    def terminal_closed(self, tty_channel):
        return self.hardware.io.terminal_closed(tty_channel)
        
    def break_received(self, tty_channel):
        return self.hardware.io.break_received(tty_channel)
        
    def has_input(self, tty_channel):
        return self._has_line_input(tty_channel) or self.hardware.io.has_input(tty_channel)
        
    def flush_input(self, tty_channel):
        self.hardware.io.flush_input(tty_channel)
        self._buffer[tty_channel] = ""
        
    def set_input_mode(self, tty_channel, mode):
        self.hardware.io.set_input_mode(mode, tty_channel)
        
    def disconnect_tty(self, tty_channel):
        self.hardware.io.disconnect_tty(tty_channel)
