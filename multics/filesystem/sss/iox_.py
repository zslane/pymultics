
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
        return "^" + chr(ord(c) + ord('@'))
    else:
        return c
        
class iox_(Subroutine):
    def __init__(self):
        super(iox_, self).__init__(self.__class__.__name__)
        self._buffer = []
        
    @property
    def hardware(self):
        return GlobalEnvironment.hardware
        
    @property
    def supervisor(self):
        return GlobalEnvironment.supervisor
        
    def _fetchbyte(self, tty_channel, ioxctl, ioxbuffer=None):
        process = None
        if ioxctl.enable_signals_sw:
            process = get_calling_process_()
        self.supervisor.check_conditions(tty_channel, process)
        
        if not self._buffer:
            input_data = self.hardware.io.get_input(tty_channel) or ""
            self._buffer = filter(lambda c: c not in ioxctl.filter_chars, list(input_data)) or [""]
        
        c = self._buffer.pop(0)
        if c and ioxctl.echo_input_sw:
            if c == BS:
                if ioxbuffer:
                    self.write(tty_channel, BS)
                    if _is_cc(ioxbuffer[-1]):
                        self.write(tty_channel, BS) # send out a second backspace char to remove the '^'
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
        
    def peek_char(self, tty_channel, buffer):
        try:
            buffer.val = self._buffer[0]
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
            else:
                result.append(c)
            escape_next = False
        # end for
        return "".join(result)
    
    def get_line(self, tty_channel, ioxctl, buffer):
        buf = ""
        while self.has_input(tty_channel):
            c = self._fetchbyte(tty_channel, ioxctl, buf)
            if c == CR or c == LF:
                buffer.val = self.inline_edit_(buf)
                return
            elif c == BS:
                buf = buf[:-1]
            elif c:
                buf += c
            # end if
        # end while
        self._buffer += list(buf)
        buffer.val = ""
    
    def wait_get_line(self, tty_channel, ioxctl, buffer):
        buf = ""
        while True:
            c = self._fetchbyte(tty_channel, ioxctl, buf)
            if c == CR or c == LF:
                buffer.val = self.inline_edit_(buf)
                return
            elif c == BS:
                buf = buf[:-1]
            elif c:
                buf += c
    
    def write(self, tty_channel, s):
        self.hardware.io.put_output(self._xlate_string(s), tty_channel)
        
    def terminal_closed(self, tty_channel):
        return self.hardware.io.terminal_closed(tty_channel)
        
    def break_received(self, tty_channel):
        return self.hardware.io.break_received(tty_channel)
        
    def has_input(self, tty_channel):
        return self._buffer or self.hardware.io.has_input(tty_channel)
        
    def flush_input(self, tty_channel):
        self.hardware.io.flush_input(tty_channel)
        self._buffer = []
        
    def set_input_mode(self, tty_channel, mode):
        self.hardware.io.set_input_mode(mode, tty_channel)
        
    def disconnect_tty(self, tty_channel):
        self.hardware.io.disconnect_tty(tty_channel)
