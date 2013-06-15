from twisted.internet.protocol import ServerFactory
from afsp import *

class AnonymousFileSenderFactory(ServerFactory):
    
    def __init__(self, filepath):
        self.filepath = filepath

    def buildProtocol(self, addr):
        return AnonymousFileSenderProtocol(self.filepath)