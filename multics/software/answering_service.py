import shutil
import datetime
from pprint import pprint

from ..globals import *
from tty import *
from user_control import UserControl

from PySide import QtCore, QtGui, QtNetwork

include.pnt
include.pdt
include.whotab
include.pit
include.login_info
            
SERVER_NAME = "localhost"
SERVER_PORT = 6800

class AnsweringService(SystemSubroutine):

    DEFAULT_CP_PATH = ">sss>default_cp"

    def __init__(self, supervisor, command_processor):
        super(AnsweringService, self).__init__(self.__class__.__name__, supervisor)
        
        self.supervisor = supervisor
        self.user_control = command_processor
        from process_overseer import ProcessOverseer
        self.process_overseer = ProcessOverseer(supervisor)
        self.__process = None
        self.__person_name_table = None
        self.__project_definition_tables = {}
        self.__whotab = None
        self.__pending_login_ttys = []
        self.__logins_in_progress = []
        self.exit_code = 0
        self.shutting_down = False
        
    def start(self, owning_process):
        self.__process = owning_process
        return self._main_loop()
        
    def kill(self):
        # self._cleanup()
        self.shutting_down = True
        pass
        
    def _main_loop(self):
        self._initialize()
        
        # shutting_down = False
        while not (self.shutting_down and self.process_overseer.running_processes == []):
            try:
                #== Visit each tty in the process of logging in and advance its UserControl
                #== state if possible
                for login in self.__logins_in_progress[:]:
                    state = login.do_state()
                    
                    if state == UserControl.CONTINUE:
                        continue
                        
                    elif state == UserControl.LOGIN_COMPLETE:
                        tty_channel = login.tty
                        process = self._user_login(login.login_options(), tty_channel)
                        if process:
                            if tty_channel:
                                print "Attaching tty_channel", tty_channel.id, "to process", process.id(), process.objectName()
                                process.attach_tty(tty_channel)
                            else:
                                print "Attaching system console to process", process.id(), process.objectName()
                                self.supervisor.hardware.io.attach_console_process(process.id())
                            # end if
                            print "Starting process", process.objectName()
                            process.start()
                        # end if
                        
                    elif state == UserControl.DISCONNECTED:
                        #== Only ttys disconnect
                        print "tty_channel", login.tty.id, "disconnected during login"
                    # end if
                    
                    #== For LOGIN_COMPLETE and DISCONNECTED states, we remove the UserControl object
                    #== from the list of logins still in progress
                    self.__logins_in_progress.remove(login)
                # end for
                
                #== Add the next pending login tty to the list of logins 'in progress'
                if self.__pending_login_ttys:
                    tty_channel = self.__pending_login_ttys.pop(0)
                    login = UserControl(self.supervisor,
                                        self.__person_name_table,
                                        self.__project_definition_tables,
                                        self.__whotab,
                                        tty_channel)
                    self.__logins_in_progress.append(login)
                    
                #== Add the system console to the list of logins 'in progress' if it isn't
                #== already attached to a process and not already in the list
                if (not self.supervisor.hardware.io.terminal_closed() and
                    not self.supervisor.hardware.io.attached_console_process() and
                    not any([ login.tty == None for login in self.__logins_in_progress ])):
                    login = UserControl(self.supervisor,
                                        self.__person_name_table,
                                        self.__project_definition_tables,
                                        self.__whotab,
                                        None)
                    self.__logins_in_progress.append(login)
                # end if
                
                if not self.shutting_down:
                    check_conditions_(ignore_break_signal=True)
                # end if
            
            # except DisconnectCondition:
                # shutting_down = True
            
            except ShutdownCondition:
                self.shutting_down = True
            # end try
            
            #== See if any processes have terminated with LOGOUT or NEW_PROC exit codes
            for process in self.process_overseer.running_processes:
                if process.exit_code != 0:
                    if process.exit_code == System.LOGOUT:
                        self._user_logout(process)
                        
                    elif process.exit_code == System.NEW_PROCESS:
                        self._user_new_proc(process)
                    # end if
                # end if
            # end for
            
        # end while
        
        self._cleanup()
        
        return 0
        
    def _default_home_dir(self, person_id, project_id):
        return ">".join([self.supervisor.fs.user_dir_dir, project_id, person_id])
        
    def _new_process(self, person_id, pdt, login_options={}):
        # pprint(login_options)
        login_info.person_id    = person_id
        login_info.project_id   = pdt.project_id
        login_info.process_type = pit_process_type_interactive
        login_info.homedir      = login_options.get('home_dir') or pdt.users[person_id].home_dir or self._default_home_dir(person_id, pdt.project_id)
        login_info.cp_path      = pdt.users[person_id].cp_path or self.DEFAULT_CP_PATH
        login_info.no_start_up  = login_options.get('no_start_up', False)
        from listener import Listener
        return self.process_overseer.create_process(login_info, Listener)
    
    def _user_login(self, login_options, tty_channel):
        login_info.time_login = datetime.datetime.now()
        
        process = self._new_process(login_options['person_id'], login_options['pdt'], login_options)
        if process:
            #== Add the user to the whotab
            with self.__whotab:
                self.__whotab.entries[login_info.user_id] = WhotabEntry(login_info.time_login, process.id(), process.dir())
            # end with
            
            self.supervisor.llout("\n%s logged in on %s\n" % (login_info.user_id, login_info.time_login.ctime()), tty_channel)
            print "%s logged in on %s" % (login_info.user_id, login_info.time_login.ctime())
        # end if
        
        return process
        
    def _user_logout(self, process):
        user_id = process.uid()
        tty_channel = process.tty()
        
        self.process_overseer.destroy_process(process)
        
        self.supervisor.llout("%s logged out on %s\n" % (user_id, datetime.datetime.now().ctime()), process.tty())
        print "%s logged out on %s" % (user_id, datetime.datetime.now().ctime())
        
        #== Remove the entry in the whotab corresponding to this user
        with self.__whotab:
            del self.__whotab.entries[user_id]
        # end with
        pprint(self.__whotab)
        
        if tty_channel == None:
            self.supervisor.hardware.io.detach_console_process(process.id())
        else:
            self.__pending_login_ttys.append(tty_channel)
        # end if
        
    def _user_new_proc(self, process):
        #== Save importnt user process info from the process being destroyed
        user_id       = process.uid()
        person_id, _, project_id = user_id.partition(".")
        pit           = process.pit()
        tty_channel   = process.tty()
        pdt           = self.__project_definition_tables.get(project_id)
        login_options = {
            'person_id'  : person_id,
            'project_id' : project_id,
            'pdt'        : pdt,
            'home_dir'   : pit.homedir,
            'no_start_up': pit.no_start_up,
        }
        login_options.update(process.stack.new_proc_options)
        
        #== Destroy the old process
        if tty_channel == None:
            self.supervisor.hardware.io.detach_console_process(process.id())
        # end if
        self.process_overseer.destroy_process(process)
        
        #== Create the new process
        process = self._new_process(person_id, pdt, login_options)
        if process:
            #== Re-attach the tty/console
            if tty_channel:
                print "Attaching tty_channel", tty_channel.id, "to process", process.id(), process.objectName()
                process.attach_tty(tty_channel)
            else:
                print "Attaching system console to process", process.id(), process.objectName()
                self.supervisor.hardware.io.attach_console_process(process.id())
            # end if
            
            #== Start the new process
            print "Starting new process", process.objectName()
            process.start()
            
            #== Update the entry in the whotab corresponding to this user
            with self.__whotab:
                self.__whotab.entries[user_id].process_id = process.id()
                self.__whotab.entries[user_id].process_dir = process.dir()
            # end with
            pprint(self.__whotab)
        else:
            self.supervisor.llout("Error creating process!")
        # end if
    
    def _initialize(self):
        self.__person_name_table = self.supervisor.pnt
        self.__project_definition_tables = self.supervisor.pdt
        self.__whotab = self.supervisor.whotab
        
        msg_handlers = {
            'upload_pmf_request': self._upload_pmf_request_handler,
        }
        self.__process.register_msg_handlers(msg_handlers)
        
        self.rfs_listener = RFSListener(self.__pending_login_ttys, self)
        self.rfs_listener.start()
        
    def _cleanup(self):
        #== Close down any tty channels in the midst of logging in
        for login in self.__logins_in_progress:
            tty_channel = login.tty
            if tty_channel:
                tty_channel.disconnect()
            # end if
        # end for
        #== Close down any tty channels connected but not yet under User Control
        for tty_channel in self.__pending_login_ttys:
            tty_channel.disconnect()
        # end for
        print "Shutting down RFS listener"
        self.rfs_listener.close()
        
    def _upload_pmf_request_handler(self, message):
        pnt  = parm()
        pdt  = parm()
        sat  = parm()
        code = parm()
        
        pdt_file = message['src_file']
        src_dir = message['src_dir']
        dst_dir = self.supervisor.fs.system_control_dir
        src_pdt_path = self.supervisor.fs.path2path(src_dir, pdt_file)
        dst_pdt_path = self.supervisor.fs.path2path(dst_dir, pdt_file)
        shutil.move(src_pdt_path, dst_pdt_path)
        
        call.hcs_.initiate(dst_dir, pdt_file, "", 0, 0, pdt, code)
        if pdt.ptr != null():
            #== Add project to the system_administrator_table if necessary
            call.hcs_.initiate(self.supervisor.fs.system_control_dir, "system_administrator_table", "", 0, 0, sat, code)
            if sat.ptr != null():
                if pdt.ptr.project_id not in sat.ptr.projects:
                    with sat.ptr:
                        sat.ptr.add_project(pdt.ptr.project_id, pdt.ptr._filepath(), pdt.ptr.alias)
                    # end with
                # end if
            # end if
            
            #== Create project directory (with add_name for alias) if necessary
            project_dir = self.supervisor.fs.path2path(self.supervisor.fs.user_dir_dir, pdt.ptr.project_id)
            if not self.supervisor.fs.file_exists(project_dir):
                print "Creating project directory " + project_dir
                self.supervisor.fs.mkdir(project_dir)
            # end if
            if pdt.ptr.alias:
                print "Adding name " + pdt.ptr.alias + " to project directory"
                self.supervisor.fs.add_name(project_dir, pdt.ptr.alias)
            # end if
            
            call.hcs_.initiate(self.supervisor.fs.system_control_dir, "person_name_table", "", 0, 0, pnt, code)
            
            #== Create user home directories (with add_names for aliases) if necessary
            for user_config in pdt.ptr.users.values():
                homedir = user_config.home_dir or self._default_home_dir(user_config.person_id, pdt.ptr.project_id)
                if not self.supervisor.fs.file_exists(homedir):
                    self._create_new_home_dir(user_config.person_id, pnt.ptr, homedir)
                    
    def _create_new_home_dir(self, person_id, pnt_ptr, homedir):
        segment = parm()
        code    = parm()
        
        print "Creating user home directory " + homedir
        code.val = self.supervisor.fs.mkdir(homedir)
        if code.val == 0:
            print "Creating user mailbox file"
            call.hcs_.make_seg(homedir, person_id + ".mbx", "", 0, segment(dict), code)
        # end if
            
        if pnt_ptr.name_entries[person_id].alias:
            print "Adding name " + pnt_ptr.name_entries[person_id].alias + " to home directory"
            self.supervisor.fs.add_name(homedir, pnt_ptr.name_entries[person_id].alias)

