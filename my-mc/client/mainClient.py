import argparse
import logging

from twisted.protocols.ftp import FTPClient
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor, defer

from clientFactory import *


CLIENT_ARGUMENTS = [
    ['-sa', '--source-address', 'store', '127.0.0.1', str, False, 'The address of the source server. Default 127.0.0.1.'],
    ['-sf', '--source-filepath', 'store', None, str, True, 'The filepath from the source server.'],
    ['-sp', '--source-port', 'store', 22020, int, False, 'The port of the source server. Default 22000.'],
    ['-dp', '--dest-port', 'store', 22000, int, False, 'The port of the destination server. Default 22020.'],
    ['-df', '--dest-filepath', 'store', None, str, True, 'The filepath from the destination server.'],
    ['-ps', '--packet-size', 'store', 67108864, str, False, 'Size of packets expressed in Bytes. Default 67108864 (64MB).'],
    ['-ws', '--window-size', 'store', 10, str, False, 'Size of sliding window expressed in number of slots. Default 10.'],
    ['-mc', '--multicast', 'store', None, str, True, 'The filepath of the multicast file (contains addresses of destination servers).'],
    ['-lf', '--logfile', 'store', '/tmp/log/client.log', str, False, 'Path for logfile. Default /var/log/client.log.']
]

class Callback(object):

    def __init__(self):
        self.port = None

    def _stop(self):
        self.port.disconnect()
        reactor.stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in CLIENT_ARGUMENTS:
        parser.add_argument(arg[0], arg[1], action=arg[2], default=arg[3], type=arg[4], required=arg[5], help=arg[6])
    args = parser.parse_args()
    logging.basicConfig(filename=args.logfile, filemode='w', format='%(levelname)s:[%(asctime)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)
    logging.info('Client started.')

    cb = Callback()
    destinations = []
    with open(args.multicast) as mcFile:
        for line in mcFile:
            dst = line.rstrip('\n').split(':')
            if len(dst) == 1:
                dst.append(args.dest_port)
            else:
                dst[1] = int(dst[1])
            destinations.append(dst)

    factory = MyClientFactory(cb, args.source_filepath, args.dest_filepath, args.packet_size, args.window_size, destinations)
    cb.port = reactor.connectTCP(args.source_address, args.source_port, factory)

    reactor.run()