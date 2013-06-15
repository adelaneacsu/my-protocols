import logging

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

class MyClientProtocol(LineReceiver):

   
    def __init__(self, parent, sourceFile, destFile, clients):
        self.parent     = parent
        self.sourceFile = sourceFile
        self.destFile   = destFile
        self.clients    = clients
    
    def connectionMade(self):
        print 'Connected to source server.'
        logging.info('Connection made: %s' % self.transport.getPeer())
        message = 'FILE ' + self.sourceFile + ' ' + self.destFile
        self.sendLine(message)

    def connectionLost(self, reason):
        print 'Connection lost.'
        logging.info('Connection lost: %s' % self.transport.getPeer())

        
    def lineReceived(self, line):
        print line
        data = line.strip().split(' ')
        if data[0] == 'SZ':
            # file size
            logging.info('File ' + self.sourceFile + ' has ' + data[1] + ' bytes.')
            logging.info('File transfer starting...')

            self.sendLine('NC ' + str(len(self.clients)))

        elif data[0] == 'IP':
            for client in self.clients:
                sLine = 'IP %s %s' % (client[0], client[1])
                self.sendLine(sLine)

        elif data[0] == 'CL':
            # number of destinations successfully connected
            logging.info('' + data[1]  + ' / ' + str(len(self.clients)) + 'destination servers were successfully connected.')

        elif data[0] == 'DN':
            finishMsg = 'Transfer fully completed. Connection ended.'
            print finishMsg
            logging.info(finishMsg)
            self.parent._stop()
        
        elif data[0] == '404':
            logging.info('File was not found on source server. Try again...')
            self.parent._stop()
    


class MyClientFactory(ClientFactory):
    
    def __init__(self, parent, sourceFile, destFile, clients):
        self.parent     = parent
        self.sourceFile = sourceFile
        self.destFile   = destFile
        self.clients    = clients
    
    def buildProtocol(self, addr):
        return MyClientProtocol(self.parent, self.sourceFile, self.destFile, self.clients)