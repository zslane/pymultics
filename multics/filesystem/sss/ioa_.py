import re

from multics.globals import *

_WIDTHFIELD_CHARS = "0123456789.v"
_REPEATABLE_CHARS = {'/':"\n", '|':chr(12), 'x':" ", '^':"^"}
_TABSIZE          = 10

def _NEXT(clist, n=1): return "".join(clist[:n])
    
def _flatten(alist):
    results = []
    for x in alist:
        if type(x) is list:
            results.extend(_flatten(x))
        else:
            results.append(x)
        # end if
    # end for
    return results
    
def _baseN(num, b, numerals="0123456789ABCDEF"): # up to base-16 (hexidecimal)
    return ((num == 0) and "0") or (_baseN(num // b, b).lstrip("0") + numerals[num % b])

def _parse_number(clist):
    #== Return None if there is no leading digit to parse
    if not _NEXT(clist).isdigit():
        return None
    # end if
    n = 0
    while _NEXT(clist).isdigit():
        n = n * 10 + int(clist.pop(0))
    # end while
    return n
    
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
    
def _edit_efloat_token(e, N):
    if N is not None:
        return "%*e" % (N, e)
    else:
        return "%e" % (e)
        
def _edit_pointer_token(p, N):
    return "|%0*d|" % (N or 12, p)
    
def _edit_repr_token(r, N):
    return "%*r" % (N or 0, r)
    
def _edit_bitstring_token(b, N, D):
    N = N or 0
    D = D or 1
    if   D == 1: # base-2 (binary)
        return "%-*r" % (N, b)
    elif D == 2: # base-4 (quarternary)
        return "%-*s" % (N, str(_baseN(int(b), 4)))
    elif D == 3: # base-8 (octal)
        return "%-*o" % (N, b)
    else:        # base-16 (hexideciaml)
        return "%-*X" % (N, b)

def _ignore_args(args, N):
    if N is None:
        N = 1
    # end if
    for i in range(N):
        try:
            x = args.pop(0)
            #print "IGNORE:", repr(x)
        except:
            pass
        # end try
    # end for
    return ""

def _edit_hortab_token(string_so_far, N):
    result_string = string_so_far[string_so_far.rfind("\n") + 1:]
    if N is None: N = 1
    if N == 0: return ""
    s = " " * (_TABSIZE - (len(result_string) % _TABSIZE))
    return s + (" " * ((N - 1) * _TABSIZE))
    
def _edit_tabpos_token(string_so_far, N, D):
    result_string = string_so_far[string_so_far.rfind("\n") + 1:]
    # print "TAB:", repr(result_string), N
    return " " * ((N or _TABSIZE) - len(result_string) - 1)
    
def _scan_case_block(clist):
    #== Scan the block-start token '^['
    result_string  = clist.pop(0)
    result_string += clist.pop(0)
    
    s = _NEXT(clist, 2)
    while clist and s != "^]":
        if s == "^[":
            result_string += _scan_case_block(clist)
        else:
            result_string += clist.pop(0)
        # end if
        s = _NEXT(clist, 2)
    # end while
    
    #== Scan the block-end token '^]'
    if _NEXT(clist) == '^':
        result_string += clist.pop(0)
        if _NEXT(clist) == ']':
            result_string += clist.pop(0)
            
    return result_string
    
def _scan_case_token(clist, args):
    result_string = ""
    
    s = _NEXT(clist, 2)
    while clist and s != "^]":
        #== Case delimiter requires parsing for expansion because of ^N;
        if re.match(r"\^(v|\d*);", "".join(clist)):
            clist.pop(0) # pop the '^'
            #== Expand the ^N;
            clist[0:0] = list(_parse_edit_token(result_string, clist, args))
            break
        elif s == "^[":
            result_string += _scan_case_block(clist)
        else:
            result_string += clist.pop(0)
        # end if
        s = _NEXT(clist, 2)
    # end while
    
    #== Discard the case delimiter '^;' or the '^' part
    #== of the block-end token '^]'
    if _NEXT(clist) == '^':
        clist.pop(0) # pop the '^'
        if _NEXT(clist) == ";":
            clist.pop(0) # pop the ';'
        # else leave the ']' in clist so it'll be found
        #  by the while loop in _parse_case_token
    
    return result_string

def _parse_case_token(clist, case_index, args):
    #== Build a list of case strings; these are unparsed raw
    #== strings separated by the '^;' delimeter token. Only
    #== the 'selected' case string will get parsed.
    cases = []
    while clist and _NEXT(clist) != "]":
        result_string = _scan_case_token(clist, args)
        # print "CASE:", repr(result_string)
        cases.append(result_string)
    # end while
    clist.pop(0) # pop the ']'
    # print "Cases:", cases, "***", case_index
    
    #== Determine the case selection index
    case_select = {'True':0, 'False':1, '"1"b':0, '"0"b':1}.get(str(case_index), int(case_index))
    
    #== Select the case string and insert its characters
    #== to the front of the character list for parsing
    try:
        clist[0:0] = list(cases[case_select])
    except:
        #== If the selection index falls outside the range
        #== of available cases, then don't add any case
        #== string characters for subsequent parsing
        pass
    # end try
    
    return ""

def _parse_iter_by_args(clist, args):
    #== This is an iter block without an iter count, e.g., ^(foo ...^).
    #== We keep iterating until we exhaust all remaining args (unless
    #== the contents of the iter block has no edit tokens that would
    #== consume any args, in which case we only iterate once).
    clist_dup = clist[:]
    result_string = ""
    
    while args:
        clist_dup = clist[:]
        len_before = len(args)
        result_string += _parse_begin(clist_dup, args)
        #== If parsing the contents of the iter block consumed no args,
        #== then only perform one iteration
        if len(args) == len_before:
            break
        # end if
    # end while
    
    clist[:] = clist_dup
    return result_string

def _parse_iter_by_count(clist, args, N):
    #== This is an iter block with an iter count, e.g., ^3(foo ...^)
    clist_dup = clist[:]
    result_string = ""
    
    for i in range(N):
        clist_dup = clist[:]
        args_before = args[:]
        try:
            result_string += _parse_begin(clist_dup, args)
            
        except IndexError:
            #== Ran out of args during iteration; discard that last iteration ==#
            
            #== Pop all characters remaining in clist_dup up to and including
            #== the terminating '^)' token
            while clist_dup and _NEXT(clist_dup, 2) != "^)":
                clist_dup.pop(0)
            # end while
            if _NEXT(clist_dup, 2) == "^)":
                clist_dup.pop(0) ; clist_dup.pop(0)
            # end if
            #== Restore the args that were left before the failed iteration
            args[:] = args_before
        # end try
    # end for
    
    clist[:] = clist_dup
    return result_string

def _parse_iter_and_discard(clist, args):
    #== This is an iter block with an iter count of 0; parse the contents
    #== of the iter block and then just discard it (i.e., return an empty
    #== result string)
    _parse_begin(clist, args)
    return ""

def _parse_iter_token(clist, args, N):
    if N is None:
        return _parse_iter_by_args(clist, args)
    elif N > 0:
        return _parse_iter_by_count(clist, args, N)
    else:
        return _parse_iter_and_discard(clist, args)

def _parse_width_token(clist, args):
    if _NEXT(clist) == "v":
        clist.pop(0)
        return int(args.pop(0))
    elif _NEXT(clist).isdigit():
        return _parse_number(clist)
    else:
        return None

def _parse_edit_token(string_so_far, clist, args, N=None, D=None):

    c = clist[0]
    
    #== Field width/repeat count: ^N, ^N.D, ^N., ^.D, ^v, ^v.v, ^v., ^N.v, ^v.D
    if c in _WIDTHFIELD_CHARS:
        #== Process leading 'v' or number
        N = _parse_width_token(clist, args)
        
        #== Process '.' and subsequent token
        if _NEXT(clist) == ".":
            clist.pop(0)
            #== Process 'v' or number following the '.'
            D = _parse_width_token(clist, args)
        # end if
        
        #== Ignore (discard) '^.'
        if N is None and D is None:
            return ""
            
        return _parse_edit_token(string_so_far, clist, args, N, D)
        
    #== Repeatable chars: ^x, ^/, ^|, ^^
    elif c in _REPEATABLE_CHARS:
        assert (D is None)
        clist.pop(0)
        if N == 0:
            return ""
        # end if
        return _REPEATABLE_CHARS[c] * (N or 1)
        
    #== Horizontal tab: ^-
    elif c == "-":
        assert (D is None)
        clist.pop(0)
        return _edit_hortab_token(string_so_far, N)
        
    #== Ascii string: ^a
    elif c == "a":
        assert (D is None)
        clist.pop(0)
        return _edit_string_token(args.pop(0), N)
        
    #== Integer: ^d, ^i
    elif c == "d" or c == "i":
        assert (D is None)
        clist.pop(0)
        return _edit_integer_token(args.pop(0), N)
        
    #== Float: ^f
    elif c == "f":
        clist.pop(0)
        return _edit_float_token(args.pop(0), N, D)
        
    #== Scientific notation float: ^e
    elif c == "e":
        assert (D is None)
        clist.pop(0)
        return _edit_efloat_token(args.pop(0), N)
        
    #== Octal integer: ^o
    elif c == "o":
        assert (D is None)
        clist.pop(0)
        return _edit_octal_token(args.pop(0), N)
        
    #== Octal 'word': ^w
    elif c == "w":
        assert (D is None)
        clist.pop(0)
        return _edit_octalword_token(args.pop(0), N)
        
    #== Pointer: ^p
    elif c == "p":
        assert (D is None)
        clist.pop(0)
        return _edit_pointer_token(args.pop(0), N)
        
    #== Python repr(): ^r
    elif c == "r":
        assert (D is None)
        clist.pop(0)
        return _edit_repr_token(args.pop(0), N)
        
    #== Bitstring: ^b
    elif c == "b":
        clist.pop(0)
        return _edit_bitstring_token(args.pop(0), N, D)
        
    #== Arg ignore: ^s
    elif c == "s":
        assert (D is None)
        clist.pop(0)
        return _ignore_args(args, N)
        
    #== Tab postion: ^t
    elif c == "t":
        clist.pop(0)
        return _edit_tabpos_token(string_so_far, N, D)
        
    #== Case selection: ^[^]
    elif c == "[":
        #print "String so far:", repr(string_so_far)
        assert (N is None and D is None)
        clist.pop(0)
        case_index = args.pop(0)
        return _parse_case_token(clist, case_index, args)
        
    #== Case delimiter: ^;
    elif c == ";":
        assert (D is None)
        clist.pop(0)
        return "^;" * (N or 1)
        
    #== Iteration: ^(^)
    elif c == "(":
        assert (D is None)
        clist.pop(0)
        return _parse_iter_token(clist, args, N)
        
    else:
        return "^"

def _parse_begin(clist, args):
    result_string = ""
    while clist:
        if _NEXT(clist) == "^":
            clist.pop(0)
            
            #== Terminate recursive call from parsing an iter block
            if _NEXT(clist) == ")":
                clist.pop(0)
                return result_string
            # end if
            
            s = _parse_edit_token(result_string, clist, args)
            #print "TOK:", repr(s), "->", repr(result_string + s)
            result_string += s
        else:
            result_string += clist.pop(0)
        # end if
    # end while
    return result_string
    
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
        call.iox_.write(tty_channel, self._format(format_string, *args) + "\n")
        
    def nnl(self, format_string="", *args):
        tty_channel = get_calling_process_().tty()
        call.iox_.write(tty_channel, self._format(format_string, *args))
    
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
