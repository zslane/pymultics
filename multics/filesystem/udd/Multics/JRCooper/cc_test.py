
from multics.globals import *

include.iox_control

ESC = chr(27)

def CTRL(s):
    return chr(ord(s.upper()) - 64)
    
def cc_test():
    ESC_prefix = False
    CTRLX_prefix = False
    
    send_esc_code("[c") # Query Device Code
    call. ioa_ (get_response('c').replace(ESC, "<ESC>"))
    send_esc_code("[5n") # Query Device Status
    call. ioa_ (get_response('n').replace(ESC, "<ESC>"))
    send_esc_code("[6n") # Query Cursor Position
    call. ioa_ (get_response('R').replace(ESC, "<ESC>"))
    
    s = "".join(map(chr, range(33, 112)))
    for code in [0, 1, 2, 4, 5, 7]:
        send_esc_code("[0;%dm" % (code))
        call. ioa_ (s)
    send_esc_code("[0m")
    
    send_esc_code("[3;5r")

    call. ioa_ ("Entering single character input mode (use ^C to exit).")
    while True:
        c = wait_get_char()
        
        if ESC_prefix:
            ESC_prefix = False
            if c == 'k':
                send_esc_code("[1K") # Erase (to) Start of Line
            elif c == 'u':
                send_esc_code("[1J") # Erase Up
            elif c == 'z':
                send_esc_code("D") # Scroll Down
            else:
                call. ioa_.nnl ("<ESC> " + c)
                
        elif CTRLX_prefix:
            CTRLX_prefix = False
            if c == 'k':
                send_esc_code("[2K") # Erase Line
            elif c == 'u':
                send_esc_code("[2J") # Erase Screen
            else:
                call. ioa_.nnl ("^X-" + c)
            
        elif c == CTRL('C'):
            break
            
        elif c == CTRL('B'):
            send_esc_code("[D") # Cursor Backward
        elif c == CTRL('F'):
            send_esc_code("[C") # Cursor Forward
        elif c == CTRL('K'):
            send_esc_code("[K") # Erase (to) End of Line
        elif c == CTRL('N'):
            send_esc_code("[B") # Cursor Down
        elif c == CTRL('P'):
            send_esc_code("[A") # Cursor Up
        elif c == CTRL('Z'):
            send_esc_code("M") # Scroll Up
        elif c == CTRL('U'):
            send_esc_code("[J") # Erase Down
        elif c == CTRL('X'):
            CTRLX_prefix = True
        elif c == ESC:
            ESC_prefix = True
        else:
            call. ioa_.nnl (c)
        
def wait_get_char():
    tty_channel = get_calling_process_().tty()
    iox_control.echo_input_sw = False
    iox_control.filter_chars = []
    buffer = parm()
    call. iox_.wait_get_char (tty_channel, iox_control, buffer)
    return buffer.val

def send_esc_code(s):
    call. ioa_.nnl (ESC+s)
    
def get_response(response_terminator):
    response = c = ""
    while c != response_terminator:
        c = wait_get_char()
        response += c
    return response
    