
from multics.globals import *

def logout():
    declare (arg_list = parm)
    call.sys_.set_exit_code(System.LOGOUT)
    