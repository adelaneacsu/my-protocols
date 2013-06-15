from twisted.protocols.ftp import FileConsumer, FTPClient
from twisted.protocols.basic import LineReceiver
from zope.interface import implements
from twisted.internet import interfaces


from common import *

class AnonymousFileReceiverProtocol(LineReceiver):

    def __init__(self, parent, filepath):
        self.parent = parent
        self.filepath = filepath
        log_message('New instance of AnonymousFileSenderProtocol created')

    def connectionMade(self):
        log_message('Connection made: %s' % self.transport.getPeer())

    def connectionLost(self, reason):
        if hasattr(self, 'fileObj'):
            self.fileObj.close()
        if hasattr(self, 'bytesLeft') and self.bytesLeft == 0:
            log_message('File transfered successfully.')
        else:
            log_message('An error ocurred during transfer.')
        # Notify parent that connection was lost so that it stops the server.
        self.parent._lostConnection()
        log_message('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        line = line.strip()
        command = line.split(' ')
        if command[0] == 'SIZE':
            try:
                self.fileObj = open(self.filepath, 'wb')
            except Exception:
                log_message('Can\'t open file %s for writing!' % self.filepath)
                self.transport.loseConnection()
                return
            self.bytesLeft = int(command[1])
            self.setRawMode()
            log_message('File %s opened for writing. Raw mode set.' % self.filepath)
            self.sendLine(OK)

    def rawDataReceived(self, rawData):
        length = len(rawData)
        self.bytesLeft -= length
        self.fileObj.write(rawData)
        log_message('Received %d bytes.' % length)