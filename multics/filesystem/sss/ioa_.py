import re

from multics.globals import *
    
def _flatten(l):
    r = []
    for x in l:
        if hasattr(x, '__iter__'):
            y = _flatten(x)
            r.extend(y)
        else:
            r.append(x)
    return r
    
def _edit_string_token(s, N):
    return "%-*s" % (N or 0, s)
    
def _edit_integer_token(i, N):
    return "%*d" % (N or 1, i)
    
def _edit_octal_token(x, N):
    return "%*o" % (N or 1, x)
    
def _edit_octalword_token(x, N):
    return ("%0*o" % (N or 12, x))[:(N or 12)]
    
def _edit_float_token(f, N, D):
    if N is not None and D is not None:
        return "%*.*f" % (N, D, f)
    elif N is not None:
        return "%*f" % (N, f)
    elif D is not None:
        return "%.*f" % (D, f)
    else:
        return "%f" % (f)
    
def _edit_pointer_token(p, N):
    return "|%0*d|" % (N or 12, p)
    
def _edit_repr_token(r, N):
    return "%*r" % (N or 0, r)
    
def _edit_bitstring_token(b, N, D):
    N = N or 0
    D = D or 1
    if D < 3:
        return "%-*r" % (N, b)
    elif D == 3:
        return "%-*o" % (N, b)
    else:
        return "%-*X" % (N, b)

def _ignore_args(args, N):
    if N is None:
        N = 1
    for i in range(N):
        try:
            x = args.pop(0)
            #print "IGNORE:", repr(x)
        except:
            pass
    return ""

def _edit_tabpos_token(string_so_far, N, D):
    s = string_so_far[string_so_far.rfind("\n") + 1:]
    #print "TAB:", repr(s)
    return " " * ((N or 10) - len(s) - 1)
    
def _scan_case_block(clist):
    s  = clist.pop(0)
    s += clist.pop(0)
    while len(clist) > 1 and clist[:2] != ["^","]"]:
        if clist[:2] == ["^","["]:
            s += _scan_case_block(clist)
        else:
            s += clist.pop(0)
    s += clist.pop(0)
    s += clist.pop(0)
    return s
    
def _scan_case_token(clist):
    s = ""
    while len(clist) > 1 and clist[:2] != ["^",";"] and clist[:2] != ["^","]"]:
        if clist[:2] == ["^","["]:
            s += _scan_case_block(clist)
        else:
            s += clist.pop(0)
    clist.pop(0)
    if clist[0] == ";":
        clist.pop(0)
    return s

def _parse_case_token(clist, case_index, args):
    cases = []
    while len(clist) > 1 and clist[0] != "]":
        s = _scan_case_token(clist)
        #print "CASE:", repr(s)
        cases.append(s)
    clist.pop(0)
    #print "Cases:", cases, "***", case_index
    if case_index is True:
        case_index = 0
    elif case_index is False:
        case_index = 1
    else:
        case_index = int(case_index)
    try:
        for t in reversed(list(cases[case_index])):
            clist.insert(0, t)
        return _begin_parse(clist, args)
    except:
        return ""

def _parse_iter_token(clist, args, N):
    s = ""
    clist2 = clist[:]
    if N is None:
        while args:
            clist2 = clist[:]
            len_before = len(args)
            s += _parse_begin(clist2, args)
            if len(args) == len_before:
                break
        clist[:] = clist2
    elif N:
        for i in range(N):
            clist2 = clist[:]
            s += _parse_begin(clist2, args)
        clist[:] = clist2
    else:
        _parse_begin(clist, args)
    return s
    
_REPEATABLE_CHARS = {'/':"\n", '-':"\t", '|':chr(12), 'x':" ", '^':"^"}
    
