
from twisted.internet.protocol import ClientFactory

from clientProtocol import *

class MyClientFactory(ClientFactory):
    
    def __init__(self, parent, sourceFile, destFile, clients):
        self.parent     = parent
        self.sourceFile = sourceFile
        self.destFile   = destFile
        self.clients    = clients
    
    def buildProtocol(self, addr):
        return MyClientProtocol(self.parent, self.sourceFile, self.destFile, self.clients)

    def startedConnecting(self, connector):
        msg = 'Connected to source server.'
        logging.info(msg)
        print msg

    def clientConnectionFailed(self, connector, reason):
        msg = 'Connecion to source server FAILED.'
        logging.info(msg)
        print msg

    def clientConnectionLost(self, connector, reason):
        msg = 'Connection to source server lost.'
        logging.info(msg)
        print msg