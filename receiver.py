# This file shows an implemention of a receivere that 
# handles multiple streams concept.

# Written by Tomer Shor at the 10th of May 2024.
# NOTE: This file contian


import socket
from quic import *
import logging
import time
import socket
# CONSTS
FORMAT = 'utf-8'
BUFFER_SIZE = (1024+1000) * 3
DISCONNECT_MSG = 1
SERVER_PORT = 5558
MAX_WAIT_TIME = 5


# Class representing receiver.
# @param host - server's IP.
# @param port - server's port.
class Receiver:
    def __init__(self, host, port):
        self.__addr = (host, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind(self.__addr)
        self.files = []
        print(f"Listening on IP:{self.__addr[0]}  Port: {self.__addr[1]}")


    # Haven't implemented it yet
    def send(self, packet: QuicPacket, client_ip):
        logging.info(f"Sending {packet.data} to {client_ip}")
        self.__sock.sendto(packet.serialize().encode(FORMAT), client_ip)

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
        if not self.wait_for_connection():
            print("Cannot open communication with the client. try again.")
            return
        
        # Statistic variables:
        start_time = 0
        end_time = 0
        numebr_of_runs = 0                  #   counts the number of sendings.
        number_of_bytes_in_each_frame = 0   #   counts the number of bytes in each frame 
        number_of_frames_per_send = 0       #   counts the number of frames in each stream
        data_rate = []                      #   stores the data rate in BYTES/SEC for each run




        start_time = time.time()
        while True:
            packet, client_addr = self.receive()
            time_of_each_packet = time.time()                # start timer for each packet
            if packet.header.flags.fin == DISCONNECT_MSG:
                end_time = time.time()
                print(f"Received close packet!")
                break
            if packet.header.packet_number == 5:
                number_of_bytes_in_each_frame = packet.payload[0].length # assuming the 5th packet will contain full fraims.
                number_of_frames_per_send = len(packet.payload)
            for frame in packet.payload:   
                if frame.stream_id >= len(self.files):        # Extend the list to have enough elements
                    self.files.extend([""] * (frame.stream_id - len(self.files) + 1))

                self.files[frame.stream_id] += frame.data
            time_of_each_packet_end = time.time()
            numebr_of_runs += 1
            data_rate.append(number_of_frames_per_send * number_of_bytes_in_each_frame / (time_of_each_packet_end - time_of_each_packet))
            self.send_data_ack(client_addr)
        print("Closing socket!\nProgram finished.")
        self.__sock.close()

        # calculate statistics
        total_time = end_time - start_time
        num_of_bytes = number_of_bytes_in_each_frame * number_of_frames_per_send * numebr_of_runs
        avararge_byte_rate = num_of_bytes / total_time
        avararge_byte_rate = round(avararge_byte_rate, 2)
        avarage_packets = (numebr_of_runs / total_time)
        avarage_packets = round(avarage_packets, 2)


        print(f"\n\n -----------------STATISTICS-----------------\n")
        print(f"STREAM SIZE: {number_of_frames_per_send} FRAMES, {number_of_bytes_in_each_frame} BYTES EACH.\n")
        print(f"TOTAL BYTES RECEIVED: {num_of_bytes}")
        print(f"TOTAL PACKETS RECEIVED: {numebr_of_runs}")
        print(f"AVARAGE BYTE RATE IS: {avararge_byte_rate} BYTES/SEC.")
        print(f"AVARAGE NUMBER OF PACKETS PER SECOND IS {avarage_packets} Packets/SEC.\n\n")
        print("---------------------------------------------\n\n")

        statistics = {
            "stream_size": round(number_of_frames_per_send / 0.6),
            "Bytes in stream": number_of_bytes_in_each_frame,
            "total_bytes_received": num_of_bytes,
            "total_packets_received": numebr_of_runs,
            "average_byte_rate": avararge_byte_rate,
            "average_packets_per_second": avarage_packets
        }

        return statistics
        

    # A degenerated function to send ack. The function will send ack no matter what has been received,
    # since we have been told to assume each packet will completly arrive.
    def send_data_ack(self, client_addr):
        flags = QuicHeaderFlags(ack=1, syn=0, data=0, fin=0)
        header = QuicHeader(flags=flags, packet_number=1, connection_id=1)
        frames = [QuicFrame(1, 0, 2, "Hi")]
        send_packet = QuicPacket(header, frames)
        self.__sock.sendto(send_packet.serialize(), client_addr)



# receiver = Receiver('127.0.0.1', 1111)
# receiver.listen()