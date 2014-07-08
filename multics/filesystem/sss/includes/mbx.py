
class Mailbox(object):

    def __init__(self):
        self.messages = []
        self.states = set()
        
    def __repr__(self):
        return "<Mailbox states: %s\n       messages: %s>" % (str(self.states), str(self.messages))
        
    def has_state(self, state):
        return state in self.states
        
    def set_state(self, state):
        self.states.add(state)
        
    def remove_state(self, state):
        self.states.discard(state)
        
    def add_message(self, message):
        self.messages.append(message)
    
#-- end class Mailbox
