from __future__ import print_function

import json
import pickle
import time
import sys
"""
An example client. Run simpleserv.py first before running this.
"""


from twisted.internet import reactor, protocol


# a client protocol

class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""
    
    def connectionMade(self):
        global node_port
        global node_ip #dont use globals
        data = {"action":"add_node",
                "received_from_node":"0",
                "node":[node_ip,node_port],
                "timestamp":str(time.time())}
        self.transport.write(json.dumps(data).encode())
    
    def dataReceived(self,data):
        "As soon as any data is received, write it back."
        print("Server said:", data)
        self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print("connection lost")

class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print("Disconnecting...")
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print("Disconnecting...")
        reactor.stop()


# this connects the protocol to a server running on port 8000
def main():
    f = EchoFactory()
    global node_port #Dont do this
    global node_ip
    node_ip = "localhost"
    node_port = 9000
    port = 9000
    args = sys.argv
    ip = "localhost"
    if len(args)>1:
        port = int(args[2])
        node_port = int(args[4])
        node_ip = args[3]
        ip = args[1]
    reactor.connectTCP(ip, port, f)
    reactor.run()
    input()
 

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()