import hashlib
import json
import logging
import time

block = ''' 
hash : %s           
+%s+
  version :   %s 
  prehash :   %s 
  timestamp : %s 
  nonce :     %s 
  target:     %s 
  mercle:     %s 
+%s+
  trans :     %s 
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

    def __init__(self, timestamp, transactions, difficulty, preHash=''):
        # body
        self.transactions = transactions

        # header
        self.version = '1.0'
        self.nonce = 0
        self.timestamp = timestamp
        self.merkleHash = self.merkleRootHash()
        self.preHash = preHash
        self.difficulty = difficulty

        self.hash = self.headerHash()

    def headerHash(self):
        return sha256(sha256(self.merkleHash + self.timestamp + self.preHash + str(self.nonce) + self.version + str(self.difficulty)))

    def merkleRootHash(self):
        return sha1(json.dumps(self.transactions))

    # PoW
    def mineBlock(self, target):
        while self.hash[0:target] != '0'*target:
            self.nonce += 1
            self.hash = self.headerHash()
        # print("BLOCK MINED: " + self.hash)


class BlockChain:

    def __init__(self):
        self.chain = [self.createGenesisBlock()]
        # 比特币最低难度取值nBits=0x1d00ffff，对应的最大目标值为：0x00000000FFFF0000000000000000000000000000000000000000000000000000
        # 这里简化计算
        self.maxTarget = 10
        self.difficulty = 2
        # 存储交易
        self.pendingTransactions = []

        # 回报
        self.miningReward = 2.33
        self.totalfees = 0

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
        self.pendingTransactions.append(transaction.getTran())
        self.totalfees += transaction.getFees()

    def minePendingTransactions(self, miningRewardAddress):
        # 计算coinbase & 创建新的区块
        coinbaseTX = Transaction('coinbase', miningRewardAddress, self.miningReward + self.totalfees, 0)
        self.pendingTransactions.append(coinbaseTX.getTran())
        block = Block(time.strftime('%Y/%m/%d',time.localtime(time.time())), self.pendingTransactions, self.difficulty)
        block.preHash = self.getLastBlock().hash

        # 简化算法，挖矿传参为前导零个数，而非实际的区块难度目标值
        block.mineBlock(int(self.maxTarget/self.difficulty))

        # 上链
        self.chain.append(block)

        # 重置待处理交易列表
        self.pendingTransactions = [
            Transaction(None, None, self.miningReward, 0).getTran()
        ]
        self.totalfees = 0

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
            print(block % (c.hash, '-'*90, c.version ,c.preHash, c.timestamp, str(c.nonce),
                           str(self.difficulty), c.merkleHash, '-'*90, json.dumps(c.transactions), '-'*90))

class Transaction:

    def __init__(self, fromAddr, toAddr, amount, fees):
        self.fromAddr = fromAddr
        self.toAddr = toAddr
        self.amount = amount
        self.fees = fees

    def getTran(self):
        return {'from': self.fromAddr, 'to': self.toAddr, 'amount': self.amount}

    def getFees(self):
        return self.fees

def test():
    # 创建tt币
    ttCoin = BlockChain()

    # 增加两笔交易
    TA = Transaction('testA', 'testB', 99, 2)
    ttCoin.createTransaction(TA)
    TB = Transaction('testD', 'testC', 51, 1)
    ttCoin.createTransaction(TB)

    # 挖矿
    starttime = time.time()
    ttCoin.minePendingTransactions('miner')
    endtime = time.time()
    # print(ttCoin.getBalanceOfAddress('miner'))
    ttCoin.outBC()
    print(endtime - starttime)

    # print(ttCoin.isChainValid())
    # ttCoin.chain[1].transactions = {'amount': 100}
    # print(ttCoin.isChainValid())

if __name__ == '__main__':
    test()