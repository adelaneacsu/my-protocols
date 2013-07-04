import logging

from twisted.protocols.basic import LineReceiver

class MyClientProtocol(LineReceiver):

   
    def __init__(self, parent, sourceFile, destFile, clients):
        self.parent     = parent
        self.sourceFile = sourceFile
        self.destFile   = destFile
        self.clients    = clients
    
    def connectionMade(self):
        logging.info('Connection made: %s' % self.transport.getPeer())
        message = 'SRC ' + self.sourceFile + ' ' + self.destFile
        self.sendLine(message)

        
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
                IP = ' '.join(client[0].split('.'))
                port = ' '.join([str(client[1] / 256), str(client[1] % 256)])
                sLine = 'IP %s %s' % (IP, port)
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
        