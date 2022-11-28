from __future__ import print_function

import json
import pickle
import time
import sys
import config

"""
An example client. Run simpleserv.py first before running this.
"""


from twisted.internet import reactor, protocol


# a client protocol

class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""

    def connectionMade(self):
        global message
        print("message sent ->",message)
        global node_ip  # dont use globals
        data = {"action": "message",
                "received_from_node": "0",
                "message":message,
                "timestamp": str(time.time())}
        self.transport.write(json.dumps(data).encode())

    def dataReceived(self, data):
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
    global message  # Dont do this
    global node_ip
    node_ip = "localhost"
    node_port = config.NETWORK_CONSTANTS["port"]
    port = config.NETWORK_CONSTANTS["port"]
    args = sys.argv
    ip = "localhost"
    if len(args) > 1:
        message = args[2]
        ip = args[1]
    reactor.connectTCP(ip, port, f)
    reactor.run()
 


# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
