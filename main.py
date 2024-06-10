from blockchain import *


def main():
    network = Network()

    Alice = Client("Alice", 6000)
    Bob = Client("Bob", 4000)
    Charlie = Client("Charlie", 2000)
    network.add_client(Alice)
    network.add_client(Bob)
    network.add_client(Charlie)

    transactions = [
        Alice.transfer(Bob, 150),
        Alice.transfer(Charlie, 200),
        Bob.transfer(Alice, 50),
        Bob.transfer(Charlie, 400),
        Charlie.transfer(Alice, 300)
    ]

    for trans in transactions:
        network.process_transaction(trans)


    #proof of work
    if network.blockchain.chain[1].validate():
        print("Valid proof of work\n")
    else:
        print("Invalid proof of work\n")


    block_info = network.blockchain.get_block_info(1)
    for client, info in block_info.items():
        print(f"Client: {client}, Current balance: {info['current']}, min balance: {info['min']}, max balance: {info['max']}")


    network.save_to_json()


if __name__ == '__main__':
    main()