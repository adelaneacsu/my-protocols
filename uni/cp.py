from twisted.protocols.basic import LineReceiver

from common import *


class ClientProtocol(LineReceiver):

   
    def __init__(self, parent, destIP, sourceFile, destFile, nos, streams, serverType):
        self.parent     = parent
        self.destIP     = destIP
        self.sourceFile = sourceFile
        self.destFile   = destFile
        self.nos        = nos
        self.streams    = streams
        self.serverType = serverType
        self.destPort   = 1991
        self.status     = 'IDLE'
    
    def connectionMade(self):  
        self.status = 'CONN'
        log_message('Connection made: %s' % self.transport.getPeer())

        
    def lineReceived(self, line):
        line = line.strip()
        if line == OK:
            for case in switch(self.status):
                if case('IDLE'): 
                    pass

                if case('CONN'):
                    self.status = 'PORT'
                    if self.serverType == 'S' and self.nos == 1:
                        self._nos()
                    self.lineReceived(OK)
                    break

                if case('PORT'):
                    self._port()
                    break

                if case('RETR'):
                    self._retr()
                    break

                if case('STOR'):
                    self._stor()
                    break

                if case('DONE'):
                    pass

                if case():
                    # No need to break here, it'll stop anyway
                    pass
        elif line == 'DONE':
            # The client can now ask for statistics
            if self.serverType == 'S' and self.nos == 1:
                self.sendLine('STAT')
            else:
                self._stop()

        elif line == 'AVG':
            # Get statitics and then stop
            stats = line.split(' ')
            self._stop()

    def _stop(self):
        msg = 'Finished transfer.'
        log_message(msg)
        print msg
        self.parent._stop()

    def _nos(self):
        # Tell source server to not generate statistics for the transfer.
        self.sendLine('NOS')

    def _strm(self):
        line = 'STRM %d' % self.streams
        self.sendLine(line)

    def _port(self):
        IP = ' '.join(self.destIP.split('.'))
        port = ' '.join([str(self.destPort / 256), str(self.destPort % 256)])
        line = 'PORT %s %s' % (IP, port)
        self.status = ['STOR', 'RETR'][self.serverType == 'S']
        self.sendLine(line)


    def _stor(self):
        line = 'STOR %s' % self.destFile
        self.status = 'DONE'
        self.sendLine(line)
    
    def _retr(self):
        line = 'RETR %s' % self.sourceFile
        self.status = 'DONE'
        self.sendLine(line)
