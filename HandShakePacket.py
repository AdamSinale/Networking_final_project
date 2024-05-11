import struct
from Quic import QuicHeaderFlags


class HandShakePacket:
    def __init__(self, number_of_files, number_of_stream, number_of_frames, size_of_frame) -> None:
        self.flags = QuicHeaderFlags(0, 1, 0, 0)
        self.number_of_files = number_of_files
        self.number_of_stream = number_of_stream
        self.number_of_frames = number_of_frames
        self.size_of_frame = size_of_frame


    def serialize(self):
        # Serialize the fields into bytes
        flags_byte = bytes([self.flags.serialize()])
        number_of_files_bytes = self.number_of_files.to_bytes(4, 'big')
        number_of_stream_bytes = self.number_of_stream.to_bytes(4, 'big')
        number_of_frames_bytes = self.number_of_frames.to_bytes(4, 'big')
        size_of_frame_bytes = self.size_of_frame.to_bytes(4, 'big')

        # Concatenate all bytes
        return flags_byte + number_of_files_bytes + number_of_stream_bytes + number_of_frames_bytes + size_of_frame_bytes

    @classmethod
    def deserialize(cls, data):
        # Deserialize the bytes into the fields
        flags = QuicHeaderFlags.deserialize(data[0])
        number_of_files = int.from_bytes(data[1:5], 'big')
        number_of_stream = int.from_bytes(data[5:9], 'big')
        number_of_frames = int.from_bytes(data[9:13], 'big')
        size_of_frame = int.from_bytes(data[13:17], 'big')

        return cls(number_of_files, number_of_stream, number_of_frames, size_of_frame)
    

    


