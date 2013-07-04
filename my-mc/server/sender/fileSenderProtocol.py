import os
import logging

from multiprocessing.connection import Client
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver


class MyFileSenderProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.sendLine('SCHM ' + str(len(self.factory.children)))
        for child in self.factory.children:
            self.sendLine('CHLD ' + child[0] + ' ' + str(child[1]))
        logging.info('Connection made: %s' % self.transport.getPeer())

    def connectionLost(self, reason):
        logging.info('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        print 'fs = %s %s' % (line ,self.transport.getPeer().host)
        data = line.strip().split(' ')
        if data[0] == 'CONN':
            # send configurations
            self.sendLine('FPTH ' + self.factory.parent.dstpath)
            nrPackets = self.factory.parent.fileSize / self.factory.parent.packetSize
            if self.factory.parent.fileSize % self.factory.parent.packetSize != 0:
                nrPackets += 1
            self.sendLine('PACK ' + str(nrPackets) + ' ' + str(self.factory.parent.packetSize))
            self.sendLine('WDSZ ' + str(self.factory.parent.windowSize))
            self.sendLine('SIBL ' + self.factory.sibling[0] + ' ' + str(self.factory.sibling[1]))

        elif data[0] == 'SEND':
            # server received configurations, now is asking for data
            packet = self.factory.parent._getPacketById(self.factory.parity)
            k = 2
            while packet != -1:
                self.sendLine(packet)
                packet = self.factory.parent._getPacketById(self.factory.parity + k)
                k += 2
            self.sendLine('REQC')

        elif data[0] == 'NREC':
            # at least one packet did not arrive to the destination, resend it        
            packet = self.factory.parent._getPacketById(int(data[1]))
            self.sendLine(packet)
            self.sendLine('REQC')
            
        elif data[0] == 'RECA':
            # all file was received
            self.factory.parent._incFileDone(self)