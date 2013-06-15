import argparse
import os
import logging

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from serverFactory import *
from receiverFactory import *


SERVER_ARGUMENTS = [
    ['-sp', '--source-port', 'store', 8080, int, False, 'The port on which the server will listen for connections.'],
    ['-dp', '--dest-port', 'store', 1991, int, False, 'The port on which the server will listen for connections.'],
    ['-lf', '--logfile', 'store', '/tmp/log/server.log', str, False, 'Path for logfile.']
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in SERVER_ARGUMENTS:
        parser.add_argument(arg[0], arg[1], action=arg[2], default=arg[3], type=arg[4], required=arg[5], help=arg[6])
    args = parser.parse_args()


    logging.basicConfig(filename=args.logfile, filemode='w', format='%(levelname)s:[%(asctime)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)
    endpointS = TCP4ServerEndpoint(reactor, args.source_port)
    endpointS.listen(ServerLineReceiverFactory(args.source_port))

    endpointD = TCP4ServerEndpoint(reactor, args.dest_port)
    endpointD.listen(MyFileReceiverFactory(args.dest_port))
    reactor.run()