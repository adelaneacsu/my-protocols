from twisted.internet.protocol import ServerFactory

from receiverProtocol import *

class MyReceiverFactory(ServerFactory):

    def __init__(self, port):
        self.echoFactory    = MultiEchoFactory(self)
        self.source         = None

    def buildProtocol(self, addr):
        return MyReceiverProtocol(self)