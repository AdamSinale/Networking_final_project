from quic2 import *
import socket


def main():
    server = Receiver("127.0.0.1", 5555)
    server.listen_clients()
    return 0


if __name__ == "__main__":
    main()
