from twisted.internet.protocol import ServerFactory
from afsp import *

class AnonymousFileSenderFactory(ServerFactory):
    
    def __init__(self, filepath):
    	print 'FACTORY !!!'
        self.filepath = filepath

    def buildProtocol(self, addr):
    	print 'build sender protocol'
        return AnonymousFileSenderProtocol(self.filepath)