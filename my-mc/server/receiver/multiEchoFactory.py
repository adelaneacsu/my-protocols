from twisted.internet.protocol import Protocol, Factory

from multiEchoProtocol import *

class MultiEchoFactory(Factory):
    
    def __init__(self, parent):
        self.echoers 	= []
        self.parent 	= parent

    def buildProtocol(self, addr):
        return MultiEchoProtocol(self)