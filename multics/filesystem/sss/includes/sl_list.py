
from multics.pl1types import *

sl_list_version_1 = 1

sl_list = PL1.Structure(
    version    = fixed.binary,
    link       = pointer,
    name_count = fixed.binary,
    names      = Dim(Dynamic.name_count) (char (32)),
)
