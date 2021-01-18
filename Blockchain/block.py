import hashlib as hs
import time
import json

class Block():
    def __init__(self, data, prev_hash = 0x0, Hash = 0x0, nonce = 0, Time = 0, no = 0):     
        self.data = data
        self.prev_hash = prev_hash
        self.hash = Hash
        self.nonce = nonce
        if Time == 0:
            self.time = time.time()
        else:
            self.time = Time
        self.no = no    
    def __str__(self):      
        return f"data: {self.data}, prev_Hash:  {self.prev_hash}, Nonce:  {self.nonce} "
   
    def self_hash(self, nonce):
        self.hash = hs.sha256((str(self.data) + str(self.prev_hash) + str(nonce) + str(self.time)).encode()).hexdigest()
        

