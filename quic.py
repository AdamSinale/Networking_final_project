
def length_by_syn(syn):
    return 2 if syn==1 else 20
stream_id_size = 2

class QuicPacket:
    def __init__(self, header, frames):
        self.header = header
        self.payload = frames
    def serialize(self):
        packet_bytes = self.header.serialize()
        for frame in self.payload:
            packet_bytes += frame.serialize(self.header.flags.syn)
        return packet_bytes
    @classmethod
    def deserialize(cls, serialized_data):
        header_length = 9  # Assuming header length is fixed
        header = QuicHeader.deserialize(serialized_data[:header_length])
        payload_data = serialized_data[header_length:]
        length_size = length_by_syn(header.flags.syn)
        frames = []
        while payload_data:
            frame_length = int.from_bytes(payload_data[stream_id_size + length_size : stream_id_size + 2*length_size], byteorder='big')
            frame_data = payload_data[ : 2*length_size + frame_length + stream_id_size]
            frames.append(QuicFrame.deserialize(frame_data, header.flags.syn))
            payload_data = payload_data[2*length_size + frame_length + stream_id_size : ]
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
    def __init__(self, stream_id, offset, length, data):
        self.stream_id = stream_id
        self.offset = offset
        self.length = length
        self.data = data
    def serialize(self, syn):
        stream_id_bytes = self.stream_id.to_bytes(stream_id_size, byteorder='big')  # Assuming stream_id is a 16-bit integer
        offset_bytes = self.offset.to_bytes(length_by_syn(syn), byteorder='big')
        length_bytes = self.length.to_bytes(length_by_syn(syn), byteorder='big')
        return stream_id_bytes + offset_bytes + length_bytes + self.data.encode('utf-8')
    @classmethod
    def deserialize(cls, serialized_data, syn):
        stream_id = int.from_bytes(serialized_data[:stream_id_size], byteorder='big')  # Deserialize stream_id
        offset = int.from_bytes(serialized_data[stream_id_size:length_by_syn(syn) + stream_id_size], byteorder='big') # Deserialize length
        length = int.from_bytes(serialized_data[length_by_syn(syn) + stream_id_size : 2*length_by_syn(syn) + stream_id_size], byteorder='big') # Deserialize length
        data = serialized_data[2*length_by_syn(syn) + stream_id_size:]  # Extract data
        return cls(stream_id, offset, length, data.decode('utf-8'))

flags = QuicHeaderFlags(ack=0,syn=0,data=1,fin=0)
header = QuicHeader(flags=flags, packet_number=1234, connection_id=1)
frames = [QuicFrame(1, 100, 1000, "Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!"),
          QuicFrame(2, 100, 1000, "Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!Sup?!")]
# frames = [QuicFrame(1, 0, 5, "Hello")]
packet = QuicPacket(header, frames)

s_packet = packet.serialize()
f_packet = QuicPacket.deserialize(s_packet)

print("O Packet:", packet.__dict__)
print("S Packet:", s_packet)
print("D Packet:", f_packet.__dict__)
print()
print("O Header:", packet.header.__dict__)
print("S Header:", packet.header.serialize())
print("D Header:", f_packet.header.__dict__)
print()
print("O Flags:", packet.header.flags.__dict__)
print("S Flags:", packet.header.flags.serialize())
print("D Flags:", f_packet.header.flags.__dict__)
print()
print("O Frame:", packet.payload[0].__dict__)
print("S Frame:", packet.payload[0].serialize(0))
print("D Frame:", f_packet.payload[0].__dict__)
print()
print("O Frame:", packet.payload[1].__dict__)
print("S Frame:", packet.payload[1].serialize(0))
print("D Frame:", f_packet.payload[1].__dict__)
print()