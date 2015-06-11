
from multics.globals import *

include.iox_control

ESC = chr(27)

def CTRL(s):
    return chr(ord(s.upper()) - 64)
    
def cc_test():
    send_control_code("[c") # Query Device Code
    call. ioa_ (get_response('c').replace(ESC, "<ESC>"))
    send_control_code("[5n") # Query Device Status
    call. ioa_ (get_response('n').replace(ESC, "<ESC>"))
    send_control_code("[6n") # Query Cursor Position
    call. ioa_ (get_response('R').replace(ESC, "<ESC>"))

    call. ioa_ ("Entering single character input mode (use ESC or ^C to exit).")
    while True:
        c = wait_get_char()
        
        if c in [ESC, CTRL('C')]:
            break
            
        elif c == CTRL('B'):
            send_control_code("[D") # Cursor Backward
        elif c == CTRL('F'):
            send_control_code("[C") # Cursor Forward
        elif c == CTRL('N'):
            send_control_code("[B") # Cursor Down
        elif c == CTRL('P'):
            send_control_code("[A") # Cursor Up
        else:
            call. ioa_.nnl (c)
        
def wait_get_char():
    tty_channel = get_calling_process_().tty()
    iox_control.echo_input_sw = False
    iox_control.enable_signals_sw = True
    iox_control.filter_chars = []
    buffer = parm()
    call. iox_.wait_get_char (tty_channel, iox_control, buffer)
    return buffer.val

def send_control_code(s):
    call. ioa_.nnl (ESC+s)
    
def get_response(response_terminator):
    response = c = ""
    while c != response_terminator:
        c = wait_get_char()
        response += c
    return response
    