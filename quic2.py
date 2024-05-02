from quic import *
import threading
import logging
import socket
BUFFER_SIZE = 1024
DISCONNECT_MSG = "DISCONNECT"
FORMAT = 'utf-8'
SERVER_PORT = 5556
SERVER_ADDR = ("127.0.0.1", SERVER_PORT)



class Sender:
    def __init__(self, ip, port):
        logging.info('Initializing Broker')
        self.addr = (ip, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handshake(self):
        flg = Flags(0, 1, 0, 0)
        pack = Quic('hello', 5, flg, 0)
        self.__sock.sendto(b'hello', self.addr)
        self.__sock.recvfrom(1024)
        self.send("ack")

    def receive_ack(self):
        data, addr = self.__sock.recvfrom(1024)
        print(data.decode())

    def send(self, packet):
        self.__sock.sendto(packet.encode(FORMAT), SERVER_ADDR)

    def receive(self):
        return self.__sock.recvfrom(1024)


class Receiver:
    def __init__(self, host, port):
        self.__addr = (host, port)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        print("Socket created")
        self.__sock.bind(self.__addr)
        print("Socket bind complete")
        self.client_list = []

    def handshake(self):
        msg, addr = self.__sock.recvfrom(BUFFER_SIZE)
        self.__sock.sendto(b'ack', (self.__addr[0]))
        self.udp_receive()

    def send(self, message, client_ip):
        logging.info(f"Sending {message} to {client_ip}")
        self.__sock.sendto(message, client_ip)

    def listen_clients(self):
        print(f"Listening on {self.__addr[0]}:{self.__addr[1]}")
        while True:
            packet, client_addr = self.__sock.recvfrom(BUFFER_SIZE)  # accept communication
            self.client_list.append(client_addr)
            thread = threading.Thread(target=self.handle_client, args=(packet, client_addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, packet, addr):
        print(f"[NEW CONNECTION] {addr} connected")
        # If received a disconnect message, close.
        if packet == DISCONNECT_MSG:
            connected = False
        # logging.info(f"[NEW CONNECTION]") - optional
        connected = True
        while connected:
            recv_packet = self.__sock.recvfrom(BUFFER_SIZE)
            if recv_packet == DISCONNECT_MSG:
                connected = False
            print(f"Received {addr} {recv_packet}")
            reply_msg = f"MSG received: {recv_packet}"

            self.__sock.sendto(reply_msg.encode('utf-8'), addr)

        self.client_list.remove(addr)
        self.__sock.close()

    def udp_receive(self):
        self.__sock.bind((self.__ip, self.__port))
        data, addr = self.__sock.recvfrom(1024)
        print(data.decode())
        self.send_ack()

    def send_ack(self):
        self.__sock.sendto(b'ack', (self.__ip, self.__port))
