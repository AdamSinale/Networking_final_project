# This file contains function relatable to sender and receiver.
from socket import *


# Class representing quic packet.
# @param data - the data sent.
# @param data_size - the size of the data in bytes.
# @param flags - packet's flags.
# @param packet_number - packet's unique sequence number.
# @param encryption_key - set to zero since no implementation required.
class Quic:
    def __init__(self, data, data_size, flags, packet_number):
        self.data = data
        self.data_size = data_size
        self.flags = flags
        self.packet_number = packet_number

# Class representing QUIC packet's flags
# @param ack - 1 if the packet is a connection request packet, else 0.
# @param syn - 1 if the packet is a syn packet, else 0.
# @param fin - 1 if the packet is closing request packet, else 0.
# @param data - 1 if the packet contains data, else 0.
class Flags:
    def __init__(self, ack, syn, fin, data):
        self.ack = ack    # first frame of the stream
        self.syn = syn    # first frame of the stream
        self.data = data  # second to second-to-last of the stream
        self.fin = fin    # last frame of the stream

# Class representing a client
class Client:
    def __init__(self, ip, port, id_num):
        self.ip = ip
        self.port = port
        self.id_num = id_num

    def connect(self):
        pass









