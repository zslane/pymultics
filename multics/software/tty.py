import re

from PySide import QtCore, QtGui, QtNetwork

CONTROL_CODE       = chr(17) # Device Control 1
UNKNOWN_CODE       = chr(0)
ECHO_NORMAL_CODE   = chr(1)
ECHO_PASSWORD_CODE = chr(2)
ASSIGN_PORT_CODE   = chr(26) # Substitute
END_CONTROL_CODE   = chr(4)  # End of Transmission

LINEFEED_CODE      = chr(10) # Linefeed
BREAK_CODE         = chr(24) # Cancel

class TTYChannel(QtCore.QObject):
    def __init__(self, socket, parent=None):
        super(TTYChannel, self).__init__(parent)
        
        self.__input_buffer = []
        self.__linefeed = False
        self.__break_signal = False
        self.__closed_signal = False
        
        self.__socket = socket
        self.__socket.disconnected.connect(self.disconnect)
        self.__socket.readyRead.connect(self.data_available)
        self.__socket.error.connect(self.socket_error)
        
        self.__socket_error = None
        
    #== PROPERTIES ==#
    
    @property
    def id(self):
        #== A tty channel id is just the socket port number that is being used
        #== for data communications with the terminal at the other end
        return self.__socket.localPort()
    
    @property
    def error_code(self):
        return self.__socket_error
        
    @property
    def error_string(self):
        return self.__socket.errorString()
        
    #== SOCKET ACTIVITY SLOTS ==#
    
    @QtCore.Slot()
    def disconnect(self):
        pass
        
    @QtCore.Slot()
    def data_available(self):
        data_packet = DataPacket(self.__socket.readAll())
        while not data_packet.is_empty():
            if data_packet.is_control_seq():
                data_code, payload = data_packet.extract_control_data()
                if data_code == LINEFEED_CODE:
                    print "tty", self.id, "received LINEFEED"
                    self.__linefeed = True
                elif data_code == BREAK_CODE:
                    print "tty", self.id, "received BREAK"
                    self.__linefeed = False
                    self.__break_signal = True
                else:
                    raise ValueError("unknown control data code %d received" % (ord(data_code)))
                # end if
            else:
                s = data_packet.extract_plain_data().strip()
                print "tty", self.id, "received", repr(s)
                self.__linefeed = False
                self.__input_buffer.append(s)
    
    @QtCore.Slot("QAbstractSocket.SocketError")
    def socket_error(self, error):
        self.__socket_error = error
        
    #== CLIENT INTERFACE ==#
    
    def moveToThread(self, thread):
        self.__socket.moveToThread(thread)
        super(TTYChannel, self).moveToThread(thread)
    
    def linefeed_received(self):
        flag, self.__linefeed = self.__linefeed, False
        return flag
        
    def break_received(self):
        flag, self.__break_signal = self.__break_signal, False
        return flag
        
    def terminal_closed(self):
        return not (self.__socket.isValid() and self.__socket.state() == QtNetwork.QAbstractSocket.ConnectedState)
        
    def has_input(self):
        return self.__input_buffer != []

    def get_input(self):
        try:
            return self.__input_buffer.pop(0)
        except:
            return None
    
    def flush_input(self):
        if not self.terminal_closed():
            while self.__socket.bytesAvailable() > 0:
                self.__socket.readAll() # and discard
            # end while
        # end if
        self.__input_buffer = []
        self.__break_signal = False
        self.__linefeed = False
        
    def set_input_mode(self, mode):
        if not self.terminal_closed():
            if mode == QtGui.QLineEdit.Normal:
                print "Sending ECHO_NORMAL_CODE out tty channel", self.id
                mode_code = ECHO_NORMAL_CODE
            elif mode == QtGui.QLineEdit.Password:
                print "Sending ECHO_PASSWORD_CODE out tty channel", self.id
                mode_code = ECHO_PASSWORD_CODE
            else:
                mode_code = UNKNOWN_CODE
            # end if
            self.__socket.write(QtCore.QByteArray(CONTROL_CODE + mode_code + END_CONTROL_CODE))
            if not self.__socket.waitForBytesWritten(3000):
                print self.ME, "failed sending new input mode to tty channel id", self.id
                self.disconnect()
        
    def put_output(self, s):
        if not self.terminal_closed():
            print "Sending string out tty channel", self.id
            print s
            self.__socket.write(QtCore.QByteArray(s))
            
    def disconnect(self):
        pass
        
#-- end class TTYChannel

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

#-- end class DataPacket
