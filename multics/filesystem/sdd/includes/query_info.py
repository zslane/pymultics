
query_info_version_5 = 5

class query_info_structure(object):
    def __init__(self):
        self.version = query_info_version_5
        self.yes_or_no_sw = False
        self.suppress_name_sw = False
        self.suppress_spacing = False
        self.literal_sw = False
        self.prompt_after_explanation = True
        self.explanation = ""
        self.echo_answer_sw = True
        self.repeat_time = 0
