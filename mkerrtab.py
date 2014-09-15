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

def _strip_comments(s):
    pos = s.find('"')
    if pos != -1:
        return s[:pos].strip()
    else:
        return s.strip()
        
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
    return s
    
def main():
    in_path = os.path.join(os.getcwd(), "error_table_.alm")
    out_path = os.path.join(os.getcwd(), "error_table.py")
    
    error_table = {}
    error_messages = {}
    current_code = -4
    
    for custom_code, error_text in CUSTOM_ERROR_CODES:
        error_table[custom_code] = {
            'errcode': current_code,
            'aliases': [],
        }
        error_messages[current_code] = error_text
        current_code -= 1
    # end for
    
    fetch_text = False
    error_codes = []
    
    with open(in_path, "r") as in_file:
        for line in in_file:
            line = _strip_comments(line)
            m = re.match(r"ec\s+(.*)", line)
            if m:
                error_codes = map(decode_cmp_chars, filter(None, re.split(r",\s*", re.sub(r"[\(\)]", "", m.group(1)))))
                fetch_text = True
            elif fetch_text and error_codes:
                m = re.match(r"\((.*)\)", line)
                if m:
                    error_text = m.group(1)
                    main_code = error_codes.pop(0)
                    error_table[main_code] = {
                        'errcode': current_code,
                        'aliases': error_codes,
                    }
                    error_messages[current_code] = error_text
                    current_code -= 1
                # end if
                fetch_text = False
                error_codes = []
            # end if
        # end for
    # end with
    
    with open(out_path, "w") as out_file:
        out_file.write("""
from pl1types import PL1
class ErrorTable(PL1.Enum):
    def __init__(self, name):
        PL1.Enum.__init__(self, name)
        self._messages = \\
""")
        out_file.write("%s\n" % (pprint.pformat(error_messages, indent=4)))
        
        for main_code, error_info in sorted(error_table.items(), key=lambda (k, v): v['errcode'], reverse=True):
            errcode = error_info['errcode']
            error_codes = [main_code] + error_info['aliases']
            for code in error_codes:
                out_file.write("        self.%s = PL1.EnumValue(name, %r, %d)\n" % (code, code, errcode))
            # end for
        # end for
        
if __name__ == "__main__":
    main()
