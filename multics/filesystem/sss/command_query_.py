
from multics.globals import *
from query_info import *

class command_query_(Subroutine):
    def __init__(self):
        super(command_query_, self).__init__(self.__class__.__name__)
        
    def __call__(self, info_ptr, answer, caller, control_string="", *args, **kwargs):
        self._do_query(info_ptr, answer, caller, control_string, *args, **kwargs)
        
    def _do_query(self, info_ptr, answer, caller, control_string="", *args, **kwargs):
        question = control_string.format(*args, **kwargs)
        if not info_ptr.suppress_name_sw:
            question = caller + ":" + (" " + question if question else "")
        if not info_ptr.suppress_spacing:
            question = "\n" + question + "  "
            
        call.ioa_.nnl(question)
        while True:
            if info_ptr.repeat_time >= 30:
                call.timer_manager_.alarm_call(info_ptr.repeat_time, self._repeat_question, question)
                
            answer.val = self._get_input(block=True)
            if info_ptr.echo_answer_sw:
                call.ioa_(answer.val)
            # end if
            
            call.timer_manager_.reset_alarm_call(self._repeat_question)
            
            if answer.val.strip() == "?":
                explanation = info_ptr.explanation_ptr
                if explanation:
                    call.ioa_(explanation)
                else:
                    break
                # end if
            elif info_ptr.yes_or_no_sw:
                if answer.val.strip().lower() in ["yes", "y", "no", "n"]:
                    break
                # end if
                call.ioa_("Question requires a 'yes' or 'no' response.")
            else:
                break
            # end if
            
            if info_ptr.prompt_after_explanation and question.strip():
                call.ioa_.nnl(question)
            else:
                call.ioa_.nnl("Answer: ")
            # end if
        # end while
        
        if not info_ptr.literal_sw:
            answer.val = answer.val.strip()
    
    def _get_input(self, block=False):
        tty_channel = get_calling_process_().tty()
        return GlobalEnvironment.supervisor.llin(block, tty_channel)
        
    def _repeat_question(self, question):
        call.ioa_.nnl(question)
        