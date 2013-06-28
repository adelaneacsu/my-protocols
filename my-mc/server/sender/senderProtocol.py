import os
import logging

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import reactor

from fileSenderFactory import *

class MySenderProtocol(LineReceiver):

    def __init__(self):
        self.directPeers = []
        logging.info('Server started.')

    def connectionMade(self):
        self.fileDoneCnt = 0
        self.destinations = []
        self.client = self.transport.getPeer()
        logging.info('Connection made: %s' % self.client)

    def connectionLost(self, reason):
        if hasattr(self, 'client'):
            logging.info('Connection ended from: %s' % self.client)
        else:
            logging.error('Connection ended unexpectedly. Reason: %s' % reason)

    def lineReceived(self, line):
        #print 'sd = %s %d' % (line ,self.transport.getPeer().port)
        data = line.strip().split(' ')
        if data[0] == 'SRFI':
            try:
                self.filepath = data[1]
            except IndexError:
                self.sendLine('ERRR')
                return
            if not os.path.exists(self.filepath):
                self.sendLine('FISZ 0')
                return
            self.fileSize = os.stat(self.filepath).st_size
            self.sendLine('FISZ ' + str(self.fileSize))
            try:
                self.fileObj = open(self.filepath, 'rb')
            except IOError:
                self.sendLine('ERRR')
                return

        elif data[0] == 'DSFI':
            try:
                self.dstpath = data[1]
            except IndexError:
                self.sendLine('ERRR')
                return

        elif data[0] == 'NRDS':
            try:
                self.nrDestinations = int(data[1])    
            except IndexError:
                self.sendLine('ERRR')
                return
            # decide distribution schema
            self.schemaIndices = [0, 0, 0, 0] # 2, 3, 4, 5
            if self.nrDestinations % 4 == 0:
                self.schemaIndices[2] = self.nrDestinations / 4
            elif self.nrDestinations % 4 == 1:
                self.schemaIndices[2] = self.nrDestinations / 4 - 1
                self.schemaIndices[3] = 1
            elif self.nrDestinations % 4 == 2:
                k = self.nrDestinations / 4
                if k == 0:
                    self.schemaIndices[0] = 1
                elif k == 1:
                    self.schemaIndices[1] = 2
                else:
                    self.schemaIndices[2] = k - 2
                    self.schemaIndices[3] = 2
            elif self.nrDestinations % 4 == 3:
                k = self.nrDestinations / 4
                if k == 0:
                    self.schemaIndices[1] = 1
                elif k == 1:
                    self.schemaIndices[1] = 1
                    self.schemaIndices[2] = 1
                elif k == 2:
                    self.schemaIndices[1] = 1
                    self.schemaIndices[2] = 2
                else:
                    self.schemaIndices[2] = k - 3
                    self.schemaIndices[3] = 3
            self.sendLine('DSOK')

        elif data[0] == 'PKSZ':
            try:
                self.packetSize = int(data[1])
            except IndexError:
                self.sendLine('ERRR')
                return

        elif data[0] == 'WDSZ':
            try:
                self.windowSize = int(data[1])
            except IndexError:
                self.sendLine('ERRR')
                return

        elif data[0] == 'DSIP':
            try:
                destIP = data[1]
                destPort = int(data[2])
            except IndexError:
                self.sendLine('ERRR')
                return
            dst = [destIP, destPort]
            index = len(self.destinations)
            self.destinations.append(dst)

            if index == self.nrDestinations - 1:
                start = 0
                group = 0
                for i in range(len(self.schemaIndices)):
                    for k in range(0, self.schemaIndices[i]):
                        lc = TCP4ClientEndpoint(reactor, self.destinations[start][0], self.destinations[start][1])
                        rc = TCP4ClientEndpoint(reactor, self.destinations[start+1][0], self.destinations[start+1][1])
                        lc.connect(MyFileSenderFactory(self, self.destinations[start+1], self.destinations[start+2:start+2+i], group, 0))
                        rc.connect(MyFileSenderFactory(self, self.destinations[start], self.destinations[start+2:start+2+i], group, 1))
                        start += (2 + i)       
                        group += 1
                self.configs = [0] * group

    def _incFileDone(self, peer):
        self.fileDoneCnt += 1
        logging.info('Transfer to %s completed.' % peer)
        if self.fileDoneCnt == self.nrDestinations:
            finishMsg = 'All destinations received the file. Transfer fully completed.'
            logging.info(finishMsg)
            print finishMsg
            for cPeer in self.directPeers:
                cPeer.transport.loseConnection()
            self.sendLine('STAT')
        else:
            self.directPeers.append(peer)

    def _getPacketById(self, packetId):
        offset = packetId * self.packetSize
        print 'offset = %d' % offset
        chunk = ''
        if self.fileSize > offset:
            # there is still data to read from file
            currOffset = self.fileObj.tell()
            if currOffset != offset:
                self.fileObj.seek(offset)
            chunk = '0000' + str(packetId).zfill(4) + self.fileObj.read(self.packetSize)
            return chunk
        else:
            return -1

    def _getConfigurations(self, groupNumber):
        if self.configs[groupNumber] == 0:
            self.configs[groupNumber] = 1
            return 1
        else:
            return -1