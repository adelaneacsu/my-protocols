import os
from multiprocessing.connection import Client

from twisted.protocols.basic import FileSender
from twisted.protocols.basic import LineReceiver

from common import *

class AnonymousFileSenderProtocol(LineReceiver):

    def __init__(self, filepath):
        self.filepath = filepath
        log_message('New instance of AnonymousFileSenderProtocol created')

    def connectionMade(self):
        self.fileObj = open(self.filepath, 'rb')
        size = os.stat(self.filepath).st_size
        self.sendLine('SIZE ' + str(size))
        log_message('Connection made: %s' % self.transport.getPeer())    

    def connectionLost(self, reason):
        log_message('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
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