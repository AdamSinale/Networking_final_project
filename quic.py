import struct

class QuicPacket:
    def __init__(self, header, frames):
        self.header = header
        self.payload = frames
    def serialize(self):
        packet_bytes = self.header.serialize()
        for frame in self.payload:
            packet_bytes += frame.serialize()
        return packet_bytes
    @classmethod
    def deserialize(cls, serialized_data):
        header_length = 9  # Assuming header length is fixed
        header_data = serialized_data[:header_length]
        header = QuicHeader.deserialize(header_data)
        payload_data = serialized_data[header_length:]
        frames = []
        while payload_data:
            frame_length = int.from_bytes(payload_data[:2], byteorder='big')
            frame_data = payload_data[2:2 + frame_length]
            frames.append(QuicFrame.deserialize(frame_data))
            payload_data = payload_data[2 + frame_length:]
        return cls(header, frames)
class QuicHeader:
    def __init__(self, flags, packet_number, connection_id):
        self.flags = flags
        self.packet_number = packet_number
        self.connection_id = connection_id
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

class QuicHeaderFlags:
    def __init__(self, ack, syn, data, fin):
        self.ack = ack    # first frame of the stream
        self.syn = syn    # first frame of the stream
        self.data = data  # second to second-to-last of the stream
        self.fin = fin    # last frame of the stream
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

class QuicFrame:
    def __init__(self, stream_id, length, data):
        self.stream_id = stream_id
        self.length = length
        self.data = data
    def serialize(self):
        stream_id_bytes = self.stream_id.to_bytes(4, byteorder='big')  # Assuming stream_id is a 32-bit integer
        length_bytes = self.length.to_bytes(2, byteorder='big')  # Assuming length is a 16-bit integer
        return stream_id_bytes + length_bytes + self.data
    @classmethod
    def deserialize(cls, serialized_data):
        stream_id = int.from_bytes(serialized_data[:4], byteorder='big')  # Deserialize stream_id
        length = int.from_bytes(serialized_data[4:6], byteorder='big')  # Deserialize length
        data = serialized_data[6:]  # Extract data
        return cls(stream_id, length, data)

flags = QuicHeaderFlags(ack=0,syn=1,data=0,fin=0)
header = QuicHeader(flags=flags, packet_number=1234, connection_id=1)
frames = [QuicFrame(1, 5, b"Hello"), QuicFrame(1, 4, b"Sup?")]


s_flags = flags.serialize()
d_flags = QuicHeaderFlags.deserialize(s_flags)
s_header = header.serialize()
d_header = QuicHeader.deserialize(s_header)
s_frame1 = frames[0].serialize()
d_frame1 = QuicFrame.deserialize(s_frame1)
s_frame2 = frames[1].serialize()
d_frame2 = QuicFrame.deserialize(s_frame2)
f_packet = QuicPacket(header, frames)
s_packet = f_packet.serialize()
f_packet = QuicPacket.deserialize(s_packet)
print("O Flags:", flags.__dict__)
print("S Flags:", s_flags)
print("D Flags:", d_flags.__dict__)
print()
print("O Header:", header.__dict__)
print("S Header:", s_header)
print("D Header:", d_header.__dict__)
print()
print("O Frame:", frames[0].__dict__)
print("S Frame:", s_frame1)
print("D Frame:", d_frame1.__dict__)
print()
print("O Frame:", frames[1].__dict__)
print("S Frame:", s_frame2)
print("D Frame:", d_frame2.__dict__)
print()
print("O Header:", f_packet.__dict__)
print("S Header:", s_packet)
print("D Header:", f_packet.__dict__)