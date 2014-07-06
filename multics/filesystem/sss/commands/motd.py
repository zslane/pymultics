
from multics.globals import *

def motd():
    f = open(vfile_(">sc1>motd.info"))
    file_text = f.read()
    f.close()
    call.ioa_(file_text)
    