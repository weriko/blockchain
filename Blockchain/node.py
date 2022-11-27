#solve efficiency things
#Separate Node in different processes
#add check for the whole network node list, checking if they are still on
from __future__ import print_function
import json
from twisted.internet import reactor, protocol
import config
import connect_db
import hashlib as hs
import pickle
import random
from requests import get
import time
"""
data model:
    
    
action: which action will be performed in the network ->
    add node, update node, download blockchain, verify mining hash, make transaction, add block
"""




class NodeAsServer(protocol.Protocol):


    
    def connectionMade(self):
        print("Started")

    def dataReceived(self, data):

        try:
            print(data)
            data = json.loads(data)
        
        except:
            self.transport.loseConnection()#Maybe dont handle this?

        action=None

        if data.get("nodes_seen"):
            data["nodes_seen"].append(self.factory.node.ip)
        else:
            data["nodes_seen"] = [self.factory.node.ip]
        


        try:
            action = data["action"]
            received_from_node = data["received_from_node"]
        except Exception as e:
            print(e)
            
            #self.transport.write(json.dumps(data).encode("ascii"))
            
            self.transport.write(b"Protocol error")

        self.transport.write(b"Data received successfully")



        if action == "request_nodes":
            enodes = connect_db.explore_nodes()
            data = {"nodes":enodes}
            self.transport.write(json.dumps(data).encode("ascii"))
            


        if action=="add_node":
            
            data["received_from_node"] ="1"
            

            
            self.factory.node.add_node(data["node"])





            
            self.factory.node.transmit_data(json.dumps(data).encode("ascii"))
            
            print("adding node...")
            print("Transmitting data to other nodes...")
                
        elif action=="add_block":
            data["received_from_node"] ="1"
            if received_from_node == "0": #If the data wasnt received by another node, it will emit the data to the network, otherwise, there is no need to do so as another node would have done it already, hopefully
                self.factory.node.transmit_data(json.dumps(data).encode("ascii"))
                print("adding block...")
                print(self.factory.node.port)
                print(self.factory.node.ip)
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

        self.node_list = connect_db.get_nodes()
        self.port = port
        if not pub_ip:
            pub_ip = get("https://api.ipify.org").text
        self.ip=pub_ip 
        
    def start_as_server(self):
        self.factory = NodeServerFactory(node=self)
        
        reactor.listenTCP(self.port,self.factory)
       
        reactor.run()
    
    def add_node(self,node):
        ip, port = node[0],node[1]
        self.node_list.append(node)
        connect_db.insert_node(ip, port)

        
    def remove_node(self, node):
        ip, port=  node[0],node[1]
        self.node_list.remove(node)
        connect_db.remove_node(ip,port)
        
    def get_nodes(self):
        nodes = connect_db.get_nodes()
        return nodes

        
    def transmit_data(self, data):
        nodes_seen = data.get("nodes_seen", []) #maybe change to set
        
        for n in self.node_list:
            if n[0] not in nodes_seen:
                try:
                    if self.ip!=n[0] or self.port!=n[1]:
                    
                        f = EchoFactory(data = data,ip=n[0],port=n[1])
                        reactor.connectTCP(n[0], n[1], f)
                    
                except:
                    pass
                
    def ping_nodes(self):  
        is_connected = []
        for n in self.node_list:
            try:
                if self.ip!=n[0] or self.port!=n[1]:

                    f = EchoFactory(data = {"ping":0},ip=n[0],port=n[1])
                    reactor.connectTCP(n[0], n[1], f)
                    is_connected.append(True)
                
            except:
                is_connected.append(False)
        return is_connected   
    
    def ping_and_remove_nodes(self):
         for n in self.node_list:
            try:
                if self.ip!=n[0] or self.port!=n[1]:

                    f = EchoFactory(data = {"ping":0},ip=n[0],port=n[1])
                    reactor.connectTCP(n[0], n[1], f)
                
            except:
                self.remove_node(n)

    def connect_to_peers(self):
        self.ping_and_remove_nodes()
        current_connected = self.get_nodes()
        l = len(current_connected)
        nodes = self.choose_connect(l)
        for n in nodes:
            self.add_node(n)


    def choose_connect(self, num=99):
        enodes = connect_db.explore_nodes()
        n = min(len(enodes), config.NETWORK_CONSTANTS["node_peers"], num)
        try:
            nodes = random.sample(enodes, config.NETWORK_CONSTANTS["node_peers"]- n ) #Implement better node selection other than random. maybe
        except:
            nodes = []
        return nodes

    def start(self):
        self.connect_to_peers()
     
        self.start_as_server()
        
            
            


