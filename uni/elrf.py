from twisted.internet.protocol import ServerFactory
from elrp import *

class ExtendedLineReceiverFactory(ServerFactory):
    
    def __init__(self, port):
        self.port = port

    def buildProtocol(self, addr):
        addr.port = self.port
        return ExtendedLineReceiverProtocol()