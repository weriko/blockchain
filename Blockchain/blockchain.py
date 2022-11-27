import hashlib as hs
import time
import json
from block import Block


class Blockchain():

    def __init__(self):

        self.blocks = []

        self.dif = 2**250
        self.next_hash = 0x0
        self.max_nonce = int(1e10)

    def mine(self, block):
        # print(self.next_hash)

        block.prev_hash = self.next_hash

        for nonce in range(self.max_nonce):

            block.self_hash(nonce)

            if int(block.hash, 16) < self.dif:
                block.nonce = nonce
                self.blocks.append(block)
                # print(block.hash)
                self.next_hash = block.hash
                block.no = len(self.blocks)

                break

    def save(self, path):
        dic = {}

        for i, block in enumerate(self.blocks):
            dic[str(i)] = block.__dict__

        print(dic)

        with open(path, "w") as json_file:
            json.dump(dic, json_file)

    def load(self, path):
        with open(path, 'r') as f:
            dic = json.load(f)

        blocks = list(dic.values())

        # print(blocks)

        for i in range(len(blocks)-1):
            if hs.sha256(str(blocks[i]["data"] + str(blocks[i]["prev_hash"]) + str(blocks[i]["nonce"]) + str(blocks[i]["time"])).encode()).hexdigest() == blocks[i+1]["prev_hash"]:
                self.blocks.append(Block(blocks[i]["data"], blocks[i]["prev_hash"], blocks[i]
                                   ["hash"], blocks[i]["nonce"], blocks[i]["time"], blocks[i]["no"]))
            else:
                print("Error checking")
                print(i)

        self.blocks.append(Block(blocks[-1]["data"], blocks[-1]["prev_hash"], blocks[-1]
                           ["hash"], blocks[-1]["nonce"], blocks[-1]["time"], blocks[-1]["no"]))
        self.next_hash = blocks[-1]["hash"]
