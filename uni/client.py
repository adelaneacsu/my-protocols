import argparse

from twisted.protocols.ftp import FTPClient
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor, defer

from common import *
from ecf import *

class Callback(object):

    def __init__(self):
        self.ports = []

    def _stop(self):
        for port in self.ports:
            if port is not None:
                port.disconnect()
        reactor.stop()



def checkConnection(args, cb, sType, client):
    
    if client is not None:
        dest_address = client[0]
        dest_port = client[1]
    else:
        dest_address = args.dest_address
        dest_port = args.dest_port
    port = None
    factory = ExtendedClientFactory(cb, dest_address, args.source_filepath, args.dest_filepath, args.no_statistics, args.parallel_streams, sType)
    if sType == 'D':
        port = reactor.connectTCP(dest_address, dest_port, factory)
    elif sType == 'S':
        port = reactor.connectTCP(args.source_address, args.source_port, factory)
    cb.ports.append(port)

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in CLIENT_ARGUMENTS:
        parser.add_argument(arg[0], arg[1], action=arg[2], default=arg[3], type=arg[4], required=arg[5], help=arg[6])
    args = parser.parse_args()
    startLogger(args.logfile)
    log_message('Client started.')

    cb = Callback()
    if args.multicast is not None:
        with open(args.multicast) as mcFile:
            for line in mcFile:
                client = line.split(':')
                if len(client) == 1:
                    client.append(args.dest_port)
                else:
                    client[1] = int(client[1])
                checkConnection(args, cb, 'D', client)
                checkConnection(args, cb, 'S', client)
    else:
        checkConnection(args, cb, 'D', None)
        checkConnection(args, cb, 'S', None)

    reactor.run()