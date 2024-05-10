import socket
import random
import string

# needs to import Quic and Flags from quic.py
from quic import *

def data_len_by_id(data, id):
    for file in data:
        if file[0] == id:
            return len(file[1])
    return -1
frame_size = 1024
class Sender:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handshake(self):
        flags = QuicHeaderFlags(ack=0, syn=1, data=0, fin=0)
        header = QuicHeader(flags=flags, packet_number=1, connection_id=1)
        frames = [QuicFrame(1, 0, 5, "Hello")]
        packet = QuicPacket(header, frames)
        self.sock.sendto(packet.serialize(), (self.ip, self.port))
        # server_hello, server_addr = self.sock.recvfrom(1024)

    def udp_send(self, data):
        packet_number = 2
        offsets = [0 for _ in range(len(data))]
        flags = QuicHeaderFlags(ack=0, syn=0, data=1, fin=0)

        while len(data) > 0:
            frames_num = round(len(data)*0.6)
            header = QuicHeader(flags=flags, packet_number=packet_number, connection_id=1)
            frames = []

            packet_data = random.sample(data, frames_num)
            for frames_id, frames_data in packet_data:
                chunck_data = frames_data[offsets[frames_id] : offsets[frames_id] + frame_size]
                frames.append(QuicFrame(frames_id, offsets[frames_id], len(chunck_data), chunck_data))
                offsets[frames_id] += frame_size
                if(offsets[frames_id] >= data_len_by_id(data, frames_id)):
                    data.remove((frames_id,frames_data))
            packet = QuicPacket(header, frames)
            serialized_packet = packet.serialize()
            deserialized_packet = QuicPacket.deserialize(packet.serialize())
            self.sock.sendto(packet.serialize(), (self.ip, self.port))
            packet_number += 1
            # self.receive_ack()
        self.sock.close()

    def receive_ack(self):
        data, addr = self.sock.recvfrom(1024)
        print(data.decode())

def generate_data_sets(num_sets=10, size_in_mb=1):
    data_sets = []
    for i in range(num_sets):
        data = ''.join(random.choices(string.ascii_letters + string.digits, k=1024 * 1024 * size_in_mb))
        data_sets.append((i, data))
    return data_sets

sender = Sender('127.0.0.1', 1111)
sender.handshake()
data = generate_data_sets(5, 1)
sender.udp_send(data)
