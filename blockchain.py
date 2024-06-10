from uuid import uuid4
import json
import hashlib
import time
from merkle_tree import *

class Transaction:
    def __init__(self, sender, recipient, amount: int):
        self.id = str(uuid4())
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def __repr__(self):
        return {
            "transaction_id": self.id,
            "sender": self.sender.id,
            "recipient": self.recipient.id,
            "amount": self.amount
        }


class Block:
    def __init__(self, transactions: list, prev_block = None):
        self.prev_hash = prev_block.hash if prev_block else None
        self.timestamp = time.time()
        self.transactions = transactions
        self.nonce = 0
        self.merkle_tree = Merkle_Tree()
        self.fill_tree()
        self.hash = self.__hash__()
        print(f"Block created. Hash: {self.hash}")

    def __repr__(self):
        return {
            "prev_hash": self.prev_hash,
            "transactions": [trans.__repr__() for trans in self.transactions],
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }

    def __hash__(self):
        if self.merkle_tree.root:
            block_str = f"{self.prev_hash}{self.nonce}{self.merkle_tree.root.hash}"
        else:
            block_str = f"{self.prev_hash}{self.nonce}"

        return hashlib.sha256(block_str.encode()).hexdigest()

    def fill_tree(self):
        for trans in self.transactions:
            self.merkle_tree.add_Node(json.dumps(trans.__repr__()))


    def validate(self, difficulty=4):
        while True:
            if self.hash[:difficulty] == '0' * difficulty:
                return True
            self.nonce += 1
            self.hash = self.__hash__()

    
    def get_info(self, data: dict):
        for trans in self.transactions:
            for client in [trans.recipient, trans.sender]:
                if client.name not in data:
                    data[client.name] = {
                        "current": client.start_balance,
                        "min": client.start_balance,
                        "max": client.start_balance
                    }

            data[trans.sender.name]['current'] -= trans.amount
            data[trans.recipient.name]['current'] += trans.amount

            data[trans.sender.name]['min'] = min(data[trans.sender.name]['min'], data[trans.sender.name]['current'])
            data[trans.recipient.name]['max'] = max(data[trans.recipient.name]['max'], data[trans.recipient.name]['current'])

        return data


class Blockchain:
    def __init__(self, difficulty = 4, mxt = 3):
        self.difficulty = difficulty
        self.max_trans = mxt

        self.chain: list[Block] = []
        self.transactions: list[Transaction] = []
        self.merkle_tree: Merkle_Tree = Merkle_Tree()
        self.block_process()


    def block_process(self, block: Block = None):
        if len(self.chain) == 0:
            block = Block([])

        block.validate(self.difficulty)
        self.chain.append(block)
        self.merkle_tree.add_Node(block.hash)

    
    def blockchain_root_hash(self):
        tree = Merkle_Tree()
        for block in self.chain:
            tree.add_Node(block.hash)

        return tree.root.hash

    
    def validate(self):
        if self.blockchain_root_hash != self.merkle_tree.root.hash:
            #print("Invalid root hash")
            return False

        for i in range(1, len(self.chain)):
            curr_block = self.chain[i]
            prev_block = self.chain[i - 1]

            if (curr_block.__hash__() != curr_block.hash) or (curr_block.prev_hash != prev_block.hash):
                print("Invalid block hash")
                return False

        return True

    def transaction_procces(self, trans: Transaction):
        self.transactions.append(trans)
        if len(self.transactions) >= self.max_trans:
            block = Block(self.transactions, self.chain[-1])
            self.block_process(block)
            self.transactions = []

    
    def get_block_info(self, id):
        block_pos = id
        if block_pos > len(self.chain):
            print("Block pos out of range")
            return

        client_balances = {}
        for i in range(block_pos+1):
            client_balances = self.chain[i].get_info(client_balances)

        return client_balances


class Client:
    def __init__(self, name, balance = 50):
        self.id = str(uuid4())
        self.name = name
        self.balance = balance
        self.start_balance = balance

    def transfer(self, recipient, amount):
        if amount > self.balance:
            print("Not enough money")
            return
        if recipient == self:
            print("Can't transfer to yourself")
        if amount < 0:
            print("Can't transfer negative amount")
        
        return Transaction(self, recipient, amount)

    def receive(self, amount):
        self.balance += amount


class Network:
    def __init__(self):
        self.blockchain = Blockchain()
        self.clients: list[Client] = []

    def add_client(self, client):
        client.network = self
        self.clients.append(client)

    def process_transaction(self, trans):
        client = next((cl for cl in self.clients if cl == trans.recipient), None)
        if not client:
            print("Recipient not found")
            return
        
        print(f"Transaction from {trans.sender.name} to {trans.recipient.name}: {trans.amount}")

        self.blockchain.transaction_procces(trans)
        client.receive(trans.amount)

    
    def save_to_json(self, path = "blockchain_data.json"):
        with open(path, 'w') as f:
            json.dump([block.__repr__() for block in self.blockchain.chain], f, indent = 4)

    
    def load_from_json(self, path = "blockchain_data.json"):
        with open(path, 'r') as f:
            data = json.load(f)
            self.blockchain = Blockchain()
            for block_data in data:
                transactions = []
                for tr in block_data['transactions']:
                    sender = next((client for client in self.clients if client.id == tr['from']), None)
                    recipient = next((client for client in self.clients if client.id == tr['to']), None)
                    transactions.append(Transaction(sender, recipient, tr['amount']))
                
                block = Block(transactions)
                block.nonce = block_data['nonce']
                block.hash = block.__hash__()
                self.blockchain.chain.append(block)

