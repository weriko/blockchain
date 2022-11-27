import hashlib as hs
import time
import json
from dataclasses import dataclass
from bitcoinutils.transactions import Transaction
@dataclass
class Block():
    Version:int
    hashPrevBlock:bytes
    tx:list
    Bits:int
    Nonce:int=0
    Time:int = time.time()
    magic_no:bytes=bytes.fromhex("D9B4BEF9")

    def __init__(self, tx, prev_hash = 0x0, Hash = 0x0, nonce = 0, Time = 0, no = 0):     
        self.data = data
        self.prev_hash = prev_hash
        self.hash = Hash
        self.nonce = nonce
        if Time == 0:
            self.time = time.time()
        else:
            self.time = Time
        self.no = no    
    def get_tx_hashes(self,tx):
        txhash = [Transaction.from_raw(x) for x in tx]

    def get_header(self):
        data = self.Version+self.hashPrevBlock+self.get_merkle(self.get_tx_hashes(self.tx))+self.Time+self.Bits+self.Nonce
        assert (len(data)==80), "Header should be 80 bytes long"
        return data
    def construct(self):
        data = {}
        data["magic_no"] = self.magic_no #fix tx counter varint
        data["blocksize"] = 80+len(self.tx)+[len(x) for x in self.tx]
        data["blockheader"] = self.get_header()
        data["tx_counter"] = len(self.tx)
        data["tx"] = self.tx
        return json.dumps(data)
    
    def get_merkle(self, tx):

        if len(tx) == 1:
            return tx[0]
        newtx = []
        for i in range(0, len(tx)-1, 2):
            h = hs.sha256(hs.sha256(tx[i][::-1]+tx[i+1][::-1]).digest()).digest()[::-1]
            newtx.append(h)
        if len(tx) % 2 != 0: 
            h = hs.sha256(hs.sha256(tx[-1][::-1]+tx[-1][::-1]).digest()).digest()[::-1]
            newtx.append(h)
        return self.get_merkle(newtx)
    
    def self_hash(self, nonce):
        return hs.sha256(self.get_header())
        

