# 



import socket
import random
import string
import time

# needs to import Quic and Flags from quic.py
from quic import *

def data_len_by_id(data, id):
    for file in data:
        if file[0] == id:
            return len(file[1])
    return -1
MAX_WAIT_TIME = 5

class Sender:
    def __init__(self, ip, port, number_of_streams):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.frame_size = random.randint(1000, 2000)
        self.streams = number_of_streams

    def set_sreams(self, streams):
        self.streams = streams

    # Function to start the sender.
    def start(self):
        self.handshake()
        data = generate_data_sets(self.streams, 1)
        self.udp_send(data)

    # Function to send a handshake packet to the server.
    # The function waits MAX_WAIT_TIME seconds to receive an ack for the handshake packet.
    def handshake(self):
        flags = QuicHeaderFlags(ack=0, syn=1, data=0, fin=0)
        header = QuicHeader(flags=flags, packet_number=1, connection_id=1)
        frames = [QuicFrame(1, 0, 5, "Hello")]
        packet = QuicPacket(header, frames)
        self.sock.sendto(packet.serialize(), (self.ip, self.port))
        self.wait_for_ack()

    # Function to send a fin packet to the server.
    def finish_connection(self,packet_number):
        flags = QuicHeaderFlags(ack=0, syn=0, data=0, fin=1)
        header = QuicHeader(flags=flags, packet_number=packet_number, connection_id=1)
        frames = [QuicFrame(1, 0, 8, "Good Bye")]
        packet = QuicPacket(header, frames)
        self.sock.sendto(packet.serialize(), (self.ip, self.port))
        # self.wait_for_ack()

    # Function to add the remaining data to the smallest frame.
    def add_to_min_frame(self, frames, space_left, offsets, packet_data):
        frame_size = self.frame_size
        min_frame = frames[0]
        min_index = 0
        for i, frame in enumerate(frames):
            if frame.offset < min_frame.offset:
                min_frame = frame
                min_index = i
        min_frame.data += packet_data[min_index][1][offsets[min_frame.stream_id]+ frame_size : offsets[min_frame.stream_id]+ frame_size+space_left]
        offsets[min_frame.stream_id] += space_left
        min_frame.length += space_left
        return frames


    # Function to send data to the server.
    # The function sends 60% of the data in random order - as asked by the teacher.
    def udp_send(self, data):
        packet_number = 2
        offsets = [0 for _ in range(len(data))]                  # array of current chuck sent
        flags = QuicHeaderFlags(ack=0, syn=0, data=1, fin=0)     # packet flags for data
        space_left = 0
        while len(data) > 0:                                     # while there is data left to send
            frames_num = round(len(data)*0.6)                    # 60% of streams will be send
            header = QuicHeader(flags=flags, packet_number=packet_number, connection_id=1)
            frames = []
            packet_data = random.sample(data, frames_num)       # the 60% will be randomly chosen
            for frames_id, frames_data in packet_data:          # for each chosen stream
                if offsets[frames_id] > len(frames_data)-self.frame_size:
                    space_left += len(frames_data) - offsets[frames_id]
                chunck_data = frames_data[offsets[frames_id] : offsets[frames_id] + self.frame_size]         # we will take the defined size data from the current offset
                frames.append(QuicFrame(frames_id, offsets[frames_id], len(chunck_data), chunck_data))  # we will add it as frame with stream-id, offset, length, data
                offsets[frames_id] += self.frame_size                                                        # set the offset to next
                if(offsets[frames_id] >= data_len_by_id(data, frames_id)):
                    data.remove((frames_id,frames_data))
            if space_left > 0:
                frames = Sender.add_to_min_frame(self, frames, space_left, offsets, packet_data)
                space_left = 0
            packet = QuicPacket(header, frames)
            self.sock.sendto(packet.serialize(), (self.ip, self.port))
            time.sleep(0.0005)
            packet_number += 1
        self.finish_connection(packet_number)
        self.sock.close()
        
    # Function to wait for an ack from the server.
    # The function waits MAX_WAIT_TIME seconds to receive an ack.
    # If received an ack, returns True, else False.
    def wait_for_ack(self):
        start_time = time.time()
        while True:
            if time.time() - start_time >= MAX_WAIT_TIME:
                break
            packet, add = self.sock.recvfrom(1024)
            recv_packet = QuicPacket.deserialize(packet)
            # if its a response for handshake packet.
            if recv_packet.header.flags.syn and recv_packet.header.flags.ack:
                print("Connection established!")
                return True
            # if its a response for data packet.
            elif recv_packet.header.flags.ack:
                return True
            else:
                return False

        print("Was not able to receive ack. Try again \n")
        return False
    
    
    

# Function to generate data sets.
def generate_data_sets(num_sets=10, size_in_mb=1):
    data_sets = []
    for i in range(num_sets):
        data = ''.join(random.choices(string.ascii_letters + string.digits, k=1024 * 1024 * size_in_mb))
        data_sets.append((i, data))
    return data_sets




