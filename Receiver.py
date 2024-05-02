import socket


class Receiver:
    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handshake(self):
        self.__sock.recvfrom(1024)
        self.__sock.sendto(b'ack', (self.__ip, self.__port))
        self.udp_receive()

    def udp_receive(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.__ip, self.__port))
        data, addr = sock.recvfrom(1024)
        print(data.decode())
        self.send_ack()

    def send_ack(self):
        self.__sock.sendto(b'ack', (self.__ip, self.__port))