import re

from multics.globals import *
        
def _doswitch(fmt, *args):
    p = r"(\^\[.+?(?:\^;.+?)\^\])"
    r = "\0%s\0\\1"
    s = re.sub(p, r, fmt)
    t = s % args
    x = re.sub("False", "1",
        re.sub("True",  "0", t))
    p2 = "(\0\d+?\0" + r"\^\[.+?(?:\^;.+?)\^\])"
    p3 = "\0(\d+?)\0" + r"\^\[(.+?(?:\^;.+?))\^\]"
    result = []
    for a in re.split(p2, x):
        m = re.match(p3, a)
        if m:
            N = int(m.group(1))
            b = re.split(r"\^;", m.group(2))
            if -1 < N < len(b):
                result.append(b[N])
        else:
            result.append(a)
    return "".join(result)
    
def _r_sub(p, c, s):
    result = []
    for a in re.split("(%s)" % (re.sub(r"[\(\)]", "", p)), s):
        m = re.match(p, a)
        result.append( (c * int(m.group(1) or "1")) if m else a )
    # end for
    return "".join(result)
    
def _docond(fmt, *args):
    p = r"\^\[(.+?)\^\]"
    r = "\0%s\0\\1\0"
    s = re.sub(p, r, fmt)
    t = s % args
    x = re.sub("\0False\0.+?\^;(.+?)\0", r"\1",
        re.sub("\0True\0(.+?)\^;.+?\0",  r"\1", t))
    x = re.sub("\0False\0.+?\0",         r"",
        re.sub("\0True\0(.+?)\0",        r"\1", x))
    return x
    
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
            #== ...next
            s = re.sub(r"\^v-",                     r"^%d-",  s) # ^v-
            s = re.sub(r"\^vx",                     r"^%dx",  s) # ^vx
            s = re.sub(r"\^v/",                     r"^%d/",  s) # ^v/
            #== ...next
            s = re.sub(r"(?<=\^)v|(?<=\^v\.)v",     r"*",     s) # ^v , ^v.v
            #== ...next
            s = re.sub(r"\^((\*|\d*)\.?(\*|\d*))f", r"%\1f",  s) # ^N.Df
            s = re.sub(r"\^(\*|\d*)[d|i]",          r"%\1d",  s) # ^Nd , ^Ni
            s = re.sub(r"\^(\*|\d*)e",              r"%\1e",  s) # ^Ne
            s = re.sub(r"\^(\*|\d*)o",              r"%\1o",  s) # ^No
            s = re.sub(r"\^(\*|\d*)a",              r"%-\1s", s) # ^Na
            #== ...next
            s = _docond(s, *args)                                # apply *args and ^[^]
            #== ...next
            s = _r_sub(r"\^(\d*)\-",                 "\t",    s) # ^N-
            s = _r_sub(r"\^(\d*)x",                  " ",     s) # ^Nx
            s = _r_sub(r"\^(\d*)/",                  "\n",    s) # ^N/
            #== ...next
            s = _dotabs(s)                                       # ^Nt
            
        else:
            s = format_string.format(*args)
        # end if
        
        s = re.sub(r"[ \t]+?\n", "\n", s) # remove whitespace preceding a newline
        return s
