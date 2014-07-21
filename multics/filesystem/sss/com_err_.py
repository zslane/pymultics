
from multics.globals import *

class com_err_(Subroutine):

    def __init__(self):
        super(com_err_, self).__init__(self.__class__.__name__)
        
    def procedure(self, code, caller, control_string="", *argl):
        user_message = parm()
        if control_string:
            call.ioa_.rsnnl(control_string, user_message, *argl)
        else:
            user_message.val = ""
        system_message = repr(code)
        call.ioa_("^a: ^[ ^a ^;^s^]^a", caller, code != 0, system_message, user_message.val)
        
    def suppress_name(self, code, caller, control_string="", *argl):
        user_message = parm()
        if control_string:
            call.ioa_.rsnnl(control_string, user_message, *argl)
        else:
            user_message.val = ""
        system_message = repr(code)
        call.ioa_("^[^a ^;^s^]^a", code != 0, system_message, user_message.val)
        
#-- end class com_err_
