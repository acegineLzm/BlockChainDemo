import hashlib
import json
import logging
import time

# logger = logging.getLogger('DEMO')
# formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
# console_handler = logging.StreamHandler()
# console_handler.formatter = formatter
# logger.addHandler(console_handler)
# logger.setLevel(logging.DEBUG)

block = ''' 
            hash : %s           
            +%s+
            | version :   %-90s |
            | prehash :   %-90s |
            | timestamp : %-90s |
            | nonce :     %-90s |
            | target:     %-90s |
            | mercle:     %-90s |
            +%s+
            | trans :     %-90s |
            +%s+ 
                      |                    
                      |
                      V
        '''

def sha256(str):
    sha256 = hashlib.sha256()
    sha256.update(str.encode('utf-8'))
    return sha256.hexdigest()

def sha1(str):
    sha1 = hashlib.sha1()
    sha1.update(str.encode('utf-8'))
    return sha1.hexdigest()

class Block:

    def __init__(self, timestamp, transactions, preHash=''):
        self.version = '1.0'
        self.nonce = 0
        self.timestamp = timestamp
        self.transactions = transactions
        self.merkleHash = self.merkleRootHash()
        self.preHash = preHash
        self.hash = self.headerHash()

    def headerHash(self):
        return sha256(self.merkleHash + self.timestamp + self.preHash + str(self.nonce) + self.version)

    def merkleRootHash(self):
        return sha1(json.dumps(self.transactions))

    # PoW
    def mineBlock(self, difficulty):
        while self.hash[0:difficulty] != '0'*difficulty:
            self.nonce += 1
            self.hash = self.headerHash()
        # print("BLOCK MINED: " + self.hash)


class BlockChain:

    def __init__(self):
        self.chain = [self.createGenesisBlock()]
        self.difficulty = 4
        # 在区块产生之间存储交易的地方
        self.pendingTransactions = []

        # 挖矿回报
        self.miningReward = 100

    def createGenesisBlock(self):
        return Block('17/3/2018', 'Genesis block', '0')

    def getLastBlock(self):
        return self.chain[len(self.chain) - 1]

    # def addNewBlock(self, newBlock):
    #     newBlock.preHash = self.getLastBlock().hash
    #     # newBlock.hash = newBlock.calculateHash()
    #     newBlock.mineBlock(self.difficulty)
    #     self.chain.append(newBlock)

    def createTransaction(self, transaction):
        self.pendingTransactions.append(transaction)

    def minePendingTransactions(self, miningRewardAddress):
        # 用所有待交易来创建新的区块并且开挖..
        block = Block(time.strftime('%Y/%m/%d',time.localtime(time.time())), self.pendingTransactions)
        block.preHash = self.getLastBlock().hash
        block.mineBlock(self.difficulty)

        # 将新挖的看矿加入到链上
        self.chain.append(block)

        # 重置待处理交易列表并且发送奖励
        self.pendingTransactions = [
            Transaction(None, miningRewardAddress, self.miningReward).getTran()
        ]

    def getBalanceOfAddress(self, addr):
        balance = 0
        for block in self.chain:
            for t in block.transactions:
                if isinstance(t, str):
                    continue
                if t['from'] == addr:
                    balance -= t['amount']
                if t['to'] == addr:
                    balance += t['amount']
        return balance

    def isChainValid(self):
        for i in range(1, len(self.chain)):
            curBlock = self.chain[i]
            preBlock = self.chain[i-1]
            if curBlock.hash != curBlock.headerHash():
                return 'False'
            if curBlock.preHash != preBlock.hash:
                return 'False'
        return 'True'

    def outBC(self):
        for c in self.chain:
            print(block % (c.hash, '-'*104, c.version ,c.preHash, c.timestamp, str(c.nonce),
                           str(self.difficulty), c.merkleHash, '-'*104, json.dumps(c.transactions), '-'*104))

class Transaction:

    def __init__(self, fromAddr, toAddr, amount):
        self.fromAddr = fromAddr
        self.toAddr = toAddr
        self.amount = amount

    def getTran(self):
        return {'from': self.fromAddr, 'to': self.toAddr, 'amount': self.amount}

def test():
    # 创建lzm币
    lzmCoin = BlockChain()

    # 增加两笔交易
    lzmCoin.createTransaction(Transaction('aaa', 'bbb', 100).getTran())
    lzmCoin.createTransaction(Transaction('ddd', 'ccc', 51).getTran())

    # 挖矿
    lzmCoin.minePendingTransactions('lzmaddr')
    print(lzmCoin.getBalanceOfAddress('lzmaddr'))
    lzmCoin.outBC()

    # 奖励在下一个区块中
    # lzmCoin.minePendingTransactions('lzmaddr')
    # print(lzmCoin.getBalanceOfAddress('lzmaddr'))
    # lzmCoin.outBC()

    # print(lzmCoin.isChainValid())
    # lzmCoin.chain[1].transactions = {'amount': 100}
    # print(lzmCoin.isChainValid())

if __name__ == '__main__':
    test()