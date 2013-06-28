from twisted.internet.protocol import ServerFactory

from fileSenderProtocol import *

class MyFileSenderFactory(ServerFactory):
    
    def __init__(self, parent, sibling, children, groupNr):
        self.parent 	= parent
        self.sibling 	= sibling
        self.children 	= children
        self.groupNr	= groupNr

    def buildProtocol(self, addr):
        return MyFileSenderProtocol(self)