# This file represents QUIC packet class.
# More information about QUIC can be found in the following link: https://web.cs.ucla.edu/~lixia/papers/UnderstandQUIC.pdf

# Written by Adam Sin at the 10th of May 2024.

FORMAT = 'utf-8'
stream_id_size = 2

# This function return the length of a packet depends on whether it contains data or not.
def length_by_data(data):
    return 2 if data==0 else 20

# Class representing a QUIC packet.
# @param header - The packet's header as implemented in QuicHeader class.
# @param frames - The packet's frames (payload) as implemented in QuicFrame class.
class QuicPacket:
    def __init__(self, header, frames):
        self.header = header
        self.payload = frames

    # Function that serializes the packet.
    # Returns the packet as a set of bytes.
    def serialize(self):
        packet_bytes = self.header.serialize()
        for frame in self.payload:
            packet_bytes += frame.serialize(self.header.flags.data)
        return packet_bytes

    # Function to deserialize a packet.
    # The function receives a set of bytes which represent a serialized packet and deserialize it back to a packet object.
    # NOTE: We assume that the function receives serialized packet data, WE DONT CHECK WHETHER IT ACTUALLY IS!
    # @param serialized_data - The data received.
    @classmethod
    def deserialize(cls, serialized_data):
        header_length = 9  # Assuming header length is fixed
        header = QuicHeader.deserialize(serialized_data[:header_length])
        payload_data = serialized_data[header_length:]
        length_size = length_by_data(header.flags.data)
        frames = []
        while payload_data:
            frame_length = int.from_bytes(payload_data[stream_id_size + length_size : stream_id_size + 2*length_size], byteorder='big')
            frame_data = payload_data[ : 2*length_size + frame_length + stream_id_size]
            frames.append(QuicFrame.deserialize(frame_data, header.flags.data))
            payload_data = payload_data[2*length_size + frame_length + stream_id_size : ]
        return cls(header, frames)

# Class representing QUIC packet header as described in the article.
# @param flags - header flags as implemented in QuicHeaderFlags class.
# @param packet_number - packet's sequence number.
# @param connection_id - Indicates client's connection ID. NOTE: in our project we set connection_id as 1, since we did not implement multiple clients connections.
class QuicHeader:
    def __init__(self, flags, packet_number, connection_id):
        self.flags = flags
        self.packet_number = packet_number
        self.connection_id = connection_id

    # The two following functions behave similar to the parallel functions in QuicPacket class.
    def serialize(self):
        flags_byte = self.flags.serialize()  # Serialize flags
        packet_number_bytes = self.packet_number.to_bytes(4, byteorder='big')  # Assuming packet number is a 32-bit integer
        connection_id_bytes = self.connection_id.to_bytes(4, byteorder='big')  # Assuming connection ID is a 32-bit integer
        return flags_byte + packet_number_bytes + connection_id_bytes

    @classmethod
    def deserialize(cls, serialized_data):
        flags = QuicHeaderFlags.deserialize(serialized_data[:1])  # Deserialize flags
        packet_number = int.from_bytes(serialized_data[1:5], byteorder='big')  # Deserialize packet number
        connection_id = int.from_bytes(serialized_data[5:9], byteorder='big')  # Deserialize connection ID
        return cls(flags, packet_number, connection_id)

# Class representing QUIC packet's header flags.
# The flags indicate the type of the packet.
# @param ack - 1 if the packet is a connection request packet, else 0.
# @param syn - 1 if the packet is a syn packet, else 0.
# @param fin - 1 if the packet is closing request packet, else 0.
# @param data - 1 if the packet contains data, else 0.
class QuicHeaderFlags:
    def __init__(self, ack, syn, data, fin):
        self.ack = ack    # first frame of the stream
        self.syn = syn    # first frame of the stream
        self.data = data  # second to second-to-last of the stream
        self.fin = fin    # last frame of the stream

    # The two following functions behave similar to the parallel functions in QuicPacket class.
    def serialize(self):
        flags_byte = (self.ack << 3) | (self.syn << 2) | (self.fin << 1) | self.data
        return flags_byte.to_bytes(1, byteorder='big')  # Convert to byte string

    @classmethod
    def deserialize(cls, serialized_data):
        flags_byte = int.from_bytes(serialized_data, byteorder='big')  # Deserialize flags byte
        ack = (flags_byte & 0b1000) >> 3  # Extract ack bit
        syn = (flags_byte & 0b0100) >> 2  # Extract syn bit
        fin = (flags_byte & 0b0010) >> 1  # Extract fin bit
        data = flags_byte & 0b0001         # Extract data bit
        return cls(ack, syn, data, fin)

# Class representing QUIC frame.
# Each frame belongs to one file. It contains chuck of data from the file.
# @param stream_id - A unique number that describes which file the information was taken from.
# @param offest - The offset from the start of the file.
# @param length - The length of the data.
# @param data - The data of the frame.
class QuicFrame:
    def __init__(self, stream_id, offset, length, data):
        self.stream_id = stream_id
        self.offset = offset
        self.length = length
        self.data = data

    # The two following functions behave similar to the parallel functions in QuicPacket class.
    def serialize(self, data):
        stream_id_bytes = self.stream_id.to_bytes(stream_id_size, byteorder='big')  # Assuming stream_id is a 16-bit integer
        offset_bytes = self.offset.to_bytes(length_by_data(data), byteorder='big')
        length_bytes = self.length.to_bytes(length_by_data(data), byteorder='big')
        return stream_id_bytes + offset_bytes + length_bytes + self.data.encode(FORMAT)

    @classmethod
    def deserialize(cls, serialized_data, data):
        stream_id = int.from_bytes(serialized_data[:stream_id_size], byteorder='big')  # Deserialize stream_id
        offset = int.from_bytes(serialized_data[stream_id_size:length_by_data(data) + stream_id_size], byteorder='big') # Deserialize length
        length = int.from_bytes(serialized_data[length_by_data(data) + stream_id_size : 2*length_by_data(data) + stream_id_size], byteorder='big') # Deserialize length
        data = serialized_data[2*length_by_data(data) + stream_id_size:]  # Extract data
        return cls(stream_id, offset, length, data.decode(FORMAT))

# flags = QuicHeaderFlags(ack=0,syn=0,data=1,fin=0)
# header = QuicHeader(flags=flags, packet_number=1234, connection_id=1)
# frames = [QuicFrame(1, 100, 1000, "Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!"),
#           QuicFrame(2, 100, 1000, "Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!")]
# # frames = [QuicFrame(1, 0, 5, "Hello")]
# packet = QuicPacket(header, frames)
#
# s_packet = packet.serialize()
# f_packet = QuicPacket.deserialize(s_packet)
#
# print("O Packet:", packet.__dict__)
# print("S Packet:", s_packet)
# print("D Packet:", f_packet.__dict__)
# print()
# print("O Header:", packet.header.__dict__)
# print("S Header:", packet.header.serialize())
# print("D Header:", f_packet.header.__dict__)
# print()
# print("O Flags:", packet.header.flags.__dict__)
# print("S Flags:", packet.header.flags.serialize())
# print("D Flags:", f_packet.header.flags.__dict__)
# print()
# print("O Frame:", packet.payload[0].__dict__)
# print("S Frame:", packet.payload[0].serialize(0))
# print("D Frame:", f_packet.payload[0].__dict__)
# print()
# print("O Frame:", packet.payload[1].__dict__)
# print("S Frame:", packet.payload[1].serialize(0))
# print("D Frame:", f_packet.payload[1].__dict__)
# print()