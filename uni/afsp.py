import os
from multiprocessing.connection import Client

from twisted.protocols.basic import FileSender
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory

from common import *

class AnonymousFileSenderFactory(ServerFactory):
    
    def __init__(self, filepath):
        print 'FACTORY !!!'
        self.filepath = filepath
        print filepath

    def buildProtocol(self, addr):
        print 'build sender protocol'
        return AnonymousFileSenderProtocol(self.filepath)

class AnonymousFileSenderProtocol(LineReceiver):

    def __init__(self, filepath):
        print 'New instance of AnonymousFileSenderProtocol created'
        self.filepath = filepath
        log_message('New instance of AnonymousFileSenderProtocol created')

    def connectionMade(self):
        print 'Connection made to sender: %s' % self.transport.getPeer()
        self.fileObj = open(self.filepath, 'rb')
        size = os.stat(self.filepath).st_size
        self.sendLine('SIZE ' + str(size))
        log_message('Connection made: %s' % self.transport.getPeer())    

    def connectionLost(self, reason):
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