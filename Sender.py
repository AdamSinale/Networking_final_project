import socket

# needs to import Quic and Flags from quic.py
from quic import Quic, Flags

class Sender:
    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handshake(self):
        flg = Flags(0, 1, 0, 0)
        pack = Quic('hello', 5, flg, 0)
        self.__sock.sendto(b'hello', (self.__ip, self.__port))
        self.__sock.recvfrom(1024)
        self.udp_send(b'ack')

    def udp_send(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (self.__ip, self.__port))
        sock.close()
        self.receive_ack()

    def receive_ack(self):
        data, addr = self.__sock.recvfrom(1024)
        print(data.decode())
