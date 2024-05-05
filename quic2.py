from quic import *
import threading
import logging
import socket
import time
FORMAT = 'utf-8'
BUFFER_SIZE = 1024
DISCONNECT_MSG = 1
SERVER_PORT = 5558
SERVER_ADDR = ("127.0.0.1", SERVER_PORT)



class Sender:
    def __init__(self, ip, port):
        logging.info('Initializing Broker')
        self.addr = (ip, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Haven't implemented it yet
    def handshake(self):
        flg = Flags(0, 1, 0, 0)
        pack = Quic('hello', 5, flg, 0)
        self.__sock.sendto(b'hello', self.addr)
        self.__sock.recvfrom(1024)
        self.send("ack")

    # Haven't implemented it yet
    def receive_ack(self):
        data, addr = self.__sock.recvfrom(1024)
        print(data.decode())

    # Haven't implemented it fully yet
    def send(self, packet):
        self.__sock.sendto(packet.encode(FORMAT), SERVER_ADDR)

    # Haven't implemented it fully yet
    def receive(self):
        return self.__sock.recvfrom(1024)


class Receiver:
    def __init__(self, host, port):
        self.__addr = (host, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Socket created")
        self.__sock.bind(self.__addr)
        self.running = True
        self.streams = []

    # Haven't implemented it yet
    def handshake(self):
        msg, addr = self.__sock.recvfrom(BUFFER_SIZE)
        self.__sock.sendto(b'ack', (self.__addr[0]))
        self.udp_receive()

    # Haven't implemented it yet
    def send(self, packet: Quic, client_ip):
        logging.info(f"Sending {packet.data} to {client_ip}")
        self.__sock.sendto(packet.serialize().encode(FORMAT), client_ip)

    # Haven't implemented it yet
    def receive(self):
        packet , clinet_addr = self.__sock.recvfrom(BUFFER_SIZE)
        packet = packet.decode(FORMAT).deserialize()
        return packet
        
    # Listens for packets and opens new thread when packet arrives
    def listen(self):
        print(f"Listening on {self.__addr[0]}:{self.__addr[1]}")
        while self.running:
            packet, client_addr = self.__sock.recvfrom(BUFFER_SIZE)  # accept communication
            packet = packet.decode(FORMAT)
            # open a new thread to handle the stream using handle stream fucntion
            # send to the function args : packet and clients's address.
            thread = threading.Thread(target=self.handle_stream, args=(packet, client_addr))
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            thread.start()

        # when it stops.
        print("Closing socket! Program finished.")
        self.__sock.close()

    def handle_stream(self, packet, addr):
        
        # reconstract the packet.
        print(f"[NEW CONNECTION] {addr} connected")
        packet_parts = packet.split(":")
        packet_number = int(packet_parts[0])
        ack = int(packet_parts[1])
        syn = int(packet_parts[2])
        fin = int(packet_parts[3])
        data_size = int(packet_parts[5])
        data = ":".join(packet_parts[6:])  # Reconstruct the data part

        flags = Flags(ack, syn, fin, 1)  # Assuming 1 for data flag
        recv_packet = Quic(data, data_size, flags, packet_number)
        
        print(f"Received data for packet {packet_number}: {data}")
        # If received a disconnect message, close.
        if recv_packet.flags.fin == DISCONNECT_MSG:
            print(f"Received close packet!")
            self.running = False
            print(self.running)
            return
        if recv_packet.packet_number >= len(self.streams):
            # Extend the list to have enough elements
            self.streams.extend([""] * (recv_packet.packet_number - len(self.streams) + 1))

        self.streams[recv_packet.packet_number] += recv_packet.data       
        print(f"Received {addr} {recv_packet.data}")
        reply_msg = f"MSG received: {recv_packet.data}"

        self.__sock.sendto(reply_msg.encode('utf-8'), addr)
        time.sleep(1) 

        #self.streams.remove(recv_packet.packet_number)
        # print("Closing the socket")
        # self.running = False

    # Haven't implemented it yet
    def udp_receive(self):
        data, addr = self.__sock.recvfrom(1024)
        print(data.decode(FORMAT))
        self.send_ack()

    # Haven't implemented it yet
    def send_ack(self):
        self.__sock.sendto(b'ack', (self.__ip, self.__port))
