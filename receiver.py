import socket

# needs to import Quic and Flags from quic.py
from quic import *
import logging
import time
import socket
FORMAT = 'utf-8'
BUFFER_SIZE = (1024+1000) * 3
DISCONNECT_MSG = 1
SERVER_PORT = 5558
MAX_WAIT_TIME = 5

class Receiver:
    def __init__(self, host, port):
        self.__addr = (host, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind(self.__addr)
        self.files = []
        print("Socket created")

    # Haven't implemented it yet
    def send(self, packet: QuicPacket, client_ip):
        logging.info(f"Sending {packet.data} to {client_ip}")
        self.__sock.sendto(packet.serialize().encode(FORMAT), client_ip)

    # Haven't implemented it yet
    def receive(self):
        packet, client_addr = self.__sock.recvfrom(BUFFER_SIZE)
        d_packet = QuicPacket.deserialize(packet)
        return d_packet, client_addr

    def wait_for_connection(self):
        start_time = time.time()
        while True:
            if time.time() - start_time >= MAX_WAIT_TIME * 10:
                break
            packet, client_addr = self.receive()
            if packet.header.flags.syn:  # Make sure it's connection packet
                flags = QuicHeaderFlags(ack=1, syn=1, data=0, fin=0)
                header = QuicHeader(flags=flags, packet_number=1, connection_id=1)
                frames = [QuicFrame(1, 0, 2, "Hi")]
                send_packet = QuicPacket(header, frames)
                self.__sock.sendto(send_packet.serialize(), client_addr)
                print("Sent syn ack packet\n")
                return True
        print("Was not able to receive syn request. Try again \n")
        return False

    def listen(self):
        if not self.wait_for_connection():
            return
        while True:
            packet, client_addr = self.receive()
            if packet.header.flags.fin == DISCONNECT_MSG:
                break
            for frame in packet.payload:
                if frame.stream_id >= len(self.files):
                    self.files.extend([""] * (frame.stream_id - len(self.files) + 1))
                self.files[frame.stream_id] += frame.data
            self.send_data_ack(client_addr)
        self.__sock.close()
        for file in self.files:
            print(len(file))

    def send_data_ack(self, client_addr):
        flags = QuicHeaderFlags(ack=1, syn=0, data=0, fin=0)
        header = QuicHeader(flags=flags, packet_number=1, connection_id=1)
        frames = [QuicFrame(1, 0, 2, "Hi")]
        send_packet = QuicPacket(header, frames)
        self.__sock.sendto(send_packet.serialize(), client_addr)

    # def listen(self):
    #     print(f"Listening on {self.addr[0]}:{self.addr[1]}")
    #     if self.wait_for_connection == False:
    #         print("Cannot open communication with the client. try again.")
    #         return
    #     while True:
    #         packet, client_addr = self.receive()
    #
    #         print(f"Received data for packet {packet.header.packet_number}: of size ")
    #         print(packet)
    #         # If received a disconnect message, close.
    #         if packet.header.flags.fin == DISCONNECT_MSG:
    #             print(f"Received close packet!")
    #             break
    #         # for each frame received, add
    #         for frame in packet.payload:
    #             if frame.stream_id >= len(self.files):
    #                 # Extend the list to have enough elements
    #                 self.files.extend([""] * (frame.stream_id - len(self.files) + 1))
    #             self.files[frame.stream_id] += frame.data
    #             print(f"Received {client_addr} {frame.data}")
    #
    #     # when it stops.
    #     print("Closing socket! Program finished.")
    #     self.__sock.close()

    # Haven't implemented it yet

receiver = Receiver('127.0.0.1', 1111)
receiver.listen()