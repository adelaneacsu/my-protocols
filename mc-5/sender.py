import os
import logging

from multiprocessing.connection import Client
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver


class MyFileSenderProtocol(LineReceiver):

    def __init__(self, parent, sibling, children, sType, counter):
        self.parent = parent
        self.sibling = sibling
        self.children = children
        self.sType = sType
        self.counter = counter

    def connectionMade(self):
        self.sendLine('NC ' + str(len(self.children) + 1))
        for child in self.children:
            self.sendLine('CON ' + child[0] + ' ' + str(child[1]))
        logging.info('Connection made: %s' % self.transport.getPeer())

    def connectionLost(self, reason):
        logging.info('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        #print 'sender: %s' % line
        line = line.strip()
        if line == 'GO':
            idx = self.counter.nextIndex()
            while idx != -1:
                self.sendLine(self.parent.buffer[idx])
                idx = self.counter.nextIndex()
        elif line == 'DN':
            self.parent._incFileDone(self.transport.getPeer())
        elif line == 'CON':
            self.sendLine('PTH ' + self.parent.dstpath)
            self.sendLine('PKs ' + str(len(self.parent.buffer)) + ' ' + str(self.parent.packetSize))
            self.sendLine('CON ' + self.sibling[0] + ' ' + str(self.sibling[1]))

class MyFileSenderFactory(ServerFactory):
    
    def __init__(self, parent, sibling, children, sType, counter):
        self.parent = parent
        self.sibling = sibling
        self.children = children
        self.sType = sType
        self.counter = counter

    def buildProtocol(self, addr):
        return MyFileSenderProtocol(self.parent, self.sibling, self.children, self.sType, self.counter)