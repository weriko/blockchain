import node
import json
import sys
import config
def main():
    with open("nodes.json","r") as nd:
        port = config.NETWORK_CONSTANTS["port"]
        args = sys.argv
        if len(args)>1:
            port = int(args[1])

        j = json.load(nd)["data"]
        print(j)
        n = node.Node(node_list=j, port = port, pub_ip = None)
        
        print("Starting...")
        n.start()
    


if __name__ == '__main__':
    main()