def _parse_edit_token(string_so_far, clist, args, N=None, D=None):

    c = clist[0]
    
    if c.isdigit() or c == ".":
        while clist and clist[0].isdigit():
            N = (N or 0) * 10 + int(clist.pop(0))
        if clist and clist[0] == ".":
            clist.pop(0)
            while clist and clist[0].isdigit():
                D = (D or 0) * 10 + int(clist.pop(0))
        return _parse_edit_token(string_so_far, clist, args, N, D)
        
    elif len(clist) > 2 and clist[:3] == "v.v":
        N = int(args.pop(0))
        D = int(args.pop(0))
        clist = clist[3:]
        return _parse_edit_token(string_so_far, clist, args, N, D)
        
    elif c == "v":
        if N is None:
            N = int(args.pop(0))
        else:
            D = int(args.pop(0))
        clist.pop(0)
        return _parse_edit_token(string_so_far, clist, args, N, D)
        
    elif c in _REPEATABLE_CHARS:
        clist.pop(0)
        if N == 0: return ""
        return _REPEATABLE_CHARS[c] * (N or 1)
        
    elif c == "a":
        clist.pop(0)
        return _edit_string_token(args.pop(0), N)
        
    elif c == "d" or c == "i":
        clist.pop(0)
        return _edit_integer_token(args.pop(0), N)
        
    elif c == "f":
        clist.pop(0)
        return _edit_float_token(args.pop(0), N, D)
        
    elif c == "o":
        clist.pop(0)
        return _edit_octal_token(args.pop(0), N)
        
    elif c == "w":
        clist.pop(0)
        return _edit_octalword_token(args.pop(0), N)
        
    elif c == "p":
        clist.pop(0)
        return _edit_pointer_token(args.pop(0), N)
        
    elif c == "r":
        clist.pop(0)
        return _edit_repr_token(args.pop(0), N)
        
    elif c == "b":
        clist.pop(0)
        return _edit_bitstring_token(args.pop(0), N, D)
        
    elif c == "s":
        clist.pop(0)
        return _ignore_args(args, N)
        
    elif c == "t":
        clist.pop(0)
        return _edit_tabpos_token(string_so_far, N, D)
        
    elif c == "[":
        #print "String so far:", repr(string_so_far)
        clist.pop(0)
        case_index = args.pop(0)
        return _parse_case_token(clist, case_index, args)
        
    # elif c == "]":
        # print "UNWINDING"
        # return ""
    # elif c == ";":
        # print "NEXT"
        # return ""
    elif c == "(":
        clist.pop(0)
        return _parse_iter_token(clist, args, N)
        
    else:
        return "^"

def _parse_begin(clist, args):
    s = ""
    while clist:
        if clist[0] == "^":
            clist.pop(0)
            
            if clist and clist[0] == "]":
                return s
            
            elif clist and clist[0] == ";":
                clist.pop(0)
                return s

            elif clist and clist[0] == ")":
                clist.pop(0)
                return s
            
            x = _parse_edit_token(s, clist, args)
            #print "TOK:", repr(x), "->", repr(s+x)
            s += x
        else:
            s += clist.pop(0)
    return s
    
def _ioa_parser(fmt, args):
    #print repr(fmt), args
    clist = list(fmt)
    args = _flatten(args)
    return _parse_begin(clist, args)
    
class ioa_(Subroutine):
    def __init__(self):
        super(ioa_, self).__init__(self.__class__.__name__)
        
    def procedure(self, format_string="", *args):
        tty_channel = get_calling_process_().tty()
        GlobalEnvironment.supervisor.llout(self._format(format_string, *args) + "\n", tty_channel)
        
    def nnl(self, format_string="", *args):
        tty_channel = get_calling_process_().tty()
        GlobalEnvironment.supervisor.llout(self._format(format_string, *args), tty_channel)
    
    def rs(self, format_string, return_string, *args):
        return_string.val = self._format(format_string, *args) + "\n"
        
    def rsnnl(self, format_string, return_string, *args):
        return_string.val = self._format(format_string, *args)
    
    def _format(self, format_string, *args):
        if isinstance(format_string, PL1.EnumValue):
            s = repr(format_string)
            
        elif "^" in format_string:
            s = _ioa_parser(format_string, args)
            
        else:
            s = format_string.format(*args)
        # end if
        
        s = re.sub(r"[ \t]+?\n", "\n", s) # remove whitespace preceding a newline
        return s
