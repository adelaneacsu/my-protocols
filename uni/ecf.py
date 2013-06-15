
from twisted.internet.protocol import ClientFactory

from cp import *

class ExtendedClientFactory(ClientFactory):
    
    def __init__(self, parent, destIP, sourceFile, destFile, nos, streams, serverType):
        self.parent     = parent
        self.destIP     = destIP
        self.sourceFile = sourceFile
        self.destFile   = destFile
        self.nos        = nos
        self.streams    = streams
        self.serverType = serverType

    def buildProtocol(self, addr):
        return ClientProtocol(self.parent, self.destIP, self.sourceFile, self.destFile, self.nos, self.streams, self.serverType)

    def startedConnecting(self, connector):
        msg = 'Connected to ' + ['destination', 'source'][self.serverType == 'S'] + ' server.'
        log_message(msg)
        print msg

    def clientConnectionFailed(self, connector, reason):
        msg = 'Connecion to ' + ['destination', 'source'][self.serverType == 'S'] + ' server FAILED.'
        log_message(msg)
        print msg

    def clientConnectionLost(self, connector, reason):
        msg = 'Connection to ' + ['destination', 'source'][self.serverType == 'S'] + ' server lost.'
        log_message(msg)
        print msg