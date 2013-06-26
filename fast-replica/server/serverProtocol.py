import os
import logging

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import reactor

from senderFactory import *

class ServerLineReceiverProtocol(LineReceiver):

    def __init__(self):
        logging.info('Server started.')

    def connectionMade(self):
        self.fileDone = 0
        self.client = self.transport.getPeer().host
        self.children = []
        logging.info('New connection from: %s on port %s' % (self.client,  self.transport.getPeer().port))

    def connectionLost(self, reason):
        if hasattr(self, 'client'):
            logging.info('Connection ended from: %s' % (self.client))
        else:
            logging.error('Connection ended unexpectedly. Reason: %s' % reason)

    def lineReceived(self, line):
        print line
        data = line.strip().split(' ')
        if len(data) == 0 or data == '':
            self.sendLine('ERR')
            return

        if data[0] == 'SRC':
            self.filepath = data[1]
            self.dstpath = data[2]
            if not os.path.exists(self.filepath):
                self.sendLine('404')
                return
            self.fileSize = os.stat(self.filepath).st_size
            self.sendLine('SZ ' + str(self.fileSize))

        elif data[0] == 'NC':
            self.clients = []
            self.nrClients = int(data[1])
            self.buffer = []
            self.packetSize = self.fileSize / self.nrClients
            if self.nrClients % self.fileSize != 0:
                self.packetSize += 1
            index = 0
            with open(self.filepath, 'rb') as fileObj:
                bytes = fileObj.read(self.packetSize)
                while bytes != '':
                    self.buffer.append('-' + str(index) + bytes)
                    index += 1
                    bytes = fileObj.read(self.packetSize)
            self.sendLine('IP')
            print 'SIZE %d' % len(self.buffer)

        elif data[0] == 'IP':
            destIP = '.'.join(data[1:5])
            destPort = int(data[5]) * 256 + int(data[6])
            client = [destIP, destPort]
            index = len(self.clients)
            self.clients.append(client)

            endpoint = TCP4ClientEndpoint(reactor, destIP, destPort)
            endpoint.connect(MyFileSenderFactory(self, index))


    def _incFileDone(self, peer):
        self.fileDone += 1
        logging.info('Transfer to %s completed.' % peer)
        if self.fileDone == self.nrClients:
            finishMsg = 'All destinations received the file. Transfer fully completed.'
            logging.info(finishMsg)
            print finishMsg
            self.sendLine('DN')

    def _connDone(self, child):
        self.children.append(child)
        if len(self.children) == self.nrClients:
            for child in self.children:
                child._sendConfiguration()