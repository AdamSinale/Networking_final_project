import threading
import time
from quic2 import *

def send_messages(ip, port, num_streams):
    client = Sender(ip, port)
    for i in range(num_streams):
        for j in range(5):  # Send 5 packets for each stream
            packet_number = i * 5 + j  # Calculate the packet number for this packet
            flags = Flags(0, 0, 0, 1)  # Assuming only the data flag is set
            quic_packet = Quic(f"Stream {i+1} Packet {j+1}", len(f"Stream {i+1} Packet {j+1}"), flags, packet_number)
            client.send(quic_packet.serialize())
            # time.sleep(1)  # Delay between packets
    client.send(Quic("DISCONNECT", len("DISCONNECT"), Flags(0, 0, 1, 0), 0).serialize())  # Send a closing request for all streams

def main():
    # Replace '127.0.0.1' and 5555 with your server's IP and port
    send_messages('127.0.0.1', SERVER_PORT, 3)  # Sending packets for 3 streams

if __name__ == "__main__":
    main()
