from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

class MultiEcho(LineReceiver):
    
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.echoers.append(self)

    def lineReceived(self, line):
        print 'LINE in MultiEcho: '
        print line
        
    def rawDataReceived(self, rawData):
        print 'RAW in MultiEcho: '
        print rawData


    def connectionLost(self, reason):
        self.factory.echoers.remove(self)


class MultiEchoFactory(Factory):
    
    def __init__(self):
        self.echoers = []

    def buildProtocol(self, addr):
        return MultiEcho(self)