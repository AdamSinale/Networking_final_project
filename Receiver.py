import socket
from Send_Flags import Send_Flags

class Receiver(Send_Flags):
    def __init__(self, ip, port):
        self.__ip = ip
        self.__port = port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def handshake(self):
        data, addr = self.__sock.recvfrom(1024)
        if data != 'syn':
            print('Invalid Data')
            return
        self.send_syn_ack(self.__sock, self.__ip, self.__port)

    def udp_receive(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.__ip, self.__port))
        data, addr = sock.recvfrom(1024)
        print(data.decode())
        self.send_ack(self.__sock, self.__ip, self.__port)