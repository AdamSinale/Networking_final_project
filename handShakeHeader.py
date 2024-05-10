from quic import *

# Class representing handshake packet.
# @param flags - packet's flags.
# @param number_of_files - number of files to be sent.
# @param number_of_frames - number of frames in the file.
# @param number_of_streams - number of streams to be sent.
# @param size_of_file - size of the file to be sent.
class handShakeQuicHeader:
    def __init__(self,flags,number_of_files,number_of_frames,number_of_streams,size_of_file):
        self.flags = flags
        self.number_of_files = number_of_files
        self.number_of_frames = number_of_frames
        self.number_of_streams = number_of_streams
        self.size_of_file = size_of_file

