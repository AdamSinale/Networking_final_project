
import socket
import random
import string
import time

# needs to import Quic from quic.py
from quic import *

# Function to fill the remaining data space to the smallest frame's data.
def add_to_min_frame(frames, space_left, offsets, packet_data):
    min_frame = frames[0]
    min_index = 0
    for i, frame in enumerate(frames):
        if frame.offset < min_frame.offset:
            min_frame = frame
            min_index = i
    min_frame.data += packet_data[min_index][1][offsets[min_frame.stream_id]: offsets[min_frame.stream_id] + space_left]
    min_frame.length = len(min_frame.data)
    offsets[min_frame.stream_id] += space_left
    return frames
# Function to find the length of the data with the given ID
def data_len_by_id(data, id):
    for file in data:
        if file[0] == id:
            return len(file[1])
    return -1
# Function to generate data sets.
def generate_data_sets(num_sets=10, size_in_mb=1):
    data_sets = []
    for i in range(num_sets):
        data_set = ''.join(random.choices(string.ascii_letters + string.digits, k=1024 * 1024 * size_in_mb + 13))
        data_sets.append((i, data_set))
    return data_sets

packet_size = random.randint(1000, 2000)
MAX_WAIT_TIME = 5
packet_number = 1

class Sender:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Function to send a handshake packet to the server.
    # The function waits MAX_WAIT_TIME seconds to receive an ack for the handshake packet.
    def handshake(self):
        flags = QuicHeaderFlags(ack=0, syn=1, data=0, fin=0)
        header = QuicHeader(flags=flags, packet_number=1, connection_id=1)
        frames = [QuicFrame(1, 0, 5, "Hello")]
        packet = QuicPacket(header, frames)
        self.sock.sendto(packet.serialize(), (self.ip, self.port))
        self.wait_for_ack()

    # Function to start the sender.
    def start(self, streams_number):
        self.handshake()
        data = generate_data_sets(streams_number, 1)
        self.udp_send(data)
        self.finish_connection(packet_number)
        self.sock.close()
        return data

    # Function to send a fin packet to the server.
    def finish_connection(self,packet_number):
        flags = QuicHeaderFlags(ack=0, syn=0, data=0, fin=1)
        header = QuicHeader(flags=flags, packet_number=packet_number, connection_id=1)
        frames = [QuicFrame(1, 0, 8, "Good Bye")]
        packet = QuicPacket(header, frames)
        self.sock.sendto(packet.serialize(), (self.ip, self.port))

    # Function that creates each sent packet.
    # chooses randomly 60% of the files, adds the current data chunck to each frame
    def create_packet(self, packet_number, data, offsets):
        flags = QuicHeaderFlags(ack=0, syn=0, data=1, fin=0)            # packet flags for data
        space_left = 0                                                  # set the space left for when we have small data left to send from the file
        frames_num = round(len(data)*0.6)                               # 60% of streams will be send
        frame_size = round(packet_size / frames_num)
        header = QuicHeader(flags=flags, packet_number=packet_number, connection_id=1)  # the header of the packet
        frames = []                                                     # the frames list we will send
        packet_data = random.sample(data, frames_num)                   # the 60% will be randomly chosen
        for frames_id, frames_data in packet_data:                      # for each chosen stream
            if offsets[frames_id] > len(frames_data) - frame_size:      # if we have smaller than set length to send
                space_left += len(frames_data) - offsets[frames_id]     # add the length we have left
            chunck_data = frames_data[offsets[frames_id]: offsets[frames_id] + frame_size]  # we will take the defined size data from the current offset
            frames.append(QuicFrame(frames_id, offsets[frames_id], len(chunck_data), chunck_data))  # we will add it as frame with stream-id, offset, length, data
            offsets[frames_id] += frame_size                            # set the offset to next
            if (offsets[frames_id] >= data_len_by_id(data, frames_id)): #
                data.remove((frames_id, frames_data))
        if space_left > 0:
            frames = add_to_min_frame(frames, space_left, offsets, packet_data)
        return QuicPacket(header, frames), data, offsets

    # Function to send data to the server.
    # The function sends 60% of the data in random order - as asked.
    def udp_send(self, sent_data):
        data = list(sent_data)
        packet_number = 2
        offsets = [0 for _ in range(len(data))]                  # array of current chuck sent
        while len(data) > 0:                                     # while there is data left to send
            packet, data, offsets = self.create_packet(packet_number, data, offsets)
            self.sock.sendto(packet.serialize(), (self.ip, self.port))
            time.sleep(0.0005)
            packet_number += 1


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
                print("Received ack for handShake packet.")
                return True
            elif recv_packet.header.flags.ack:  # if its a response for data packet.
                return True
            return False
        print("Was not able to receive ack. Try again \n")
        return False

