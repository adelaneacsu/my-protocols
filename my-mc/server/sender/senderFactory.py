from twisted.internet.protocol import ServerFactory
from senderProtocol import *

class MySenderFactory(ServerFactory):
    
    def __init__(self, port):
        self.port = port

    def buildProtocol(self, addr):
        addr.port = self.port
        return MySenderProtocol()