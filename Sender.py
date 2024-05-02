import socket
from Send_Flags import Send_Flags

# needs to import Quic and Flags from quic.py
from quic import Quic, Flags

class Sender(Send_Flags):
    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handshake(self):
        self.send_syn(self.__sock, self.__ip, self.__port)
        data, addr = self.__sock.recvfrom(1024)
        if data != 'syn_ack':
            print('Invalid Data')
            return
        self.send_ack(self.__sock, self.__ip, self.__port)

    def udp_send(self, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (self.__ip, self.__port))
        sock.close()
        # self.receive_ack()
