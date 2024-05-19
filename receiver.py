# This file shows an implementation of a receiver that
# handles multiple streams concept.

# Written by Tomer Shor at the 10th of May 2024.
# NOTE: This file contian

from quic import *
import time
import socket
# CONSTS
FORMAT = 'utf-8'
BUFFER_SIZE = (1024+1000) * 5
DISCONNECT_MSG = 1
MAX_WAIT_TIME = 5

def print_stats(bytes_received, packets_received, time_taken):
    for i in range(len(time_taken)):
        if time_taken[i] == 0:
            return 0, 0
    if len(time_taken) == 0:
        return 0,0
    print("------------------------------------------------------------------------------")
    avg_bytes_per_sec = bytes_received[0] / time_taken[0]
    print("The average num of bytes per second is " + str(avg_bytes_per_sec))
    avg_packets_per_sec = packets_received[0] / time_taken[0]
    print("The average num of packets per second is " + str(avg_packets_per_sec))
    for i in range(1,len(bytes_received)):
        print("------------------------------------------------------------------------------")
        print("The total num of bytes in stream number "+str(i)+" is " + str(bytes_received[i]))
        print("The total num of packets in stream number "+str(i)+" is " + str(packets_received[i]))
        avg_bytes_per_sec = bytes_received[i] / time_taken[i]
        print("The average num of bytes per second in stream number "+str(i)+" is " + str(avg_bytes_per_sec))
        avg_packets_per_sec = packets_received[i] / time_taken[i]
        print("The average num of packets per second in stream number "+str(i)+" is " + str(avg_packets_per_sec))
    return avg_bytes_per_sec, avg_packets_per_sec

class Receiver:
    def __init__(self, host, port):
        self.__addr = (host, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind(self.__addr)
        self.files = []
        print(f"Listening on IP:{self.__addr[0]}  Port: {self.__addr[1]}")

    # Function to receive a massege from the client.
    # Returns a serialized QUIC packet and client's address.
    def receive(self):
        packet, client_addr = self.__sock.recvfrom(BUFFER_SIZE)
        d_packet = QuicPacket.deserialize(packet)
        return d_packet, client_addr

    # Function that waits for a syn request from the client.
    # The function waits MAX_WAIT_TIME * 10 seconds to receive a syn request, if it did not receive one, the receiver will return false.
    # If received a syn request, returns True and will return syn ack packet back to the clienet.
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
                print("\n\nReceived syn request!\nConection established!\n")
                return True
        print("Was not able to receive syn request. Try again \n")
        return False

    # This function is the main function of the receiver.
    # The function listens for packets and handles them.
    # The function will receive packets until it will receive a closing packet (aka flasg.fin == 1)
    # The data of each frame will be added to the matching data container recognized by steamID.
    def listen(self):
        bytes_received = []
        packets_received = []
        time_taken = []
        if not self.wait_for_connection():
            return
        while True:
            packet, client_addr = self.receive()
            start_time = time.perf_counter()
            if packet.header.flags.fin == DISCONNECT_MSG:
                break
            for frame in packet.payload:
                if frame.stream_id >= len(self.files):
                    self.files.extend([""] * (frame.stream_id - len(self.files) + 1))
                    packets_received.extend([0] * (frame.stream_id - len(packets_received) + 1))
                    bytes_received.extend([0] * (frame.stream_id - len(bytes_received) + 1))
                    time_taken.extend([0] * (frame.stream_id - len(time_taken) + 1))
                self.files[frame.stream_id] += frame.data
            finish_time = time.perf_counter()
            for frame in packet.payload:
                bytes_received[frame.stream_id] += len(frame.data)
                packets_received[frame.stream_id] += 1
                time_taken[frame.stream_id] += finish_time - start_time
                bytes_received[0] += len(frame.data)
            time_taken[0] += finish_time - start_time
            packets_received[0] += 1
            self.send_data_ack(client_addr)
        self.__sock.close()
        return print_stats(bytes_received, packets_received, time_taken)

    # A degenerated function to send ack. The function will send ack no matter what has been received,
    # since we have been told to assume each packet will completely arrive.
    def send_data_ack(self, client_addr):
        flags = QuicHeaderFlags(ack=1, syn=0, data=0, fin=0)
        header = QuicHeader(flags=flags, packet_number=1, connection_id=1)
        frames = [QuicFrame(1, 0, 2, "Hi")]
        send_packet = QuicPacket(header, frames)
        self.__sock.sendto(send_packet.serialize(), client_addr)
