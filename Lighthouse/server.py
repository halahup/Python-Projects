from peewee import *
import socket
from hashlib import sha256
from json import dumps
import json
import os

db_user = SqliteDatabase('users.db')
db_transaction = SqliteDatabase('transactions.db')
db_miner = SqliteDatabase('miners.db')

TCP_IP = '127.0.0.1'
TCP_PORT = 4025
NUM_CONN = 1
BUFFER = 10240


# database model for the user in the network
class User(Model):
    """
        Database model to store the users, registered to the chain
    """
    user_id = CharField(unique=True)
    user_ip = CharField(unique=False)
    public_key = CharField(unique=True)
    user_port = CharField(unique=False)

    class Meta:
        database = db_user


# database model for the miners
class Miner(Model):
    """
        Database model to store the miners, registered to the chain
    """
    miner_id = CharField(unique=True)
    miner_ip = CharField(unique=False)
    miner_port = CharField(unique=False)

    class Meta:
        database = db_miner


# database model for the transactions
class Trans(Model):
    """
        Database model to store the transactions
    """
    trans = CharField(unique=True)
    id = CharField()

    class Meta:
        database = db_transaction


class Server:

    _outstanding_pool = list()

    def __init__(self, ip, port, sock=None):
        """
            Init with ip, port and socket
        """
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        # bind the ip and the port
        self.sock.bind((ip, port))

    def enter_loop(self):
        """
            Main loop to handle the server operations
        """

        # connect the databases
        # connect the user database
        db_user.connect()
        db_user.create_tables([User], safe=True)

        # create the test user
        # creates multiple users
        try:
            User.create(user_id='0', user_ip='0.0.0.0', public_key="pub_key", user_port="0")
        except IntegrityError:
            pass

        # connect the transaction database
        db_transaction.connect()
        db_transaction.create_tables([Trans], safe=True)

        # connect the miner database
        db_miner.connect()
        db_miner.create_tables([Miner], safe=True)

        # listen for incoming connections
        self.sock.listen(NUM_CONN)

        # main server loop
        while True:

            # accept the incoming connection
            conn, addr = self.sock.accept()

            print("Connected to {}".format(addr))
            # data = loads(conn.recv(BUFFER))
            data = json_loads_byteified(conn.recv(BUFFER))

            # if the data we receive has a user register header
            # register the user
            if data['meta'] == "user_register":

                # register the user in the database
                try:
                    User.create(user_ip=addr[0],
                                user_port=addr[1],
                                user_id=data['id'],
                                public_key=data['public_key'])

                    conn.send('100')

                except IntegrityError:
                    print("The user is already with this id: {} is already in the database".
                          format(sha256(data['id']).hexdigest()))

                    user_record = User.get(user_hash=sha256(data['id']).hexdigest())

                    # update ip address if needed
                    user_record.user_ip = addr
                    user_record.save()

                    print("Updated the ip address")

                    conn.send("200")
                finally:
                    conn.close()

            elif data['meta'] == "miner_register":

                try:

                    # create a user in the database
                    User.create(user_ip=addr[0],
                                user_port=addr[1],
                                user_id=data['id'],
                                public_key=data['public_key'])

                    # create a miner in the database with the same id
                    Miner.create(miner_id=data['id'],
                                 miner_ip=addr[0],
                                 miner_port=addr[1])

                    # response
                    conn.send('100')

                except IntegrityError:
                    print "Debug me"

            # another kind of incoming data can be a transaction
            elif data['meta'] == "transaction":

                try:
                    Trans.create(trans=dumps(data["transaction"]), id=data["transaction"]["signature"])

                    # response
                    conn.send("100")

                except Exception as e:
                    print "Error", e

            # if a miner requests transactions
            elif data['meta'] == "transaction_request":

                transactions = list()
                for transaction in Trans.select():
                    transactions.append(transaction.trans)

                # send the data
                conn.send("+++++".join(transactions))

            # the client requests block chain
            elif data["meta"] == "block_chain_request":

                conn.send("Here is the block chain goes back the channel")
                # the miner requesting the current block-chain
                pass

            # redirect block to a miner
            # elif data['meta'] == 'block_chain_submit':
            #
            #     chain = list()
            #
            #     if os.path.isfile('block_chain.txt'):
            #
            #         # update the chain
            #         with open("block_chain.txt", "r") as blck_obj:
            #             chain = blck_obj.readlines()
            #
            #         chain.append(data["chain"])
            #
            #         print chain
            #
            #         with open("block_chain.txt", "w") as blck_obj:
            #             blck_obj.writelines(chain)
            #
            #         # send the response
            #         conn.send("100")
            #
            #     else:
            #
            #         with open("block_chain.txt", "w") as blck_obj:
            #             blck_obj.writelines(data["chain"])
            #
            #         # send the response
            #         conn.send("100")





            #print("Received data: {}".format(data))

            # send the public key back
            # conn.send(data)
            # feedback
            # conn.send("Printed to console: {}".format(data))










def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

















def main():

    server = Server(TCP_IP, TCP_PORT)
    server.enter_loop()

if __name__ == "__main__":
    main()
