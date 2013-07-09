import logging

from twisted.protocols.basic import LineReceiver

class MyClientProtocol(LineReceiver):
   
    def __init__(self, factory):
        self.factory = factory
    
    def connectionMade(self):
        msg = 'Connection made: %s' % self.transport.getPeer()
        logging.info(msg)
        print 'Connection made: %s on port %d' % (self.transport.getPeer().host, self.transport.getPeer().port)
        
        line = 'SRFI ' + self.factory.sourceFile
        self.sendLine(line)
        line = 'DSFI ' + self.factory.destFile
        self.sendLine(line)

        
    def lineReceived(self, line):
        if __debug__:
            print line
        data = line.strip().split(' ')
        if data[0] == 'FISZ':
            # file size
            logging.info('File ' + self.factory.sourceFile + ' has ' + data[1] + ' bytes.')
            size = int(data[1])
            if size == 0:
                logging.info('Transfer stopped.')
                print 'The file does NOT exist on the source server or it does not have reading rights.'
                print 'Communication with the source server will now stop.'
                self.factory.callback._stop()
            else:
                print 'The file has %d Bytes of data.' % size
                sLine = 'NRDS ' + str(len(self.factory.destinations))
                self.sendLine(sLine)
                sLine = 'PKSZ ' + str(self.factory.packetSize)
                self.sendLine(sLine)
                sLine = 'WDSZ ' + str(self.factory.windowSize)
                self.sendLine(sLine)

        elif data[0] == 'DSOK':
            # received number of destinations
            for dst in self.factory.destinations:
                sLine = 'DSIP %s %d' % (dst[0], dst[1])
                self.sendLine(sLine)

        elif data[0] == 'TRST':
            # transfer started
            msg = 'Transfer started ...'
            logging.info(msg)
            print msg

        elif data[0] == 'STAT':
            # statistics
            msg = 'Transfer fully completed. Connection ended.'
            print msg
            logging.info(msg)
            self.factory.callback._stop()

        elif data[0] == 'ERRR':
            msg = 'An error ocurred. Connection ended.'
            print msg
            logging.info(msg)
            self.factory.callback._stop()
        