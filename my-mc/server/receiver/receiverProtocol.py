import logging
import struct

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor, defer

from multiEchoFactory import *


class MyReceiverProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.MAX_LENGTH = 524288010

    def connectionMade(self):
        if self.factory.source is None:
            #print 'source is %d' % self.transport.getPeer().port
            self.factory.source = self
        logging.info('Connection made: %s' % self.transport.getPeer())

    def connectionLost(self, reason):
        if self.factory.source == self:
            self.factory.source = None
            for echoer in self.factory.echoFactory.echoers:
                echoer.transport.loseConnection()
        logging.info('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        #print 'rc = %s %d' % (line ,self.transport.getPeer().port)
        if line[0:4] == '0000':
            # this is a packet - store and forward
            if self.factory.source == self:
                for echoer in self.factory.echoFactory.echoers:
                    echoer.sendLine(line)
            return self._processData(line[4:])
        else:
            data = line.strip().split(' ')
            if data[0] == 'SCHM':
                try:
                    self.factory.nrConnections = int(data[1]) + 1
                except IndexError:
                    self.sendLine('ERRR')
                    return

            elif data[0] == 'SIBL' or data[0] == 'CHLD':
                try:
                    IP = data[1]
                    port = int(data[2])
                    endpoint = TCP4ClientEndpoint(reactor, IP, port)
                    endpoint.connect(self.factory.echoFactory).addCallback(self._newConnection)
                except IndexError:
                    self.sendLine('ERRR')
                    return

            elif data[0] == 'FPTH':
                try:
                    self.factory.fileObj = open(data[1], 'wb')
                    self.factory.nextToWrite = 0
                    logging.info('File %s opened for writing. Raw mode set.' % data[1])
                except IndexError:
                    self.sendLine('ERRR')
                    return
                if self.factory.source == self:
                    for echoer in self.factory.echoFactory.echoers:
                        echoer.sendLine(line)
            
            elif data[0] == 'PACK':
                try:
                    self.factory.nrPackets = int(data[1])
                    self.factory.packetSize = int(data[2])
                    self.factory.packetsReceived = [False] * self.factory.nrPackets
                except IndexError:
                    self.sendLine('ERRR')
                    return
                if self.factory.source == self:
                    for echoer in self.factory.echoFactory.echoers:
                        echoer.sendLine(line)

            elif data[0] == 'WDSZ':
                try:
                    self.factory.windowSize = int(data[1])
                    self.factory.window = [""] * self.factory.windowSize
                    # -1 if the slot is free, packet index otherwise
                    self.factory.slotBusy = [-1] * self.factory.windowSize
                except IndexError:
                    self.sendLine('ERRR')
                    return
                if self.factory.source == self:
                    for echoer in self.factory.echoFactory.echoers:
                        echoer.sendLine(line)
                self.factory.source.sendLine('SEND')

            elif data[0] == 'REQC':
                allSent = True
                for bitIndex in range(len(self.factory.packetsReceived)):
                    if not self.factory.packetsReceived[bitIndex]:
                        allSent = False
                        self.sendLine('NREC ' + str(bitIndex))
                        break
                if allSent:
                    self.sendLine('RECA')


    def _processData(self, rawData):
        logging.info('Received %d bytes.' % (len(rawData) - 4))
        # split : header + data
        currIndex = int(rawData[0:4])
        if self.factory.packetsReceived[currIndex] == False:
            # only keep first copy of each packet, since they might arrive on more than one links
            self.factory.packetsReceived[currIndex] = True
            if self.factory.nextToWrite == currIndex:
                # current packet must be written directly to file
                self.factory.fileObj.write(rawData[4:])
                self.factory.nextToWrite += 1
                countdown = self.factory.windowSize
                done = False
                # also write all packets that come after
                while not done:
                    for slotIndex in range(self.factory.windowSize):
                        countdown -= 1
                        if self.factory.slotBusy[slotIndex] == self.factory.nextToWrite:
                            self.factory.fileObj.write(self.factory.window[slotIndex])
                            self.factory.slotBusy[slotIndex] = -1
                            self.factory.nextToWrite += 1
                            countdown = self.factory.windowSize
                        if countdown == 0:
                            done = True
            else:
                # find an empty slot to store data
                for slotIndex in range(self.factory.windowSize):
                    if self.factory.slotBusy[slotIndex] == -1:
                        self.factory.window[slotIndex] = rawData[4:]
                        self.factory.slotBusy[slotIndex] = currIndex
                        break

            if self.factory.nextToWrite == self.factory.nrPackets:
                # file was completely written 
                self.factory.fileObj.close()
                if len(self.factory.echoFactory.echoers) == 0:
                    self.sendLine('CHRA')


    def _newConnection(self, deffered):
        if len(self.factory.echoFactory.echoers) == self.factory.nrConnections:
            # all nodes are connected
            self.sendLine('CONN')