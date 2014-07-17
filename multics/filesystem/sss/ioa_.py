import re

from multics.globals import *
    
def _r_sub(p, c, s):
    result = []
    for a in re.split("(%s)" % (re.sub(r"[\(\)]", "", p)), s):
        m = re.match(p, a)
        result.append( (c * int(m.group(1) or "1")) if m else a )
    # end for
    return "".join(result)
    
def _docase(fmt, *args):
    #print "1.", fmt
    p_w_brackets = r"(\^\[(?:.+?|(?:.+?(?:\^;.+?)*))\^\])"
    #p_wo_brackets = r"\^\[(.+?|(?:.+?(?:\^;.+?)*))\^\]"
    r = "\0%s\0\\1\0"
    s = re.sub(p_w_brackets, r, fmt)
    #print "2.", repr(s)
    t = s % args
    #print "3.", repr(t)
    t = re.sub("\0False\0", "\0"+"1"+"\0",
        re.sub("\0True\0",  "\0"+"0"+"\0", t)) # support Python bools
    x = re.sub('\0"0"b\0',  "\0"+"1"+"\0",
        re.sub('\0"1"b\0',  "\0"+"0"+"\0", t)) # support PL1 bit(1)
    #print "4.", repr(x)
    p_split_on_brackets = "(\0\d+?\0" + r"\^\[(?:.+?|(?:.+?(?:\^;.+?)*))\^\]" + "\0)"
    p_find_bracket_innards = "\0(\d+?)\0" + r"\^\[(.+?|(?:.+?(?:\^;.+?)*))\^\]" + "\0"
    result = []
    l = re.split(p_split_on_brackets, x)
    #print "5.", l
    for a in l:
        m = re.match(p_find_bracket_innards, a)
        if m:
            #print "6.", m.groups()
            N = int(m.group(1))
            b = re.split(r"\^;", m.group(2))
            if -1 < N < len(b):
                result.append(b[N])
        else:
            result.append(a)
    return "".join(result)
    
def _doiter0(s, *args):
    result = []
    l = re.split(r"(\^\(.*?\^\))", s)
    for s in l:
        t = re.findall(r"%.*?\w", s)
        N = 1
        if t:
            N = len(args) / len(t)
        m = re.match(r"\^\((.*)\^\)", s)
        if m:
            s = m.group(1) * N
        result.append(s)
    return "".join(result)

def _doiter(s):
    result = []
    for t in re.split(r"(\^\d+\(.*?\^\))", s):
        m = re.match(r"\^(\d+)\((.*?)\^\)", t)
        if m:
            N = max(0, int(m.group(1)))
            result.append(m.group(2) * N)
        else:
            result.append(t)
    return "".join(result)
    
# def _docond(fmt, *args):
    # p = r"\^\[(.+?)\^\]"
    # r = "\0%s\0\\1\0"
    # s = re.sub(p, r, fmt)
    # t = s % args
    # x = re.sub("\0False\0.+?\^;(.+?)\0", r"\1",
        # re.sub("\0True\0(.+?)\^;.+?\0",  r"\1", t))
    # x = re.sub("\0False\0.+?\0",         r"",
        # re.sub("\0True\0(.+?)\0",        r"\1", x))
    # return x
    
def _dotabs(s, default_tab_stop=10):
    result = []
    for s in s.split("\n"):
        next_default, t = default_tab_stop, ""
        for x in re.split(r"(\^\d*t)", s):
            m = re.match(r"\^(\d*)t", x)
            if m:
                t += " " * (int(m.group(1) or str(next_default)) - len(t) - 1)
                next_default += default_tab_stop
            else:
                t += x
            # end if
        # end for
        result.append(t)
    # end for
    return ("\n".join(result)).expandtabs(default_tab_stop)

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
            #== Order of execution is critial! ==#
            
            #== First, turn single '%' signs into double '%%' signs...
            s = re.sub(r"(?<!%)%(?!%)",             r"%%",    format_string)
            #== ...next: prep repeating characters via ^v
            s = re.sub(r"\^v-",                     r"^%d-",  s) # ^v-
            s = re.sub(r"\^vx",                     r"^%dx",  s) # ^vx
            s = re.sub(r"\^v/",                     r"^%d/",  s) # ^v/
            s = re.sub(r"\^v\|",                    r"^%d|",  s) # ^v|
            s = re.sub(r"\^v\^",                    r"^%d^",  s) # ^v^
            s = re.sub(r"\^v\(",                    r"^%d(",  s) # ^v(
            #== ...next: convert arg-based field width token
            s = re.sub(r"(?<=\^)v|(?<=\^v\.)v",     r"*",     s) # ^v , ^v.v
            #== ...next: ioa_ tokens that map directly to Python tokens
            s = re.sub(r"\^((\*|\d*)\.?(\*|\d*))f", r"%\1f",  s) # ^N.Df
            s = re.sub(r"\^(\*|\d*)e",              r"%\1e",  s) # ^Ne
            s = re.sub(r"\^(\*|\d*)(d|i)",          r"%\1d",  s) # ^Nd , ^Ni
            s = re.sub(r"\^(\*|\d*)(o|w)",          r"%\1o",  s) # ^No , ^Nw
            s = re.sub(r"\^(\*|\d*)r",              r"%\1r",  s) # ^Nr (not originally an ioa_ token)
            s = re.sub(r"\^(\*|\d*)a",              r"%-\1s", s) # ^Na
            s = re.sub(r"\^(\*|\d*)p",              r"|%0\1d|",s) # ^Np
            s = re.sub(r"\^(\*|\d*)(\.1)?b",        r"%-\1r", s) # ^Nb , ^N.1b
            s = re.sub(r"\^(\*|\d*)\.3b",           r"%\1o",  s) # ^N.3b
            s = re.sub(r"\^(\*|\d*)\.4b",           r"%\1X",  s) # ^N.4b
            s = re.sub(r"\^(\*|\d*)\.\d+b",         r"%\1X",  s) # ^N.Db (where D > 4)
            #== ...next: iteration and conditional/case-selection expansion
            s = _doiter0(s, *args)                               # expand ^(^) by *args
            s = _docase(s, *args)                                # apply *args and ^[^]
            s = _doiter(s)                                       # ^N(^)
            #== ...next: repeating character expansion
            s = _r_sub(r"\^(\d*)\-",                 "\t",    s) # ^N-
            s = _r_sub(r"\^(\d*)x",                  " ",     s) # ^Nx
            s = _r_sub(r"\^(\d*)/",                  "\n",    s) # ^N/
            s = _r_sub(r"\^(\d*)\|",                 chr(12), s) # ^N|
            s = _r_sub(r"\^(\d*)\^",                 "^",     s) # ^N^
            #== ...next: explicit tab positioning
            s = _dotabs(s)                                       # ^Nt
            
        else:
            s = format_string.format(*args)
        # end if
        
        s = re.sub(r"[ \t]+?\n", "\n", s) # remove whitespace preceding a newline
        return s