class RFSListener(QtNetwork.QTcpServer):

    def __init__(self, pending_login_ttys, parent=None):
        super(RFSListener, self).__init__(parent)
        self.ME = self.__class__.__name__
        self.__rfs_port = SERVER_PORT
        self.__new_com_port = SERVER_PORT
        self.__recycled_com_ports = []
        self.__handshakers = []
        self.__pending_login_ttys = pending_login_ttys
        
    def _get_next_available_com_port(self):
        if self.__recycled_com_ports != []:
            return self.__recycled_com_ports.pop(0)
        # end if
        self.__new_com_port += 1
        return self.__new_com_port
        
    def start(self):
        if self.listen(port=self.__rfs_port):
            self.newConnection.connect(self.respond_to_rfs)
            print self.ME, "listening on port", self.__rfs_port
        else:
            print self.ME, self.errorString()
    
    def recycle_com_port(self, port_num):
        print self.ME, "recycling port", port_num
        self.__recycled_com_ports.append(port_num)
        
    @QtCore.Slot()
    def respond_to_rfs(self):
        #== Get the incoming 'request for service' socket
        socket = self.nextPendingConnection()
        socket.setSocketOption(QtNetwork.QAbstractSocket.LowDelayOption, 1)
        print self.ME, "respond_to_rfs:", socket.localPort(), socket.localAddress().toString()
        
        #== Get a port for ongoing communication and create a 'handshaker' to facilitate the
        #== switch-over to the new com port
        com_port = self._get_next_available_com_port()
        handshaker = QtNetwork.QTcpServer(self)
        #== Start listening on the new com port
        if handshaker.listen(port=com_port):
            print self.ME, "listening to com port:", com_port
            handshaker.newConnection.connect(lambda: self.add_com_connection(handshaker))
            self.__handshakers.append(handshaker)
            
            #== Send a packet to the client indicating the (permanent) com port number to switch over to
            socket.write(DataPacket.Out(ASSIGN_PORT_CODE, com_port))
            if not socket.waitForBytesWritten():
                print self.ME, "ERROR: Client not responding to handshake"
    
    def add_com_connection(self, handshaker):
        socket = handshaker.nextPendingConnection()
        com_port = socket.localPort()
        socket.setObjectName("tty_socket_%d" % (com_port))
        socket.setSocketOption(QtNetwork.QAbstractSocket.LowDelayOption, 1)
        socket.disconnected.connect(lambda: self.recycle_com_port(com_port))
        
        tty_channel = TTYChannel(socket)
        self.__pending_login_ttys.append(tty_channel)
        print self.ME, "created tty_channel", tty_channel.id
        
        handshaker.close()
        self.__handshakers.remove(handshaker)
        