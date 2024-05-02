from abc import ABC

# needs to import Quic and Flags from quic.py
from quic import Quic, Flags

class Send_Flags(ABC):
    def send_ack(self, sock, ip, port):
        flg = Flags(1, 0, 0, 0)
        pack = Quic('hello', 5, flg, 0)
        sock.sendto(b'ack', (ip, port))

    def send_syn(self, sock, ip, port):
        flg = Flags(0, 1, 0, 0)
        pack = Quic('hello', 5, flg, 0)
        sock.sendto(b'syn', (ip, port))

    def send_syn_ack(self, sock, ip, port):
        flg = Flags(1, 1, 0, 0)
        pack = Quic('hello', 5, flg, 0)
        sock.sendto(b'syn_ack', (ip, port))

    def send_fin(self, sock, ip, port):
        flg = Flags(0, 0, 1, 0)
        pack = Quic('hello', 5, flg, 0)
        sock.sendto(b'fin', (ip, port))

    def send_fin_ack(self, sock, ip, port):
        flg = Flags(1, 0, 1, 0)
        pack = Quic('hello', 5, flg, 0)
        sock.sendto(b'fin_ack', (ip, port))

    def send_data(self, sock, ip, port):
        flg = Flags(0, 0, 0, 1)
        pack = Quic('hello', 5, flg, 0)
        sock.sendto(b'data', (ip, port))