from twisted.internet.protocol import ServerFactory

from fileSenderProtocol import *

class MyFileSenderFactory(ServerFactory):
    
    def __init__(self, parent, sibling, children, groupNr, parity):
        self.parent 	= parent
        self.sibling 	= sibling
        self.children 	= children
        self.groupNr	= groupNr
        self.parity		= parity

    def buildProtocol(self, addr):
        return MyFileSenderProtocol(self)