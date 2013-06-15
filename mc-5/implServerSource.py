import os
import logging

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor

from sender import *


class Contor:

    def __init__(self, size):
        
        self.size = size
        self.index = 0

    def nextIndex(self):
        if self.index < self.size:
            self.index += 1
            return self.index - 1
        else:
            return -1


class MySourceProtocol(LineReceiver):

    def __init__(self):
        self.packetSize = 2 ** 14 - 10
        logging.info('Server started.')

    def connectionMade(self):
        self.connDone = 0
        self.fileDone = 0
        self.client = self.transport.getPeer().host
        self.sendLine('K')
        logging.info('New connection from: %s on port %s' % (self.client,  self.transport.getPeer().port))

    def connectionLost(self, reason):
        if hasattr(self, 'client'):
            logging.info('Connection ended from: %s' % (self.client))
        else:
            logging.error('Connection ended unexpectedly. Reason: %s' % reason)

    def lineReceived(self, line):
        #print 'SS: %s' % line
        data = line.strip().split(' ')
        if data[0] == 'FILE':
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
            # decide schema
            self.inds = [0, 0, 0, 0] # 2, 3, 4, 5
            if self.nrClients % 4 == 0:
                self.inds[2] = self.nrClients / 4
            elif self.nrClients % 4 == 1:
                self.inds[2] = self.nrClients / 4 - 1
                self.inds[3] = 1
            elif self.nrClients % 4 == 2:
                k = self.nrClients / 4
                if k == 0:
                    self.inds[0] = 1
                elif k == 1:
                    self.inds[1] = 2
                else:
                    self.inds[2] = k - 2
                    self.inds[3] = 2
            elif self.nrClients % 4 == 3:
                k = self.nrClients / 4
                if k == 0:
                    self.inds[1] = 1
                elif k == 1:
                    self.inds[1] = 1
                    self.inds[2] = 1
                elif k == 2:
                    self.inds[1] = 1
                    self.inds[2] = 2
                else:
                    self.inds[2] = k - 3
                    self.inds[3] = 3
            index = 0
            with open(self.filepath, 'rb') as fileObj:
                bytes = fileObj.read(self.packetSize)
                while bytes != '':
                    self.buffer.append('-' + str(index) + '-' + bytes)
                    index += 1
                    bytes = fileObj.read(self.packetSize)
            self.sendLine('IP')

        elif data[0] == 'IP':
            destIP = data[1]
            destPort = int(data[2])
            client = [destIP, destPort]
            index = len(self.clients)
            self.clients.append(client)

            if index == self.nrClients - 1:
                start = 0
                for i in range(len(self.inds)):
                    for k in range(0, self.inds[i]):
                        ctr = Contor(len(self.buffer))
                        lc = TCP4ClientEndpoint(reactor, self.clients[start][0], self.clients[start][1])
                        rc = TCP4ClientEndpoint(reactor, self.clients[start+1][0], self.clients[start+1][1])
                        lc.connect(MyFileSenderFactory(self, self.clients[start+1], self.clients[start+2:start+2+i], 'L', ctr))
                        rc.connect(MyFileSenderFactory(self, self.clients[start], self.clients[start+2:start+2+i], 'R', ctr))
                        start += (2 + i)



    def _incFileDone(self, peer):
        self.fileDone += 1
        logging.info('Transfer to %s completed.' % peer)
        if self.fileDone == self.nrClients:
            finishMsg = 'All destinations received the file. Transfer fully completed.'
            logging.info(finishMsg)
            print finishMsg
            self.sendLine('DN')



class MySourceFactory(ServerFactory):
    
    def __init__(self, port):
        self.port = port

    def buildProtocol(self, addr):
        addr.port = self.port
        return MySourceProtocol()