import re
import sys
import telnetlib
from telnetlib import *

from PySide import QtCore, QtNetwork

UNKNOWN_CODE       = chr(0)
CONTROL_CODE       = chr(128)
ECHO_NORMAL_CODE   = chr(129)
ECHO_PASSWORD_CODE = chr(130)
ASSIGN_PORT_CODE   = chr(131)
WHO_CODE           = chr(132)
BREAK_CODE         = chr(133)
END_CONTROL_CODE   = chr(254)

class Thread(QtCore.QThread):
    """
    The worker object passed to the Thread() constructor must have the following:
        a. A start() slot/method that starts execution of the worker
        b. A stop() slot/method that stops/aborts execution of the worker
        c. A finished signal that is emitted when the worker is done
    """
    def __init__(thread, worker, name=""):
        #== Note that 'thread' is being used here instead of the usual 'self'
        super(Thread, thread).__init__()
        thread.worker = worker
        thread.ident = id(thread)
        thread.name = name or "Thread.%d" % (thread.ident)
        #== Set Qt object names for thread and worker objects
        thread.setObjectName(thread.name + ".Object")
        worker.setObjectName(thread.name + ".Worker")
        #== Move the worker object to the new thread and set up its connections
        worker.moveToThread(thread)
        worker.finished.connect(thread.quit)
        thread.started.connect(worker.start)
        
    def stop(thread, wait=True):
        #== Note that 'thread' is being used here instead of the usual 'self'
        thread.worker.stop()
        thread.quit()
        if wait:
            thread.wait()
        return thread.isFinished()
        
#-- end class Thread

