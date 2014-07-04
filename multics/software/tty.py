import re

from ..globals import *

from PySide import QtCore, QtGui, QtNetwork

CONTROL_CODE       = chr(17) # Device Control 1
UNKNOWN_CODE       = chr(0)  # Null
ECHO_NORMAL_CODE   = chr(1)
ECHO_PASSWORD_CODE = chr(2)
ASSIGN_PORT_CODE   = chr(26) # Substitute
END_CONTROL_CODE   = chr(4)  # End of Transmission

LINEFEED_CODE      = chr(10) # Linefeed
BREAK_CODE         = chr(24) # Cancel

class TTYChannel(QtCore.QObject):
    
    def __init__(self, socket, parent=None):
        super(TTYChannel, self).__init__(parent)
        self.setObjectName("tty_channel_%d" % (socket.localPort()))
        
        self.__input_buffer = []
        self.__linefeed = False
        self.__break_signal = False
        self.__closed_signal = False
        self.__origin_thread = QtCore.QThread.currentThread()
        
        self.__socket = socket
        self.__socket.setParent(None)
        self.__socket.disconnected.connect(self.disconnect)
        self.__socket.readyRead.connect(self.data_available)
        self.__socket.error.connect(self.socket_error)
        
        self.__socket_error = None
        #== A tty channel id is just the socket port number that is being used
        #== for data communications with the terminal at the other end
        self.__id = self.__socket.localPort()
        
    #== PROPERTIES ==#
    
    @property
    def id(self):
        return self.__id
    
    @property
    def error_code(self):
        return self.__socket_error
        
    @property
    def error_string(self):
        return self.__socket.errorString()
        
    #== SOCKET ACTIVITY SLOTS ==#
    
    @QtCore.Slot()
    def disconnect(self):
        self.__socket.close()
        
    @QtCore.Slot()
    def data_available(self):
        # print "TTYChannel.data_available for", get_calling_process_().objectName()
        data_packet = DataPacket.In(self.__socket.readAll())
        while not data_packet.is_empty():
            if data_packet.is_control_seq():
                data_code, payload = data_packet.extract_control_data()
                
                if data_code == LINEFEED_CODE:
                    # print "tty", self.id, "received LINEFEED"
                    self.__linefeed = True
                    
                elif data_code == BREAK_CODE:
                    # print "tty", self.id, "received BREAK"
                    self.__linefeed = False
                    self.__break_signal = True
                    
                else:
                    raise ValueError("unknown control data code %d received" % (ord(data_code)))
                # end if
                
            else:
                s = data_packet.extract_plain_data().strip()
                # print "tty", self.id, "received", repr(s),
                self.__linefeed = False
                self.__input_buffer.append(s)
    
    @QtCore.Slot("QAbstractSocket.SocketError")
    def socket_error(self, error):
        self.__socket_error = error
        
    def detach_from_process(self):
        print get_calling_process_().objectName() + " detaching tty channel to " + self.__origin_thread.objectName()
        self.moveToThread(self.__origin_thread)
        
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
                # print "Sending ECHO_NORMAL_CODE out tty channel", self.id
                mode_code = ECHO_NORMAL_CODE
            elif mode == QtGui.QLineEdit.Password:
                # print "Sending ECHO_PASSWORD_CODE out tty channel", self.id
                mode_code = ECHO_PASSWORD_CODE
            else:
                mode_code = UNKNOWN_CODE
            # end if
            self.__socket.write(DataPacket.Out(mode_code))
            self.__socket.flush()
            # if not self.__socket.waitForBytesWritten(3000):
                # print "Failed sending new input mode to tty channel id " + str(self.id)
                # self.disconnect()
        
    def put_output(self, s):
        if not self.terminal_closed():
            # print "Sending string out tty channel", self.id
            # print s
            self.__socket.write(QtCore.QByteArray(s))
            self.__socket.flush()
        
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
    
    @staticmethod
    def In(byte_array):
        return DataPacket(byte_array)
        
    @staticmethod
    def Out(data_code, payload=""):
        if data_code[0] < chr(32) and data_code[0] != '\r': # control codes are all less than ASCII value 32
            # print "DataPacket.Out(CONTROL_CODE + chr(%d) + %s + END_CONTROL_CODE)" % (ord(data_code[0]), repr(payload))
            return QtCore.QByteArray(CONTROL_CODE + data_code + str(payload) + END_CONTROL_CODE)
        else:
            # print "DataPacket.Out(%s)" % (repr(data_code))
            return QtCore.QByteArray(data_code)
    
#-- end class DataPacket
