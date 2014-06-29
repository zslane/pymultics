
from multics.globals import *

class test_(Subroutine):
    def __init__(self):
        super(test_, self).__init__(self.__class__.__name__)

    def procedure(self):
        call.ioa_("test_() successfully called")
        
    def func1(self):
        call.ioa_("test_.func1() successfully called")
        
    def func2(self, x):
        return x * x
        