from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver

class MultiEchoProtocol(LineReceiver):
    
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        if __debug__:
            print 'Connection in echo ===: %s' % self.transport.getPeer()
        self.factory.parent.proto._newConnection()
        self.factory.echoers.append(self)

    def connectionLost(self, reason):
        self.factory.echoers.remove(self)

    def lineReceived(self, line):
        if __debug__:
            print 'echo = %s %s' % (line ,self.transport.getPeer())
        data = line.strip().split(' ')
        if data[0] == 'CHRA':
            self.factory.parent.source.sendLine('RECA')