import logging

# [flags, action, default, type, required, help]
CLIENT_ARGUMENTS = [
    ['-sa', '--source-address', 'store', '127.0.0.1', str, False, 'The address of the source server.'],
    ['-da', '--dest-address', 'store', '127.0.0.1', str, False, 'The address of the destination server.'],
    ['-sf', '--source-filepath', 'store', None, str, True, 'The filepath from the source server.'],
    ['-df', '--dest-filepath', 'store', None, str, True, 'The filepath from the destination server.'],
    ['-sp', '--source-port', 'store', 1234, int, False, 'The port of the source server.'],
    ['-dp', '--dest-port', 'store', 1234, int, False, 'The port of the destination server.'],
    ['-mc', '--multicast', 'store', None, str, False, 'The filepath of the multicast file (contains addresses of destination servers).'],
    ['-ps', '--parallel-streams', 'store', 1, int, False, 'Option for using multiple connections during transfer'],
    ['-ns', '--no-statistics', 'store', False, bool, False, 'The client doesn\'t request any statistics for the transfer.'],
    ['-lf', '--logfile', 'store', '/var/log/client.log', str, False, 'Path for logfile.']
]

SERVER_ARGUMENTS = [
    ['-p', '--port', 'store', 1234, int, False, 'The port on which the server will listen for connections.'],
    ['-lf', '--logfile', 'store', '/var/log/server.log', str, False, 'Path for logfile.']
]

# HTTP CODES 
OK      = '200'
ERR_S   = '404'


def startLogger(filename):
    logging.basicConfig(filename=filename, filemode='w', format='%(levelname)s:[%(asctime)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)

def log_message(message):
    logging.info(message)

def error_message(message):
    logging.error(message)


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False