from twisted.internet.protocol import ServerFactory
from serverProtocol import *

class ServerLineReceiverFactory(ServerFactory):
    
    def __init__(self, port):
        self.port = port

    def buildProtocol(self, addr):
        addr.port = self.port
        return ServerLineReceiverProtocol()