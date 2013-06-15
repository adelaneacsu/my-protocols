import logging

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor, defer

from multiEcho import *


class MyDestinationProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        if self.factory.source is None:
            self.factory.source = self
        logging.info('Connection made: %s' % self.transport.getPeer())

    def connectionLost(self, reason):
        if self.factory.source == self:
            self.factory.source = None
        logging.info('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        if line[0] == '-':
            return self.rawDataReceived(line)
        else:
            print 'SD: %s' % line
            data = line.strip().split(' ')
            if data[0] == 'PTH' and self.factory.source == self:
                self.factory.dstpath = data[1]
                logging.info('File %s opened for writing. Raw mode set.' % self.factory.dstpath)
                for echoer in self.factory.echoFactory.echoers:
                    echoer.sendLine(line)

            elif data[0] == 'PKs' and self.factory.source == self:
                self.factory.nrPackages = int(data[1])
                self.factory.packetSize = int(data[2])
                self.factory.buffer = ["" for x in range(self.factory.nrPackages)]
                self.factory.toReceive = self.factory.nrPackages
                for echoer in self.factory.echoFactory.echoers:
                    echoer.sendLine(line)

            elif data[0] == 'NC':
                self.factory.nrConn = int(data[1])
                if self.factory.nrConn == 1:
                    self.sendLine('CON')

            elif data[0] == 'CON':
                IP = data[1]
                port = int(data[2])
                endpoint = TCP4ClientEndpoint(reactor, IP, port)
                endpoint.connect(self.factory.echoFactory).addCallback(self._newConn)

    def rawDataReceived(self, rawData):
        # write to buffer
        ln = rawData.index('-', 1)
        index = int(rawData[1:ln])
        self.factory.buffer[index] = rawData[ln+1:]
        self.factory.toReceive -= 1
        
        if self.factory.source == self:
            for echoer in self.factory.echoFactory.echoers:
                echoer.sendLine(rawData)

        if self.factory.toReceive == 0:
            fileObj = open(self.factory.dstpath, 'wb')
            for buff in self.factory.buffer:
                fileObj.write(buff)
            fileObj.close()
            self.factory.source.sendLine('DN')
        logging.info('Received %d bytes.' % len(rawData))

    def _newConn(self, deffered):
        if len(self.factory.echoFactory.echoers) == self.factory.nrConn - 1:
            self.sendLine('CON')
        elif len(self.factory.echoFactory.echoers) == self.factory.nrConn:
            self.sendLine('GO')

class MyDestinationFactory(ServerFactory):

    def __init__(self, port):
        self.port = port
        self.echoFactory = MultiEchoFactory(self)
        self.source = None

    def buildProtocol(self, addr):
        addr.port = self.port
        return MyDestinationProtocol(self)