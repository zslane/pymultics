
from multics.globals import *

class sst_(Subroutine):

    def __init__(self):
        super(sst_, self).__init__(self.__class__.__name__)

    def set_up_game(self, NODE, game_length, difficulty):
        call. ioa_ ("NODE: ^r^/game_length:^-^d^/difficulty:^-^d", NODE, game_length, difficulty)
        
    def print_introduction(self, NODE, last_name):
        call. ioa_ ("last_name:^-^a", last_name)
        
    def daemon(self):
        pass
        