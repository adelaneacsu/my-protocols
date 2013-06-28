
from twisted.internet.protocol import ClientFactory

from clientProtocol import *

class MyClientFactory(ClientFactory):
    
    def __init__(self, callback, sourceFile, destFile, packetSize, windowSize, destinations):
        self.callback       = callback
        self.sourceFile     = sourceFile
        self.destFile       = destFile
        self.destinations   = destinations
        self.packetSize     = packetSize
        self.windowSize     = windowSize
    
    def buildProtocol(self, addr):
        return MyClientProtocol(self)

    def startedConnecting(self, connector):
        msg = 'Connected to source server.'
        logging.info(msg)

    def clientConnectionFailed(self, connector, reason):
        msg = 'Connection to source server FAILED.'
        logging.info(msg)

    def clientConnectionLost(self, connector, reason):
        msg = 'Connection to source server lost.'
        logging.info(msg)