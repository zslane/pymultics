import re

from multics.globals import *
        
def _rxsub(p, s):
    result = []
    for a in re.split("(%s)" % (re.sub(r"[\(\)]", "", p)), s):
        m = re.match(p, a)
        result.append( (" " * int(m.group(1) or "1")) if m else a )
    # end for
    return "".join(result)
    
def _docond(fmt, *args):
    p = r"\^\[(.+?)\^\]"
    r = "\0%s\0\\1\0"
    s = re.sub(p, r, fmt)
    t = s % args
    x = re.sub("\0False\0.*?\0", "",
        re.sub("\0True\0(.*?)\0", r"\1", t))
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
    return "\n".join(result)

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
            s = re.sub(r"\^/", "\n",
                re.sub(r"\^(\*|\d*)a", r"%-\1s",
                re.sub(r"\^(\*|\d*)d", r"%\1d",
                re.sub(r"\^((?:\*|\d*)\.?(?:\*|\d*))f", r"%\1f",
                _rxsub(r"\^(\d*)x",
                re.sub(r"%", "%%",
                    format_string))))))
            s = _dotabs(_docond(s, *args))
        else:
            s = format_string.format(*args)
        # end if
        return s
