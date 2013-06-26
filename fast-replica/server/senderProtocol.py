import os
import logging
from multiprocessing.connection import Client

from twisted.protocols.basic import LineReceiver


class MyFileSenderProtocol(LineReceiver):

    def __init__(self, parent, index):
        self.parent = parent
        self.index = index
        

    def connectionMade(self):
        self.sendLine('PTH ' + self.parent.dstpath)
        self.sendLine('PKs ' + str(self.parent.nrClients) + ' ' + str(self.parent.packetSize))
        self.sendLine('IDx ' + str(self.index))
        self.parent.connDone += 1
        for currIndex in range(self.parent.nrClients - 2):
            idx = (currIndex + self.index + 1) % self.parent.nrClients
            line = 'N ' + self.parent.clients[idx][0] + ' ' + str(self.parent.clients[idx][1])
            if currIndex == (self.parent.nrClients - 3):
                line += ' DN'
            self.sendLine(line)
        if self.parent.nrClients == 2:
            self.sendLine('NON')
        logging.info('Connection made: %s' % self.transport.getPeer())

    def connectionLost(self, reason):
        logging.info('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        if line == 'GO':
            self.sendLine(self.parent.buffer[self.index])
            self.sendLine(self.parent.buffer[(self.index + 1) % self.parent.nrClients])
        elif line == 'DN':
            self.parent._incFileDone(self.transport.getPeer())