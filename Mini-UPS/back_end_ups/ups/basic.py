import psycopg2
import socket
import world_ups_pb2, amazon_ups_pb2
import sys
import threading
import select

from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint

# Send and receive message
def send_msg(socketfd, msg):
    _EncodeVarint(socketfd.send, len(msg), None)
    socketfd.sendall(msg)

def receive_msg(socket):
    var_int_buff = []
    while True:
        try:
            buf = socket.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        except:
            whole_message = []
            return whole_message
    whole_message = socket.recv(msg_len)
    return whole_message


# Connect to the database
def connect_to_database():
    try:
        conn = psycopg2.connect(database="xvuptemb", user="xvuptemb", password="9mf588qMKRBoUm7HQ-L_0zxRuZNgE7ZA", host="drona.db.elephantsql.com", port="5432")
        print ('Open the databse upsDB created by Django')
        return conn
    except:
        print ('Cannot connect to the database')