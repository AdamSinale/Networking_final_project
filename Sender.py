from quic2 import *


def main():
    client = Sender("127.0.0.1", SERVER_PORT)

    for i in range(10):
        send_message = "Trying to send message"
        client.send(send_message)
        client.receive()


if __name__ == "__main__":
    main()
    print("Done")

