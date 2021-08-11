

from __future__ import print_function
import json
from twisted.internet import reactor, protocol
import pickle
"""
data model:
    
    
action: which action will be performed in the network ->
    add node, update node, download blockchain, verify mining hash, make transaction, add block
"""
class NodeAsServer(protocol.Protocol):
    
    def connectionMade(self):
        print("Started")
    def dataReceived(self, data):
        print("Data received...")
        try:
            print(data)
            data = json.loads(data)
        
        except:
            self.transport.loseConnection()#Maybe dont handle this?
        action=None
        try:
            action = data["action"]
            received_from_node = data["received_from_node"]
        except Exception as e:
            print(e)
            
            #self.transport.write(json.dumps(data).encode("ascii"))
            
            self.transport.write(b"Protocol error")
        self.transport.write(b"Data received successfully")
            
        if action=="add_node":
            data["received_from_node"] ="1"
            self.factory.node.add_node(data["node"]) #This should be the ip adress, along with the port of the node (?)
            if received_from_node == "0": #If the data wasnt received by another node, it will emit the data to the network, otherwise, there is no need to do so as another node would have done it already, hopefully
                self.factory.node.transmit_data(json.dumps(data).encode("ascii"))
                print("adding node...")
                print("Transmitting data to other nodes...")
                
        elif action=="add_block":
            data["received_from_node"] ="1"
            if received_from_node == "0": #If the data wasnt received by another node, it will emit the data to the network, otherwise, there is no need to do so as another node would have done it already, hopefully
                self.factory.node.transmit_data(json.dumps(data).encode("ascii"))
                print("adding block...")
                print("Transmitting to other nodes...")
               
            
        
        
class NodeServerFactory(protocol.ServerFactory): #Used when node is acting as a server, receiving information from other nodes to verify, or from others to, for example, add a node to the network
    protocol = NodeAsServer
    def __init__(self,queue=None, node = None):
        if not queue:
            self.queue = []
        else:
            self.queue = queue
        if not node:
            self.node = Node()
        else:
            self.node = node
            
            
    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
       
    
    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")

class NodeHandler(protocol.Protocol): #Used when node sends data to other nodes
    
    
    def connectionMade(self):
        try:
            self.transport.write(self.factory.data.encode())
        except:
            self.transport.write(self.factory.data)
    
    def dataReceived(self, data):
     
        print("Server said:", data)
        self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print("connection lost")

class EchoFactory(protocol.ClientFactory):
    protocol = NodeHandler
    
    def __init__(self,data=None):
        self.data = data or "None"
        

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed with node")
       
    
    def clientConnectionLost(self, connector, reason):
        print("Connection closed with node")
       
class Node:
    def __init__(self,node_list =None):
        if not node_list:
            self.node_list = []
        else:
            self.node_list = node_list
        
    def start_as_server(self):
        self.factory = NodeServerFactory(node=self)
        
        reactor.listenTCP(9002,self.factory)
       
        reactor.run()
    
    def add_node(self,node):
        self.node_list.append(node)
        
        
        
    def transmit_data(self,data):
        print(self.node_list)
        for node in self.node_list:
            
            f = EchoFactory(data = data)
            reactor.connectTCP(node, 9002, f)
        
            
            
            pass
    
    
    def start(self):
     
        self.start_as_server()
        
            
            


def main():
    node = Node(node_list=["localhost"])
    node.start()
    
    
    


if __name__ == '__main__':
    main()
