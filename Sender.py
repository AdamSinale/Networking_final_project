from quic2 import *
import Quic

def main():
    client = Sender("127.0.0.1", SERVER_PORT)
    flags = QuicHeaderFlags(ack=0,syn=1,data=0,fin=0)
    header = QuicHeader(flags=flags, packet_number=1234, connection_id=1)
    frames = [QuicFrame(1,0, 5, b"Hello"), QuicFrame(1,0, 4, b"Sup?")]

    quic_packet = QuicPacket(header, frames)
    client.send(quic_packet)

        
        

if __name__ == "__main__":
    main()
    print("Done")


