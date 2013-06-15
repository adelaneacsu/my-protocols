from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

class MultiEcho(LineReceiver):
    
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.echoers.append(self)

    def lineReceived(self, line):
        self.factory.parent.source.sendLine(line)
        if len(self.factory.echoers) == 0:
            self.factory.parent.source.loseConnection()
            for echoer in self.factory.echoers:
                echoer.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.echoers.remove(self)

class MultiEchoFactory(Factory):
    
    def __init__(self, parent):
        self.echoers = []
        self.parent = parent

    def buildProtocol(self, addr):
        return MultiEcho(self)