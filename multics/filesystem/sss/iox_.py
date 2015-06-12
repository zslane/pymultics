
from multics.globals import *
from iox_control import *

BACKSPACE = chr(8)

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
        
    def _fetchbyte(self, tty_channel, ioxctl):
        process = None
        if ioxctl.enable_signals_sw:
            process = get_calling_process_()
        self.supervisor.check_conditions(tty_channel, process)
        
        if not self._buffer:
            input_data = self.hardware.io.get_input(tty_channel) or ""
            self._buffer = filter(lambda c: c not in ioxctl.filter_chars, list(input_data)) or [""]
        
        c = self._buffer.pop(0)
        if c and ioxctl.echo_input_sw:
            self.put_chars(tty_channel, c)
            
        return c
        
    def get_char(self, tty_channel, ioxctl, buffer):
        buffer.val = self._fetchbyte(tty_channel, ioxctl)
    
    def wait_get_char(self, tty_channel, ioxctl, buffer):
        buffer.val = ""
        while not buffer.val:
            buffer.val = self._fetchbyte(tty_channel, ioxctl)
        
    def peek_char(self, tty_channel, buffer):
        buffer.val = self.hardware.io.peek_input(tty_channel) or ""
            
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
            c = self._fetchbyte(tty_channel, ioxctl)
            if c == '\r' or c == '\n':
                buffer.val = self.inline_edit_(buf)
                return
            elif c == BACKSPACE:
                buf = buf[:-1]
            elif c:
                buf += c
            # end if
        # end while
        self._buffer = buf
        buffer.val = ""
    
    def wait_get_line(self, tty_channel, ioxctl, buffer):
        buf = ""
        while True:
            c = self._fetchbyte(tty_channel, ioxctl)
            if c == '\r' or c == '\n':
                buffer.val = self.inline_edit_(buf)
                return
            elif c == BACKSPACE:
                buf = buf[:-1]
            elif c:
                buf += c
    
    def put_chars(self, tty_channel, s):
        self.hardware.io.put_output(s, tty_channel)
        
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
