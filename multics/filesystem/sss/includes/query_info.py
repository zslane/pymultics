
from multics.pl1types import PL1

query_info_version_5 = 5

class query_info_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            version                  = query_info_version_5,
            yes_or_no_sw             = False,
            suppress_name_sw         = False,
            suppress_spacing         = False,
            literal_sw               = False,
            prompt_after_explanation = True,
            explanation              = "",
            echo_answer_sw           = True,
            repeat_time              = 0,
        )
