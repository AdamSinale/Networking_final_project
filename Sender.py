from quic2 import *

def main():
    client = Sender("127.0.0.1", SERVER_PORT)

    for i in range(10):
        send_message = "Trying to send message"
        pack = Quic(send_message, len(send_message), Flags(0, 0, 0, 1), i)
        client.send(pack.serialize())
        client.receive_ack()
    close_packet = Quic("Closing", len("Closing"), Flags(0, 0, 1, 0), 11)
    client.send(close_packet.serialize())

if __name__ == "__main__":
    main()
    print("Done")


