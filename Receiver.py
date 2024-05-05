from quic2 import *
import socket


def main():
    server = Receiver("127.0.0.1", SERVER_PORT)
    server.listen()



if __name__ == "__main__":
    main()
    print("Done")
