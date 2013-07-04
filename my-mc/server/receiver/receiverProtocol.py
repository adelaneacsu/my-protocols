import logging
import struct
import time

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor, defer

from multiEchoFactory import *


class MyReceiverProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory    = factory
        self.MAX_LENGTH = 524288010

    def connectionMade(self):
        print 'Connection MADE: %s' % self.transport.getPeer()
        if self.factory.source is None:
            #print 'source is %d' % self.transport.getPeer().port
            self.factory.source = self
        logging.info('Connection made: %s' % self.transport.getPeer())

    def connectionLost(self, reason):
        print 'Connection LOST: %s' % self.transport.getPeer()
        if self.factory.source == self:
            self.factory.source = None
            for echoer in self.factory.echoFactory.echoers:
                echoer.transport.loseConnection()
        logging.info('Connection lost: %s' % self.transport.getPeer())

    def lineReceived(self, line):
        if line[0:4] == '0000':
            # this is a packet - store and forward
            if self.factory.source == self:
                for echoer in self.factory.echoFactory.echoers:
                    echoer.sendLine(line)
            return self._processData(line[4:])
        else:
            print 'rc = %s %s' % (line ,self.transport.getPeer().host)
            data = line.strip().split(' ')
            if data[0] == 'SCHM':
                # SCHM number of schema (0, 1, 2 or 3)
                try:
                    self.factory.nrConnections = int(data[1]) + 1
                except IndexError:
                    self.sendLine('ERRR')
                    return

            elif data[0] == 'SIBL' or data[0] == 'CHLD':
                # SIBL/CHLD IP port
                try:
                    IP = data[1]
                    port = int(data[2])
                    endpoint = TCP4ClientEndpoint(reactor, IP, port)
                    endpoint.connect(self.factory.echoFactory).addCallback(self._newConnection)
                except IndexError:
                    self.sendLine('ERRR')
                    return

            elif data[0] == 'FPTH':
                # FPTH filepath
                try:
                    self.factory.fileObj = open(data[1], 'wb')
                    self.factory.nextToWrite = 0
                    logging.info('File %s opened for writing. Raw mode set.' % data[1])
                except IndexError:
                    self.sendLine('ERRR')
                    return
                # start statistics
                self.factory.startTime  = time.time()
                self.factory.minTime    = 1000000
                self.factory.maxTime    = 0
                self.factory.avgTime    = 0
                self.factory.nrPacksRec = 0
                # forward configurations
                if self.factory.source == self:
                    for echoer in self.factory.echoFactory.echoers:
                        echoer.sendLine(line)
            
            elif data[0] == 'PACK':
                # PACK nrPacks sizePack
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
                # WDSZ windSz
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
                # REQC -- check of all packets arrived
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
        print 'Received PACK %d from %s' % (currIndex, self.transport.getPeer())
        # statistics
        self.factory.nrPacksRec += 1
        currTime = time.time()
        delta = currTime - self.factory.startTime
        if delta < self.factory.minTime:
            self.factory.minTime = delta
        elif delta > self.factory.maxTime:
            self.factory.maxTime = delta
        self.factory.avgTime += delta
        self.factory.startTime = currTime

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
                # print stats
                print '==================================================================='
                print 'MIN = %.3f seconds' % self.factory.minTime
                print 'MAX = %.3f seconds' % self.factory.maxTime
                print 'AVG = %.3f seconds' % (self.factory.avgTime/self.factory.nrPacksRec)
                print 'RECEIVED %d packets in %d seconds' % (self.factory.nrPacksRec, self.factory.avgTime)
                print '==================================================================='

    def _newConnection(self, deffered):
        if len(self.factory.echoFactory.echoers) == self.factory.nrConnections:
            # all nodes are connected
            self.sendLine('CONN')