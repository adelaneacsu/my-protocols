import os
from multiprocessing.connection import Client

from twisted.protocols.basic import FileSender
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory

from common import *

class AnonymousFileSenderFactory(ServerFactory):
    
    def __init__(self, parent):
        self.parent = parent
        self.filepath = parent.filename
        self.connections = 0

    def buildProtocol(self, addr):
        return AnonymousFileSenderProtocol(self)

class AnonymousFileSenderProtocol(LineReceiver):

    def __init__(self, factory):
        print 'New instance of AnonymousFileSenderProtocol created'
        self.filepath = factory.filepath
        self.factory = factory
        log_message('New instance of AnonymousFileSenderProtocol created')

    def connectionMade(self):
        self.factory.connections += 1
        self.fileObj = open(self.filepath, 'rb')
        size = os.stat(self.filepath).st_size
        self.sendLine('SIZE ' + str(size))
        log_message('Connection made: %s' % self.transport.getPeer())    

    def connectionLost(self, reason):
        self.factory.connections -= 1
        if self.factory.connections == 0:
            self.factory.parent._finishedTransfer()
        log_message('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        print 'sender %s' % line
        line = line.strip()
        if line == OK:
            sender = FileSender()
            sender.CHUNK_SIZE = 2 ** 16
            deffered = sender.beginFileTransfer(self.fileObj, self.transport, None)
            deffered.addCallback(self.success).addErrback(self.error)
            
    def success(self, lastByte):
        self.fileObj.close()
        self.transport.loseConnection()
        log_message('Finished transfer.')

    def error(self, response):
        self.fileObj.close()
        self.transport.loseConnection()
        log_message('Error: %s' % response)