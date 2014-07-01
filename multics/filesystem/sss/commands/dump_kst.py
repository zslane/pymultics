from pprint import pprint

from multics.globals import *

@system_privileged
def dump_kst():
    print "KNOWN SEGMENT TABLE:"
    pprint(supervisor.dynamic_linker.known_segment_table)
    