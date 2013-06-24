from twisted.internet.protocol import ServerFactory
from afrp import *

class AnonymousFileReceiverFactory(ServerFactory):
    
    def __init__(self, parent, filepath):
    	print 'another ServerFactory'
        self.parent = parent
        self.filepath = filepath

    def buildProtocol(self, addr):
    	print 'buile receiver protocol'
        return AnonymousFileReceiverProtocol(self.parent, self.filepath)