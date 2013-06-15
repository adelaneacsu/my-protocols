import argparse
import os

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from common import *
from elrf import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in SERVER_ARGUMENTS:
        parser.add_argument(arg[0], arg[1], action=arg[2], default=arg[3], type=arg[4], required=arg[5], help=arg[6])
    args = parser.parse_args()

    startLogger(args.logfile)
    endpoint = TCP4ServerEndpoint(reactor, args.port)
    endpoint.listen(ExtendedLineReceiverFactory(args.port))
    reactor.run()