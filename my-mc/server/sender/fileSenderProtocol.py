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
        self.sendLine('SIBL ' + self.factory.sibling[0] + ' ' + str(self.factory.sibling[1]))
        for child in self.factory.children:
            self.sendLine('CHLD ' + child[0] + ' ' + str(child[1]))
        logging.info('Connection made: %s' % self.transport.getPeer())

    def connectionLost(self, reason):
        logging.info('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        #print 'fs = %s %d' % (line ,self.transport.getPeer().port)
        data = line.strip().split(' ')
        if data[0] == 'CONN':
            # get configuration data
            if self.factory.parent._getConfigurations(self.factory.groupNr) == 1:
                # first connected
                self.sendLine('FPTH ' + self.factory.parent.dstpath)
                nrPackets = self.factory.parent.fileSize / self.factory.parent.packetSize
                if self.factory.parent.fileSize % self.factory.parent.packetSize != 0:
                    nrPackets += 1
                self.sendLine('PACK ' + str(nrPackets) + ' ' + str(self.factory.parent.packetSize))
                self.sendLine('WDSZ ' + str(self.factory.parent.windowSize))

        elif data[0] == 'SEND':
            # server received configurations, now is asking for data
            packet = self.factory.parent._getNextPacket(self.factory.groupNr)
            while packet != -1:
                self.sendLine(packet)
                packet = self.factory.parent._getNextPacket(self.factory.groupNr)
            self.sendLine('REQC')
            '''
            if packet == -1:
                # if there are no more packets to send, get a confirmation request
                self.sendLine('REQC')
            else:
                self.sendLine(packet)
                self.lineReceived('SEND')
                '''

        elif data[0] == 'NREC':
            # at least one packet did not arrive to the destination, resend it        
            packet = self.factory.parent._getPacketById(int(data[1]))
            self.sendLine(packet)
            self.sendLine('REQC')
            
        elif data[0] == 'RECA':
            # all file was received
            print '%s %d' % (line ,self.transport.getPeer().host)
            self.factory.parent._incFileDone(self)