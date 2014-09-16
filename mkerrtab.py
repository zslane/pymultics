import os
import re
import sys
import pprint

CUSTOM_ERROR_CODES = [

    ("no_such_user",              "Unknown user."),
    ("fileioerr",                 "Error processing file."),
    ("no_directory_entry",        "No such file or directory."),
    ("no_command_name_available", "No command name available."),
    
]

DOUBLE_QUOTE_TOKEN = chr(1)

def _strip_comments(s):
    #== Replace double quotes with special token
    s = s.replace('""', DOUBLE_QUOTE_TOKEN)
    #== Any remaining quotation mark indicates the beginning of a comment (to end of line)
    pos = s.find('"')
    if pos != -1:
        s = s[:pos].strip()
    else:
        s = s.strip()
    # end if
    #== Replace special token with single quotation mark (appropriate for a python string)
    return s.replace(DOUBLE_QUOTE_TOKEN, '"')
    
def valid_chars(s):
    return re.match(r"^[A-Za-z0-9_]+$", s) != None
    
def decode_cmp_chars(s):
    decode_table = [
        ("^=", "NE"),
        ("^", "NOT"),
        (">", "GT"),
        ("<", "LT"),
        ("=", "EQ"),
    ]
    for a, b in decode_table:
        s = s.replace(a, b)
    # end for
    return s.strip()
    
out_txt_begin = \
"""
from pl1types import PL1
class ErrorTable(PL1.Enum):
    def __init__(self, name):
        PL1.Enum.__init__(self, name)
        self._messages = \\
"""

def main():
    in_path = os.path.join(os.getcwd(), "error_table_.alm")
    out_path = os.path.join(os.getcwd(), "error_table.py")
    
    error_table = {}
    error_messages = {}
    current_code = -1001
    
    #== Inject custom error codes
    for custom_code_symbol, error_text in CUSTOM_ERROR_CODES:
        error_table[frozenset([custom_code_symbol])] = current_code
        error_messages[current_code] = error_text
        current_code -= 1
    # end for
    
    fetch_text = False
    error_codes = []
    
    #== Read error_table_.alm file
    with open(in_path, "r") as in_file:
        for line in in_file:
            line = _strip_comments(line)
            m = re.match(r"ec\s+(.*)", line)
            if m:
                error_codes = frozenset(filter(None, map(str.strip, re.sub(r"[\(\)]", "", m.group(1)).split(","))))
                fetch_text = True
            elif fetch_text and error_codes:
                m = re.match(r"\((.*)\)", line)
                if m:
                    error_text = m.group(1).strip()
                    error_table[error_codes] = current_code
                    error_messages[current_code] = error_text
                    current_code -= 1
                # end if
                fetch_text = False
                error_codes = []
            # end if
        # end for
    # end with
    
    #== Write error_table.py file
    with open(out_path, "w") as out_file:
        out_file.write(out_txt_begin)
        out_file.write("%s\n\n" % (pprint.pformat(error_messages, indent=8)))
        for error_codes, errcode in sorted(error_table.items(), key=lambda (k, v): v, reverse=True):
            for code in error_codes:
                out_file.write("        self.%s = PL1.EnumValue(name, %r, %d)\n" % (decode_cmp_chars(code), code, errcode))
            # end for
        # end for
    # end with
    
#-- end def main

if __name__ == "__main__":
    main()
