import os
from multiprocessing.connection import Listener

from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint
from twisted.internet import reactor

from common import *
from afsf import *
from afrf import *


class ExtendedLineReceiverProtocol(LineReceiver):

    def __init__(self):
        self.noStatistics = False
        log_message('Server started.')

    def connectionMade(self):
        self.client = self.transport.getPeer().host
        self.sendLine(OK)
        log_message('New connection from: %s on port %s' % (self.client,  self.transport.getPeer().port))

    def connectionLost(self, reason):
        if hasattr(self, 'client'):
            log_message('Connection ended from: %s' % (self.client))
        else:
            error_message('Connection ended unexpectedly. Reason: %s' % reason)

    def lineReceived(self, line):
        line = line.strip()
        data = line.split(' ')
        if len(data) == 0 or data == '':
            self.sendLine(ERR_S)
            return

        command = data[0]
        if command == 'NOS':
            # NOS
            # no-statistics
            self.noStatistics = True

        elif command == 'PORT':
            # PORT a1,a2,a3,a4,p1,p2,s
            # IP = a1.a2.a3.a4, port = p1*256+p2, streams = s
            try:
                self.destIP = '.'.join(data[1:5])
                self.destPort = int(data[5]) * 256 + int(data[6])
            except IndexError:
                self.sendLine(ERR_S)
                return
            
        elif command == 'RETR':
            # RETR filename
            # Send data
            try:
                self.filename = data[1]
            except IndexError:
                self.sendLine(ERR_S)
                return
            # check if file exists
            if not os.path.exists(self.filename):
                self.sendLine(ERR_S)
                return
            # if everything is OK, start connection from source server
            endpoint = TCP4ClientEndpoint(reactor, self.destIP, self.destPort)
            endpoint.connect(AnonymousFileSenderFactory(self.filename))

        elif command == 'STOR':
            # STOR filename
            # Receive data
            try:
                self.filename = data[1]
            except IndexError:
                self.sendLine(ERR_S)
                return
            #endpoint = TCP4ServerEndpoint(reactor, self.destPort)
            #endpoint.listen(AnonymousFileReceiverFactory(self, self.filename))
            port = reactor.listenTCP(self.destPort, AnonymousFileReceiverFactory(self, self.filename))
            self.port = port

        self.sendLine(OK)

    def _lostConnection(self):
        # Called from destination server, after the file was transfered.
        self.port.stopListening()
        self.sendLine('DONE')