class Worker(QtCore.QObject):

    error = QtCore.Signal(int)
    hostFound = QtCore.Signal()
    connected = QtCore.Signal()
    disconnected = QtCore.Signal()
    readyRead = QtCore.Signal()
    bytesWritten = QtCore.Signal(int)
    
    finished = QtCore.Signal() # required by the Thread class above
    
    class Stopped(Exception): pass
    
    def __init__(self):
        super(Worker, self).__init__()
        self._stopped_flag = False
        self._telnet = None
        self._read_mutex = QtCore.QMutex()
        self._read_buffer = QtCore.QByteArray()
        self._error_string = ""
        
    def isValid(self):
        return self._telnet is not None
        
    def state(self):
        if self.isValid() and self._telnet.get_socket():
            return QtNetwork.QAbstractSocket.ConnectedState
        else:
            return QtNetwork.QAbstractSocket.UnconnectedState
            
    def errorString(self):
        return self._error_string
        
    @QtCore.Slot(str, int)
    def connectToHost(self, name, port):
        try:
            host_info = QtNetwork.QHostInfo.fromName(name)
            
            if host_info.error() == QtNetwork.QHostInfo.NoError:
                self.hostFound.emit()
                self._telnet.open(name, port, timeout=5)
                self.connected.emit()
                
            elif host_info.error() == QtNetwork.QHostInfo.HostNotFound:
                self._error_string = host_info.errorString()
                self.error.emit(QtNetwork.QAbstractSocket.SocketError.HostNotFoundError)
            # end if
            
            return
            
        except:
            # import traceback
            # traceback.print_exc()
            self._error_string = sys.exc_info()[1]
        # end try
        
        self.error.emit(QtNetwork.QAbstractSocket.SocketError.ConnectionRefusedError)
        
    @QtCore.Slot()
    def disconnectFromHost(self):
        self.closeSocket()
        self.stop()
        
    @QtCore.Slot()
    def closeSocket(self):
        if self.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self._telnet.close()
            self.disconnected.emit()
            
    @QtCore.Slot(str)
    def write(self, s):
        try:
            if self.state() == QtNetwork.QAbstractSocket.ConnectedState:
                s = s.replace("\r\n", "\n").replace("\n", "\r\n")
                self._telnet.write(s.encode("latin-1"))
                self.bytesWritten.emit(len(s))
        except:
            # import traceback
            # traceback.print_exc()
            self._error_string = sys.exc_info()[1]
            self.error.emit(QtNetwork.QAbstractSocket.SocketError.NetworkError)
    
    def readAll(self):
        self._read_mutex.lock()
        data = self._read_buffer
        self._read_buffer = QtCore.QByteArray()
        self._read_mutex.unlock()
        return data
        
    def callback(self, socket, command, option):
        printable_constants = {
            IAC:"IAC", DONT:"DONT", DO:"DO", WONT:"WONT", WILL:"WILL", SE:"SE", NOP:"NOP", DM:"DM", BRK:"BRK", IP:"IP", AO:"AO", AYT:"AYT", EC:"EC", EL:"EL", GA:"GA", SB:"SB"
        }
        print "Negotiating:", socket, printable_constants.get(command, ord(command)), printable_constants.get(option, ord(option))
        
    def run(self):
        self._telnet = telnetlib.Telnet()
        # self._telnet.set_option_negotiation_callback(self.callback)
        # print "run: QTelnetSocket.Worker._telnet.get_socket =", self._telnet.get_socket()
        
        while True:
            if self._stopped_flag:
                break
            
            #== Do stuff ==#
            if self._telnet.get_socket():
                try:
                    data = self._telnet.read_very_eager()
                    if data:
                        # data = data.replace("\r\n", "\n").replace("\t", "        ")
                        self._read_mutex.lock()
                        self._read_buffer += data
                        self._read_mutex.unlock()
                        self.readyRead.emit()
                    # end if
                    
                except EOFError:
                    self.closeSocket()
                    self.error.emit(QtNetwork.QAbstractSocket.SocketError.RemoteHostClosedError)
                    
                except:
                    # import traceback
                    # traceback.print_exc()
                    self._error_string = sys.exc_info()[1]
                    self.error.emit(QtNetwork.QAbstractSocket.SocketError.NetworkError)
            
            #== If the worker object sits in a processing loop like this one,
            #== it will not respond to any QueuedConnection (i.e., externally
            #== triggered) signals unless we call sendPostedEvents().
            QtCore.QCoreApplication.sendPostedEvents(self, QtCore.QEvent.MetaCall)
            
    def cleanup(self):
        self.disconnectFromHost()
        self.deleteLater()
        
    @QtCore.Slot()
    def start(self): # required by the Thread class above
        try:
            self.run()
            
        except Worker.Stopped as e:
            pass
            
        except:
            # import traceback
            # traceback.print_exc()
            self._error_string = sys.exc_info()[1]
            self.error.emit(QtNetwork.QAbstractSocket.SocketError.NetworkError)
        
        finally:
            self.cleanup()
            self.finished.emit() # useful to the Thread class above
    
    @QtCore.Slot()
    def stop(self): # required by the Thread class above
        self._stopped_flag = True
        
#-- end class Worker

