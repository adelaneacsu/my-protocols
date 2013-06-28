from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver

class MultiEchoProtocol(LineReceiver):
    
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.echoers.append(self)

    def connectionLost(self, reason):
        self.factory.echoers.remove(self)

    def lineReceived(self, line):
        print 'echo = %s %d' % (line ,self.transport.getPeer().port)
        data = line.strip().split(' ')
        if data[0] == 'CHRA':
            self.factory.parent.source.sendLine('RECA')