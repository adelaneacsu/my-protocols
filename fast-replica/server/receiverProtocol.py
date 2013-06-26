import logging

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor, defer

from multiEcho import *


class MyFileReceiverProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.MAX_LENGTH = 524288010

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
            print line
            data = line.strip().split(' ')
            if data[0] == 'PTH':
                self.factory.dstpath = data[1]
                logging.info('File %s opened for writing. Raw mode set.' % self.factory.dstpath)

            elif data[0] == 'PKs':
                self.factory.nrPackages = int(data[1])
                self.factory.packetSize = int(data[2])
                self.factory.nrOutConn = 0
                self.factory.buffer = ["" for x in range(self.factory.nrPackages)]
                self.factory.toReceive = self.factory.nrPackages

            elif data[0] == 'IDx':
                self.factory.index = int(data[1])
                self.factory.originalReceived = False
                self.factory.allConnected = False
                self.factory.dstpath = self.factory.dstpath + data[1]

            elif data[0] == 'N':
                IP = data[1]
                port = int(data[2])
                endpoint = TCP4ClientEndpoint(reactor, IP, port)
                endpoint.connect(self.factory.echoFactory).addCallback(self._addNeighbour)
                if len(data) == 4 and data[3] == 'DN':
                    self.sendLine('GO')

            elif data[0] == 'NON':
                self.sendLine('GO')                

    def rawDataReceived(self, rawData):
        # write to buffer
        index = int(rawData[1])
        self.factory.buffer[index] = rawData[2:]
        print 'RAW nr. %d size %d' % (index, len(self.factory.buffer[index]))
        self.factory.toReceive -= 1
        if index == self.factory.index:
            self.factory.originalReceived = True
        # forward original package
        
        if self.factory.isFirst and self.factory.allConnected and (self.factory.originalReceived):
            for echoer in self.factory.echoFactory.echoers:
                echoer.sendLine('-' + str(self.factory.index) + self.factory.buffer[self.factory.index])
            self.factory.isFirst = False
        # check if there are any other packages
        if self.factory.toReceive == 0:
            fileObj = open(self.factory.dstpath, 'wb')
            for buff in self.factory.buffer:
                fileObj.write(buff)
            fileObj.close()
            # disconnect from neighbours and announce source you got all data
            self.factory.source.sendLine('DN')
            self.factory.source.transport.loseConnection()
            for echoer in self.factory.echoFactory.echoers:
                echoer.transport.loseConnection()
        logging.info('Received %d bytes.' % len(rawData))

    def lineLengthExceeded(self, line):
        print 'LINE EXCEEDED'

    def _addNeighbour(self, deff):
        self.factory.nrOutConn += 1
        if (self.factory.nrOutConn == self.factory.nrPackages - 2):
            self.factory.allConnected = True