class QTelnetSocket(QtCore.QObject):

    ME = "[QTelnetSocket]"
    
    connectToHost_signal = QtCore.Signal(str, int)
    disconnectFromHost_signal = QtCore.Signal()
    close_signal = QtCore.Signal()
    write_signal = QtCore.Signal(str)
    
    error = QtCore.Signal(int)
    hostFound = QtCore.Signal()
    connected = QtCore.Signal()
    disconnected = QtCore.Signal()
    readyRead = QtCore.Signal()
    bytesWritten = QtCore.Signal(int)
    
    def __init__(self, parent):
        super(QTelnetSocket, self).__init__()
        self._peerName = ""
        self._peerPort = 0
        self._assign_port_code_data = None
        
        self._thread = Thread(Worker(), name="telnetThread")
        self._thread.worker.error.connect(self.on_error)
        self._thread.worker.hostFound.connect(self.hostFound)
        self._thread.worker.connected.connect(self.connected)
        self._thread.worker.connected.connect(self.send_assign_port_code)
        self._thread.worker.disconnected.connect(self.disconnected)
        self._thread.worker.readyRead.connect(self.readyRead)
        self._thread.worker.bytesWritten.connect(self.bytesWritten)
        
        self.connectToHost_signal.connect(self._thread.worker.connectToHost)
        self.disconnectFromHost_signal.connect(self._thread.worker.disconnectFromHost)
        self.close_signal.connect(self._thread.worker.closeSocket)
        self.write_signal.connect(self._thread.worker.write)
        
        self._thread.start()
        
    def is_control_seq(self, data):
        return data != "" and re.match(CONTROL_CODE + ".+" + END_CONTROL_CODE, data, re.DOTALL) != None
        
    def extract_control_data(self, data):
        if self.is_control_seq(data):
            m = re.match(CONTROL_CODE + "(.)(.*)" + END_CONTROL_CODE + "(.*)", data, re.DOTALL)
            data_code = m.group(1)
            payload   = m.group(2)
            self.data = m.group(3)
            return (data_code, payload)
        # end if
        return (None, None)
        
    def isValid(self):
        return self._thread.worker.isValid()
        
    def state(self):
        return self._thread.worker.state()
        
    def peerName(self):
        return self._peerName
        
    def peerPort(self):
        return self._peerPort
        
    def setSocketOption(self, option, value):
        print self.ME, "Ignoring setSocketOption() call."
        pass
        
    def close(self):
        if self._peerPort != 6801:
            print self.ME, "Pretending to close connection with", self._peerName, self._peerPort
            self.disconnected.emit()
        else:
            print self.ME, "Emitting close_signal."
            self.close_signal.emit()
        
    @QtCore.Slot(int)
    def on_error(self, error_code):
        if error_code == QtNetwork.QAbstractSocket.SocketError.RemoteHostClosedError:
            self._peerName = ""
            self._peerPort = 0
        else:
            print self.ME, "Detected error code", error_code, "-> thread.worker.get_socket() returns", self._thread.worker._telnet.get_socket()
        # end if
        self.error.emit(error_code)
    
    def send_assign_port_code(self):
        print self.ME, "Sending ASSIGN_PORT_CODE '6801'."
        self._assign_port_code_data = QtCore.QByteArray(CONTROL_CODE + ASSIGN_PORT_CODE + str("6801") + END_CONTROL_CODE)
        self.readyRead.emit()
        
    def connectToHost(self, name, port=23):
        if self._peerName == "" and self._peerPort == 0:
            print self.ME, "Connecting to host", name, port
            self._peerName = name
            self._peerPort = port
            self.connectToHost_signal.emit(name, port)
        else:
            self._peerPort = port
            print self.ME, "Pretending to connect to port", self._peerPort
            self.connected.emit()
        
    def disconnectFromHost(self):
        print self.ME, "Disconnecting from host."
        self._peerName = ""
        self._peerPort = 0
        self.disconnectFromHost_signal.emit()
        
    def abort(self):
        self.disconnectFromHost()
        
    def readAll(self):
        if self._assign_port_code_data:
            print self.ME, "readAll() returns ASSIGN_PORT_CODE."
            data = self._assign_port_code_data
            self._assign_port_code_data = None
            return data
        else:
            # print self.ME, "Calling thread.worker.readAll()."
            return self._thread.worker.readAll()
        
    def write(self, byte_array):
        s = byte_array.data()
        if self.is_control_seq(s):
            code, payload = self.extract_control_data(s)
            if code == WHO_CODE:
                print self.ME, "Discarding WHO_CODE."
                pass
            elif code == BREAK_CODE:
                print self.ME, "Sending ^C in place of BREAK_CODE."
                self.write_signal.emit(chr(3))
            # end if
            self.bytesWritten.emit(len(s))
        else:
            # print self.ME, "Sending", repr(s)
            self.write_signal.emit(s)
        
    def flush(self):
        pass
        
    def errorString(self):
        return self._thread.worker.errorString()
        