import datetime

from ..globals import *

include.query_info

class Listener(Subroutine):

    MESSAGE_TIMER_DURATION = 1.0
    
    def __init__(self, command_processor):
        super(Listener, self).__init__(self.__class__.__name__)
        
        self.__default_command_processor = command_processor
        self.__process = None
        self.__prev_command_time = None
        self.__command_history = []
        self.__homedir = ""
        self.exit_code = 0
        
    def start(self, owning_process):
        self.__process = owning_process
        return self._main_loop()
        
    def kill(self):
        self._cleanup()
        
    def ready(self, ready_mode):
        if ready_mode:
            now = datetime.datetime.now()
            delta, self.__prev_command_time = now - self.__prev_command_time, now
            if self.__process.stack_level() > 1:
                command_level_str = " level %d" % (self.__process.stack_level())
            else:
                command_level_str = ""
            
            ready_message = "r %s %0.3f %d%s" % (now.strftime("%H%M"), delta.seconds + (delta.microseconds / 10.0**6), call.segfault_count, command_level_str)
            call.ioa_(ready_message)
    
    def _main_loop(self):
        # command_line = parm()
        code         = parm()
        # commands     = []
        
        # query_info.suppress_name_sw = True
        # query_info.suppress_spacing = True
        
        self._initialize()
        
        if not self.__process.pit().no_start_up:
            call.cu_.cp("exec_com start_up new_proc interactive", code)
        # end if
        
        # self.exit_code = 0
        # while self.exit_code == 0:
            # try:
                # #== If there are no more commands queued up from a multi-command line
                # #== then get some commands from command_query_
                # if commands == []:
                    # call.cu_.ready_proc()
                    # call.command_query_(query_info, command_line, "listener")
                    # #== Semi-colons separate multiple commands--create a command queue
                    # commands = command_line.val.split(";")
                # # end if
                
                # #== Get the next command in the queue and execute it
                # command_line.val = commands.pop(0).strip()
                # self.__command_history.append(command_line.val)
                # call.cu_.cp(command_line.val, code)
                # self.exit_code = code.val
                
            # except BreakCondition:
                # call.hcs_.signal_break()
            # except DisconnectCondition:
                # self.exit_code = System.LOGOUT
            # except ShutdownCondition:
                # self.exit_code = System.LOGOUT
            # except (SegmentFault, LinkageError, InvalidSegmentFault):
                # call.dump_traceback_()
            # except:
                # #== FOR DEBUGGING THE SIMULATION
                # call.dump_traceback_()
            # # end try
        # # end while
        self._enter_command_level()
        
        # do any cleanup necessary at the CommandShell level
        self._cleanup()
        
        return self.exit_code
        
    def _initialize(self):
        homedir = parm()
        call.user_info_.homedir(homedir)
        call.sys_.push_directory(homedir.val)
        call.cu_.set_command_processor(self.__default_command_processor)
        call.cu_.set_ready_procedure(self.ready)
        call.cu_.set_ready_mode(True)
        self.__homedir = homedir.val
        self.__prev_command_time = datetime.datetime.now()
        
        msg_handlers = {
            'shutdown_announcement': self._process_ms_handler,
        }
        self.__process.register_msg_handlers(msg_handlers)
        
        call.timer_manager_.alarm_call(self.MESSAGE_TIMER_DURATION, self._interactive_message)
        
        self._print_motd()
        
    def _enter_command_level(self):
        command_line = parm()
        code         = parm()
        commands     = []
        
        query_info.suppress_name_sw = True
        query_info.suppress_spacing = True
        
        ### ! EXPERIMENTAL! ###
        with on_quit(self._push_command_level):
        
            self.exit_code = 0
            while self.exit_code == 0:
                try:
                    #== If there are no more commands queued up from a multi-command line
                    #== then get some commands from command_query_
                    if commands == []:
                        call.cu_.ready_proc()
                        call.command_query_(query_info, command_line, "listener")
                        #== Semi-colons separate multiple commands--create a command queue
                        commands = command_line.val.split(";")
                    # end if
                    
                    #== Get the next command in the queue and execute it
                    command_line.val = commands.pop(0).strip()
                    
                    ### ! EXPERIMENTAL! ###
                    if self.__process.stack_level() > 1 and command_line.val in ["release", "rl"]:
                        return 0
                    # end if
                    
                    self.__command_history.append(command_line.val)
                    call.cu_.cp(command_line.val, code)
                    self.exit_code = code.val
                    
                except BreakCondition:
                    call.hcs_.signal_break()
                except DisconnectCondition:
                    self.exit_code = System.LOGOUT
                except ShutdownCondition:
                    self.exit_code = System.LOGOUT
                except (SegmentFault, LinkageError, InvalidSegmentFault):
                    call.dump_traceback_()
                except:
                    #== FOR DEBUGGING THE SIMULATION
                    call.dump_traceback_()
                # end try
            # end while
            
            return self.exit_code
    
    def _push_command_level(self):
        print "Pushing command level"
        self.__process.push_stack()
        exit_code = self._enter_command_level()
        self.__process.pop_stack()
        print "Popping command level"
    
    def _process_ms_handler(self, message):
        if message['type'] == "shutdown_announcement":
            # call.ioa_("From {0} {1}: {2}", message['from'], message['time'].ctime(), message['text'])
            call.ioa_("{0}: {1}", message['from'], message['text'])
        
    def _interactive_message(self):
        mbx_segment = parm()
        code        = parm()
        
        call.timer_manager_.reset_alarm_call(self._interactive_message)
        
        self.__process.stack.assert_create("accepting_messages", bool)
        accepting = self.__process.stack.accepting_messages
        self.__process.stack.assert_create("holding_messages", bool)
        holding = self.__process.stack.holding_messages
        
        user_id = self.__process.uid()
        homedir = self.__homedir
        
        call.sys_.lock_user_mbx_(user_id, homedir, mbx_segment, code)
        if mbx_segment.ptr != null():
            # accepting = mbx_segment.ptr.has_state("accept_messages")
            # holding   = mbx_segment.ptr.has_state("hold_messages")
            with mbx_segment.ptr:
                for message in mbx_segment.ptr.messages[:]:
                    if message['type'] == "interactive_message":
                        #== Print unread interactive messages and shutdown announcements
                        if message['status'] == "unread" and accepting:
                            call.ioa_("From {0} {1}: {2}", message['from'], message['time'].ctime(), message['text'])
                            message['status'] = "read"
                        # end if
                        if accepting and holding:
                            message['status'] = "hold"
                        # end if
                        #== Delete messages marked as read; messages marked as unread or hold will remain
                        if message['status'] == "read":
                            mbx_segment.ptr.messages.remove(message)
                        # end if
                    # end if
                # end for
            # end with
            call.sys_.unlock_user_mbx_(mbx_segment.ptr, code)
        # end if
        
        call.timer_manager_.alarm_call(self.MESSAGE_TIMER_DURATION, self._interactive_message)
    
    def _cleanup(self):
        pass
        
    def _print_motd(self):
        #== Only do this if the user does not have a start_up.ec in his
        #== home directory
        if not GlobalEnvironment.fs.file_exists(self.__homedir + ">start_up.ec"):
            #== Open the system motd file if it exists and display its contents
            try:
                f = open(vfile_(GlobalEnvironment.fs.system_control_dir + ">motd"))
                file_text = f.read()
                f.close()
                
                call.ioa_(file_text)
            except:
                pass
                