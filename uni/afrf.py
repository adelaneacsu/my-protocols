from twisted.internet.protocol import ServerFactory
from afrp import *

class AnonymousFileReceiverFactory(ServerFactory):
    
    def __init__(self, parent, filepath):
        self.parent = parent
        self.filepath = filepath

    def buildProtocol(self, addr):
        return AnonymousFileReceiverProtocol(self.parent, self.filepath)