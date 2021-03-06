import argparse
import os

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from common import *
from elrp import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in SERVER_ARGUMENTS:
        parser.add_argument(arg[0], arg[1], action=arg[2], default=arg[3], type=arg[4], required=arg[5], help=arg[6])
    args = parser.parse_args()

    startLogger(args.logfile)

    endpointD = TCP4ServerEndpoint(reactor, args.dest_port)
    endpointD.listen(AnonymousFileReceiverFactory(args.dest_port))

    endpointS = TCP4ServerEndpoint(reactor, args.source_port)
    endpointS.listen(ExtendedLineReceiverFactory(args.source_port))

    reactor.run()