import Quic
from Quic import *
import threading
import logging
import socket
import time
import random
FORMAT = 'utf-8'
BUFFER_SIZE = 1024
DISCONNECT_MSG = 1
SERVER_PORT = 5558
SERVER_ADDR = ("127.0.0.1", SERVER_PORT)
FILE_SIZE = (2 * 1024 * 1024) # 2MB
MAX_WAIT_TIME = 4
RETRY = 5



class Sender:
    def __init__(self, ip, port):
        self.addr = (ip, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.streams = random.randint(1,10)
        self.size_of_frame = random.randint(1000,2000)
        self.packet_count = 0


    # Waits for ack for MAX_WAIT_TIME seconds.
    # @param sequence number - sequence number of the packet.
    # return True if received an ack from the server, False if didnt receive ack after MAX_WAIT_TIME seconds.
    def wait_for_ack(self, sequence_number):
        start_time = time.time()
        while True:
            if time.time() - start_time >= MAX_WAIT_TIME:
                break
            packet, add = self.__sock.recvfrom(1024)
            packet = packet.decode(FORMAT)
            recv_packet = Quic.desirialize(packet)
            if recv_packet.header.flags.syn and recv_packet.header.flags.ack == 1 and recv_packet.header.packet_number == sequence_number:
                print("Received ack for handShake packet.")
                return True
            if recv_packet.header.flags.syn and recv_packet.header.packet_number == sequence_number:
                return True

        print("Was not able to receive ack. Try again \n")
        return False



    # Function that sends syn request to establish communication with the server.
    # The function sends packet with syn ack = 1, then waits for confirmation from the server.
    # In our implementation, the server address is fixed.
    # returns True if recevied positve answer from the server, False if couldnt receive response after RETRY attempts.
    def handshake(self):
        for i in range(RETRY):
            flags = QuicHeaderFlags(ack = 0,syn= 1,data= 0,fin= 0)
            header = QuicHeader(flags=flags, packet_number = self.packet_count, connection_id=SERVER_ADDR)
            send_packet = QuicPacket(header=header)
            self.__sock.sendto(send_packet.serialize, SERVER_ADDR)
            if self.wait_for_ack(self.packet_count):
                self.packet_count += 1
                return True
        print("Not able to open a connection with the server. Try to send again.\n")
        return False

        

    # Haven't implemented it fully yet
    def quic_send(self, data):
        packet_number = self.packet_count
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
    
    # Generates sets of data. The size of the sets are equal.
    # @param num_sets - The number of sets to generate.
    # @param size_in_mb - The size of each set in MB (Mega Byte).
    def generate_data_sets(num_sets=10, size_in_mb=1):
        data_sets = []
        for i in range(num_sets):
            data = ''.join(random.choices(string.ascii_letters + string.digits, k=1024 * 1024 * size_in_mb))
            data_sets.append((i, data))
        return data_sets
    



class Receiver:
    def __init__(self, host, port):
        self.__addr = (host, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
        print("Socket created")
        self.__sock.bind(self.__addr)
        self.files = []
        self.streams = 0
        self.size_of_frame = 0

    # Haven't implemented it yet
    def handshake(self):
        pass

    # Haven't implemented it yet
    def send(self, packet : QuicPacket, client_ip):
        logging.info(f"Sending {packet.data} to {client_ip}")
        self.__sock.sendto(packet.serialize().encode(FORMAT), client_ip)

    # Haven't implemented it yet
    def receive(self):
        packet , clinet_addr = self.__sock.recvfrom(BUFFER_SIZE)
        packet = packet.decode(FORMAT).deserialize()
        return packet
        
        #self.streams.remove(recv_packet.packet_number)
        # print("Closing the socket")
        # self.running = False


    # Listens for packets and opens new thread when packet arrives
    def listen(self):
        print(f"Listening on {self.__addr[0]}:{self.__addr[1]}")
        #while self.running:
        packet, client_addr = self.__sock.recvfrom(BUFFER_SIZE)  # accept communication
        # packet = packet.decode(FORMAT)
        # reconstract the packet.
        recv_packet = Quic.QuicPacket.deserialize(packet)
        
        print(f"Received data for packet {recv_packet.header.packet_number}: of size ")
        print(recv_packet)
        # If received a disconnect message, close.
        if recv_packet.header.flags.fin == DISCONNECT_MSG:
            print(f"Received close packet!")
            self.running = False
            return
        # for each frame received, add 
        for frame in recv_packet.payload:
            if frame.stream_id >= len(self.files):
            # Extend the list to have enough elements
                self.files.extend([""] * (frame.stream_id - len(self.files) + 1))
            self.files[frame.stream_id] += frame.data.decode(FORMAT)      
            print(f"Received {client_addr} {frame.data}")

        # when it stops.
        print("Closing socket! Program finished.")
        self.__sock.close()

    # Haven't implemented it yet
    def send_ack(self, ):
        pass
