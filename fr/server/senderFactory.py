from twisted.internet.protocol import ServerFactory

from senderProtocol import *

class MyFileSenderFactory(ServerFactory):
    
    def __init__(self, parent, index):
        self.parent = parent
        self.index = index

    def buildProtocol(self, addr):
        return MyFileSenderProtocol(self.parent, self.index)