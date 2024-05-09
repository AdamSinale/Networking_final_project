# This file describes QUIC Packet structure.
# Author - Tomer Shor

from socket import *




# Class representing QUIC packet's flags
# @param ack - 1 if the packet is a connection request packet, else 0.
# @param syn - 1 if the packet is a syn packet, else 0.
# @param fin - 1 if the packet is closing request packet, else 0.
# @param data - 1 if the packet contains data, else 0.

class Flags:
    def __init__(self, ack, syn, fin, data):
        self.ack = ack    # first frame of the stream
        self.syn = syn    # first frame of the stream
        self.data = data  # second to second-to-last of the stream
        self.fin = fin    # last frame of the stream

# Class representing Protect Payload as described in the article.
# @param frames - A list of frames to be sent with the packet.
class ProtectedPayload:
    def __init__(self, frames : list) -> None:
        self.frames = frames


# Class frame representing packet frame as describes in the article.
# @param -
class Frame:
    def __init__(self, StreamID, Offset, Length, StreamData) -> None:
        self.StreamID = StreamID
        self.Offset = Offset
        self.Length = Length
        self.StreamData = StreamData


# Class representing quic packet.
# @param data - the data sent.
# @param data_size - the size of the data in bytes.
# @param flags - packet's flags.
# @param packet_number - packet's unique sequence number.
# @param encryption_key - set to zero since no implementation required.
class Quic:
    def __init__(self, Destination : tuple, flags : Flags, packet_number : int, protectedPayload : ProtectedPayload):
        self.Destination = Destination
        self.flags = flags
        self.packet_number = packet_number
        self.ProtectedPayload = protectedPayload

    # method to serialize a packet
    def serialize(self):
        frames_str = ":".join([f"{frame.StreamID},{frame.Offset},{frame.Length},{frame.StreamData}" for frame in self.ProtectedPayload.frames])
        return f"{self.packet_number}:{self.flags.ack}:{self.flags.syn}:{self.flags.fin}:{self.flags.data}:{frames_str}"

    @staticmethod
    def deserialize(packet_data: str):
        parts = packet_data.split(":")
        packet_number = int(parts[0])
        ack = int(parts[1])
        syn = int(parts[2])
        fin = int(parts[3])
        data = int(parts[4])
        frames_data = parts[5].split(",")
        frames = [Frame(int(frame_data[0]), int(frame_data[1]), int(frame_data[2]), frame_data[3]) for frame_data in [frame.split(",") for frame in frames_data]]
        flags = Flags(ack, syn, fin, data)
        protectedPayload = ProtectedPayload(frames)
        return Quic(None, flags, packet_number, protectedPayload)








