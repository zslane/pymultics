import shutil
import datetime
from collections import defaultdict
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
            
SYSTEM_CONSOLE = None

class AnsweringService(Subroutine):

    DEFAULT_CP_PATH = ">sss>command_processor_"

    def __init__(self, command_processor):
        super(AnsweringService, self).__init__(self.__class__.__name__)
        
        self.__process            = None
        self.__whotab             = None
        self.__pending_login_ttys = []
        self.__logins_in_progress = []
        self.__login_count        = defaultdict(int)
        
        self.exit_code            = 0
        self.shutting_down        = False
        
        import process_overseer
        reload(process_overseer)
        from process_overseer import ProcessOverseer
        self.process_overseer = ProcessOverseer()
        
    def start(self, owning_process):
        self.__process = owning_process
        return self._main_loop()
        
    def kill(self):
        # self._cleanup()
        self.shutting_down = True
        
    def _main_loop(self):
        MAX_ATTEMPTS = 6
        
        self._initialize()
        
        while not (self.shutting_down and self.process_overseer.running_processes == []):
            try:
                #== Visit each tty in the process of logging in and advance its UserControl
                #== state if possible
                for login in self.__logins_in_progress[:]:
                    state = login.do_state()
                    tty_channel = login.tty
                    
                    if state == UserControl.CONTINUE:
                        continue
                        
                    elif state == UserControl.LOGIN_COMPLETE:
                        process = self._user_login(login.login_options(), tty_channel)
                        if process:
                            if tty_channel:
                                print "Attaching tty_channel", tty_channel.id, "to process", process.id(), process.objectName()
                                process.attach_tty(tty_channel)
                            else:
                                print "Attaching system console to process", process.id(), process.objectName()
                                GlobalEnvironment.hardware.io.attach_console_process(process.id())
                            # end if
                            print "Starting process", process.objectName()
                            process.start()
                        else:
                            #== If there were errors creating a process for the user, just put the
                            #== tty channel back on the list of pending login ttys
                            self.__pending_login_ttys.append(tty_channel)
                        # end if
                        
                    elif state == UserControl.DISCONNECTED:
                        #== Only ttys disconnect
                        print "tty_channel", tty_channel.id, "disconnected during login"
                    # end if
                    
                    #== For LOGIN_COMPLETE and DISCONNECTED states, we remove the UserControl object
                    #== from the list of logins still in progress
                    self.__logins_in_progress.remove(login)
                # end for
                
                #== Add the next pending login tty to the list of logins 'in progress'
                if self.__pending_login_ttys:
                    tty_channel = self.__pending_login_ttys.pop(0)
                    first_login = (self.__login_count[tty_channel] == 0)
                    login = UserControl(MAX_ATTEMPTS, self.__whotab, tty_channel, wait_for_linefeed=first_login)
                    self.__logins_in_progress.append(login)
                # end if
                    
                #== Add the system console to the list of logins 'in progress' if it isn't
                #== already attached to a process and not already in the list
                if (not GlobalEnvironment.hardware.io.attached_console_process() and
                    not any([ login.tty == SYSTEM_CONSOLE for login in self.__logins_in_progress ])):
                    first_login = (self.__login_count[SYSTEM_CONSOLE] == 0)
                    login = UserControl(-1, self.__whotab, SYSTEM_CONSOLE, wait_for_linefeed=first_login)
                    self.__logins_in_progress.append(login)
                # end if
                
                if not self.shutting_down:
                    GlobalEnvironment.supervisor.check_for_shutdown()
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
        return ">".join([GlobalEnvironment.fs.user_dir_dir, project_id, person_id])
        
    def _new_process(self, person_id, pdt, login_options, tty_channel):
        # pprint(login_options)
        login_info.person_id    = person_id
        login_info.project_id   = pdt.project_id
        login_info.process_type = pit_process_type_interactive
        login_info.homedir      = login_options.get('home_dir') or pdt.users[person_id].home_dir or self._default_home_dir(person_id, pdt.project_id)
        login_info.cp_path      = pdt.users[person_id].cp_path or self.DEFAULT_CP_PATH
        login_info.no_start_up  = login_options.get('no_start_up', False)
        from listener import Listener
        return self.process_overseer.create_process(login_info, Listener, tty_channel)
    
    def _user_login(self, login_options, tty_channel):
        journal = parm()
        code    = parm()
        
        login_info.time_login = datetime.datetime.now()
        person_id = login_options['person_id']
        tty_name = (tty_channel and tty_channel.name) or "console"
        self.__login_count[tty_channel] += 1
        
        process = self._new_process(person_id, login_options['pdt'], login_options, tty_channel)
        if process:
            #== Add the user to the whotab
            with self.__whotab:
                self.__whotab.entries[login_info.user_id] = WhotabEntry(login_info.time_login, process.id(), process.dir())
            # end with
            
            #== Update the login journal
            call.hcs_.initiate(GlobalEnvironment.fs.system_control_dir, "login_journal", "", 0, 0, journal, code)
            if code.val == 0 and journal.ptr != null():
                journal_entry = journal.ptr.get(login_info.user_id, {})
                last_login_time = journal_entry.get('last_login_time')
                last_login_from = journal_entry.get('last_login_from')
                with journal.ptr:
                    journal.ptr[login_info.user_id] = {
                        'last_login_time': login_info.time_login,
                        'last_login_from': tty_name,
                    }
                # end with
            # end if
            
            if not login_options.get('brief'):
                call.iox_.write(tty_channel, "%s logged in %s from %s\n" % (login_info.user_id, login_info.time_login.ctime(), tty_name))
                if last_login_time:
                    call.iox_.write(tty_channel, "Last login %s from %s\n" % (last_login_time.ctime(), last_login_from))
                # end if
            print "%s logged in on %s from %s" % (login_info.user_id, login_info.time_login.ctime(), tty_name)
        # end if
        
        return process
        
    def _user_logout(self, process):
        user_id     = process.uid()
        tty_channel = process.tty()
        
        try:
            logout_options = process.stack.logout_options
        except:
            logout_options = {}
        # end try
        
        self.process_overseer.destroy_process(process)
        
        if not logout_options.get('brief'):
            call.iox_.write(process.tty(), "%s logged out %s\n" % (user_id, datetime.datetime.now().ctime()))
        print "%s logged out %s" % (user_id, datetime.datetime.now().ctime())
        
        #== Remove the entry in the whotab corresponding to this user
        with self.__whotab:
            del self.__whotab.entries[user_id]
        # end with
        pprint(self.__whotab)
        
        if tty_channel == SYSTEM_CONSOLE:
            call.iox_.write(tty_channel, "\n")
            GlobalEnvironment.supervisor.hardware.io.detach_console_process(process.id())
        elif not logout_options.get('hold'):
            call.iox_.write(tty_channel, "Disconnect\n")
            GlobalEnvironment.supervisor.hardware.io.disconnect_tty(tty_channel)
        else:
            call.iox_.write(tty_channel, "\n")
            self.__pending_login_ttys.append(tty_channel)
        # end if
        
    def _user_new_proc(self, process):
        #== Save importnt user process info from the process being destroyed
        user_id       = process.uid()
        person_id, _, project_id = user_id.partition(".")
        pit           = process.pit()
        tty_channel   = process.tty()
        pdt           = GlobalEnvironment.supervisor.pdt.get(project_id)
        login_options = {
            'person_id'  : person_id,
            'project_id' : project_id,
            'pdt'        : pdt,
            'home_dir'   : pit.homedir,
            'no_start_up': pit.no_start_up,
        }
        login_options.update(process.stack.new_proc_options)
        
        #== Destroy the old process
        if tty_channel == SYSTEM_CONSOLE:
            GlobalEnvironment.supervisor.hardware.io.detach_console_process(process.id())
        # end if
        self.process_overseer.destroy_process(process)
        
        #== Create the new process
        process = self._new_process(person_id, pdt, login_options, tty_channel)
        if process:
            #== Re-attach the tty/console
            if tty_channel:
                print "Attaching tty_channel", tty_channel.id, "to process", process.id(), process.objectName()
                process.attach_tty(tty_channel)
            else:
                print "Attaching system console to process", process.id(), process.objectName()
                GlobalEnvironment.supervisor.hardware.io.attach_console_process(process.id())
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
            call.iox_.write(SYSTEM_CONSOLE, "Error creating process!")
        # end if
    
    def _initialize(self):
        self.__whotab = GlobalEnvironment.supervisor.whotab
        
        msg_handlers = {
            'upload_pmf_request': self._upload_pmf_request_handler,
        }
        self.__process.register_msg_handlers(msg_handlers)
        
        self.rfs_listener = RFSListener(GlobalEnvironment.supervisor.site_config['port'], self.__pending_login_ttys, self)
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
        dst_dir = GlobalEnvironment.fs.system_control_dir
        src_pdt_path = GlobalEnvironment.fs.path2path(src_dir, pdt_file)
        dst_pdt_path = GlobalEnvironment.fs.path2path(dst_dir, pdt_file)
        shutil.move(src_pdt_path, dst_pdt_path)
        
        call.hcs_.initiate(dst_dir, pdt_file, "", 0, 0, pdt, code)
        if pdt.ptr != null():
            #== Add project to the system_administrator_table if necessary
            call.hcs_.initiate(GlobalEnvironment.fs.system_control_dir, "system_administrator_table", "", 0, 0, sat, code)
            if sat.ptr != null():
                if pdt.ptr.project_id not in sat.ptr.projects:
                    with sat.ptr:
                        sat.ptr.add_project(pdt.ptr.project_id, pdt.ptr._filepath(), pdt.ptr.alias)
                    # end with
                # end if
            # end if
            
            #== Add pdt segment to supervisor's pdt table if necessary
            if pdt.ptr.project_id not in GlobalEnvironment.supervisor.pdt:
                GlobalEnvironment.supervisor.pdt[pdt.ptr.project_id] = pdt.ptr
                if pdt.ptr.alias:
                    GlobalEnvironment.supervisor.pdt[pdt.ptr.alias] = pdt.ptr
                # end if
            # end if
            
            #== Create project directory (with add_name for alias) if necessary
            project_dir = GlobalEnvironment.fs.path2path(GlobalEnvironment.fs.user_dir_dir, pdt.ptr.project_id)
            if not GlobalEnvironment.fs.file_exists(project_dir):
                print "Creating project directory " + project_dir
                GlobalEnvironment.fs.mkdir(project_dir)
            # end if
            if pdt.ptr.alias:
                print "Adding name " + pdt.ptr.alias + " to project directory"
                GlobalEnvironment.fs.add_name(project_dir, pdt.ptr.alias)
            # end if
            
            call.hcs_.initiate(GlobalEnvironment.fs.system_control_dir, "PNT.pnt", "", 0, 0, pnt, code)
            
            #== Create user home directories (with add_names for aliases) if necessary
            for user_config in pdt.ptr.users.values():
                homedir = user_config.home_dir or self._default_home_dir(user_config.person_id, pdt.ptr.project_id)
                if not GlobalEnvironment.fs.file_exists(homedir):
                    self._create_new_home_dir(user_config.person_id, pnt.ptr, homedir)
                # end if
            # end for
        else:
            call.iox_.write(SYSTEM_CONSOLE, "Failed to install %s." % (pdt_file))
                    
    def _create_new_home_dir(self, person_id, pnt_ptr, homedir):
        print "Creating user home directory " + homedir
        GlobalEnvironment.fs.mkdir(homedir)
        
        alias = pnt_ptr.name_entries[person_id].alias
        _, homedir_name = GlobalEnvironment.fs.split_path(homedir)
        #== If there's an alias, only create an add_name for the home directory if the
        #== first letter of each matches. We don't want an alias like 'bar' being added
        #== as a name to a home dir like >udd>Multics>Common just because it was specified
        #== as user Bar's home dir in the Multics PDT.
        if alias and alias[0].lower() == homedir_name[0].lower():
            print "Adding name " + pnt_ptr.name_entries[person_id].alias + " to home directory"
            GlobalEnvironment.fs.add_name(homedir, pnt_ptr.name_entries[person_id].alias)

class RFSListener(QtNetwork.QTcpServer):

    def __init__(self, server_port, pending_login_ttys, parent=None):
        super(RFSListener, self).__init__(parent)
        self.ME = self.__class__.__name__
        self.__rfs_port = server_port
        self.__new_com_port = server_port
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
            socket.flush()
            # if not socket.waitForBytesWritten():
                # print self.ME, "ERROR: Client not responding to handshake"
    
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
        