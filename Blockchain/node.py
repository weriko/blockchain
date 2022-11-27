# solve efficiency things
# Separate Node in different processes
# add check for the whole network node list, checking if they are still on
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
import uuid
import pathlib
import socket
from telnetlib import Telnet
from apscheduler.schedulers.background import BackgroundScheduler
"""
data model:
    
    
action: which action will be performed in the network ->
    add node, update node, download blockchain, verify mining hash, make transaction, add block
"""

# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class NodeAsServer(protocol.Protocol):

    def connectionMade(self):
        print("Started")

    def dataReceived(self, data):

        try:

            data = json.loads(data)

        except Exception as e:
            print(e)
            self.transport.loseConnection()  # Maybe dont handle this?
        if data.get("broadcast") != "false":
            action = None

            if data.get("nodes_seen"):
                data["nodes_seen"].append(self.factory.node.ip)
            else:
                data["nodes_seen"] = [self.factory.node.ip]

            try:
                action = data["action"]
                received_from_node = data["received_from_node"]
            except Exception as e:
                print(e)

                # self.transport.write(json.dumps(data).encode("ascii"))

                self.transport.write(b"Protocol error")

            self.transport.write(b"Data received successfully")

            if action == "request_nodes":
                enodes = connect_db.explore_nodes()
                data = {"nodes": enodes}
                self.transport.write(json.dumps(data).encode("ascii"))

            if action == "add_explore_node":

                data["received_from_node"] = "1"

                self.factory.node.add_explore_node(data["node"])
                self.factory.node.transmit_data(
                    json.dumps(data).encode("ascii"))

                print("adding node...")
                print("Transmitting data to other nodes...")

            if action == "add_node":

                data["received_from_node"] = "1"

                self.factory.node.add_node(data["node"])
                #self.factory.node.transmit_data(
                 #   json.dumps(data).encode("ascii"))

                print("adding node...")
                

            if action == "message":
                data["received_from_node"] = "1"

                self.factory.node.transmit_data(
                    json.dumps(data).encode("ascii"))

                
                print("message received : ", data.get("message"))

            elif action == "add_block":
                data["received_from_node"] = "1"
                if received_from_node == "0":  # If the data wasnt received by another node, it will emit the data to the network, otherwise, there is no need to do so as another node would have done it already, hopefully
                    self.factory.node.transmit_data(
                        json.dumps(data).encode("ascii"))
                    print("adding block...")
                    print(self.factory.node.port)
                    print(self.factory.node.ip)
                    print("Transmitting to other nodes...")


# Used when node is acting as a server, receiving information from other nodes to verify, or from others to, for example, add a node to the network
class NodeServerFactory(protocol.ServerFactory):
    protocol = NodeAsServer

    def __init__(self, queue=None, node=None):
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


class NodeHandler(protocol.Protocol):  # Used when node sends data to other nodes

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

    def __init__(self, data=None, ip=None, port=None):
        self.data = data or "None"

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed with node", reason)

    def clientConnectionLost(self, connector, reason):
        print("Connection closed with node", reason)


class Node:
    def __init__(self, node_list=None, port=9000, pub_ip=None):

        self.node_list = connect_db.get_nodes()
        self.port = port
        if not pub_ip:
            pub_ip = get("https://api.ipify.org").text
        self.ip = pub_ip
        self.id = self.get_id()

    def get_id(self):
        file = pathlib.Path("node_id.id")
        if file.exists():
            with open("node_id.id", "r") as f:
                return f.read()
        return uuid.uuid4()

    def start_as_server(self):
        self.factory = NodeServerFactory(node=self)

        reactor.listenTCP(self.port, self.factory)

        reactor.run()

    def add_node(self, node):
        
        if len(self.node_list)< config.NETWORK_CONSTANTS["node_peers_max"]+1:
            ip, port = node[0], node[1]
            if node not in self.node_list:
                self.node_list.append(node) #fix this for efficiency
            connect_db.insert_node(ip, port)
            self.add_explore_node(node)

    def add_explore_node(self, node):
        ip, port = node[0], node[1]

        connect_db.insert_explore_node(ip, port, 0)

    def remove_node(self, node):
        print("removed node")
        ip, port = node[0], node[1]
        connect_db.remove_node(ip, port)

        self.node_list.remove(node)

    def get_nodes(self):
        nodes = connect_db.get_nodes()
        return nodes

    def transmit_data(self, data):
        try:
            data = json.loads(data)
        except Exception as e:
            print(e)
            return  # Maybe dont handle this?
        print("data sent", data)
        nodes_seen = data.get("nodes_seen", [])  # maybe change to set
        priv_ip = get_ip()
        for n in self.node_list:
            if n[0] not in nodes_seen:
                try:
                    if self.ip != n[0] and priv_ip != n[0]:

                        f = EchoFactory(data=json.dumps(data).encode(
                            "ascii"),  ip=n[0], port=n[1])
                        reactor.connectTCP(n[0], n[1], f)

                except:
                    pass

    def ping_nodes(self):
        is_connected = []
        for n in self.node_list:
            try:
                if self.ip != n[0]:

                    with Telnet(n[0], n[1], timeout=0.7) as tn:
                        tn.interact()

                    is_connected.append(True)

            except:
                is_connected.append(False)
        return is_connected

    def ping_and_remove_nodes(self):

        nodes = self.ping_nodes()
        temp = []
        for i, n in enumerate(nodes):
            if not n:
                temp.append(self.node_list[i])
        for n in temp:
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
            # Implement better node selection other than random. maybe
            nodes = random.sample(
                enodes, config.NETWORK_CONSTANTS["node_peers"] - n)
        except:
            nodes = []
        return nodes

    def update_peers(self):
        self.connect_to_peers()
        print("Updating nodes -> ", self.get_nodes())

    def start(self):
        self.connect_to_peers()
        scheduler = BackgroundScheduler(job_defaults={'max_instances': 10})
        scheduler.add_job(self.update_peers, 'interval', seconds=600)
        scheduler.start()
        print("Peers ", self.get_nodes())
        print(self.id)
        self.start_as_server()
