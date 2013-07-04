from twisted.internet.protocol import ServerFactory

from receiverProtocol import *

class MyFileReceiverFactory(ServerFactory):

    def __init__(self, port):
        self.port = port
        self.echoFactory = MultiEchoFactory()
        self.isFirst = True
        self.source = None

    def buildProtocol(self, addr):
        addr.port = self.port
        return MyFileReceiverProtocol(self)