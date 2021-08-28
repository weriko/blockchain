

from __future__ import print_function
import json
from twisted.internet import reactor, protocol
import pickle
from requests import get
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
                print(self.factory.node.port)
                print(self.factory.node.pub_ip)
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
    
    def __init__(self,data=None,ip=None,port=None):
        self.data = data or "None"
        

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed with node",reason)
       
    
    def clientConnectionLost(self, connector, reason):
        print("Connection closed with node")
       
class Node:
    def __init__(self,node_list =None, port = 9000, pub_ip =None):
        if not node_list:
            self.node_list = []
        else:
            self.node_list = node_list
        self.port = port
        if not pub_ip:
            pub_ip = get("https://api.ipify.org").text
        self.pub_ip=pub_ip 
        
    def start_as_server(self):
        self.factory = NodeServerFactory(node=self)
        
        reactor.listenTCP(self.port,self.factory)
       
        reactor.run()
    
    def add_node(self,node):
        self.node_list.append(node)
        
        
        
    def transmit_data(self,data):
        print(self.node_list)
        for n in self.node_list:
            try:
                if self.pub_ip!=n[0] or self.port!=n[1]:
                
                    f = EchoFactory(data = data,ip=n[0],port=n[1])
                    reactor.connectTCP(n[0], n[1], f)
                   
            except:
                pass
                
                
    
    
    def start(self):
     
        self.start_as_server()
        
            
            


def main():
    with open("nodes.json","r") as nd:
        j = json.load(nd)["data"]
        print(j)
        node = Node(node_list=j, port = 9000, pub_ip = None)
        
        print("Starting...")
        node.start()
    
    
    


if __name__ == '__main__':
    main()
