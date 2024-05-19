import unittest
from receiver import *
from sender import *
import threading

host = '127.0.0.1'
port = 1111

class TestSenderReceiver(unittest.TestCase):
    def run_receiver(self, host, port):
        self.receiver = Receiver(host, port)
        self.receiver.listen()

    # Due to the fact that regular start will generate automatically
    # a number of data sets with the same length.
    # We will use this instead to check for different sizes of files.
    def run_sender(self, host, port, data):
        self.sender = Sender(host, port)
        self.sender.handshake()
        self.sender.udp_send(data)
        self.sender.finish_connection(packet_number)
        self.sender.sock.close()
        return data

    def global_test(self, data):
        receiver_thread = threading.Thread(target=self.run_receiver, args=(host, port))
        sender_thread = threading.Thread(target=self.run_sender, args=(host, port, data))

        receiver_thread.start()
        time.sleep(1)
        sender_thread.start()

        receiver_thread.join()
        sender_thread.join()
        received_data = self.receiver.files
        self.assertEqual(data, received_data)

    def test_send_receive_short_data(self):
        data = [(0,b'hello')]
        self.global_test(data)

    def test_send_receive_medium_data(self):
        data = [(0,b'a'*1024)]  # 1 KB of data
        self.global_test(data)

    def test_send_receive_long_data(self):
        data = [(0,b'a'*1024*1024)]  # 1 MB of data
        self.global_test(data)

    def test_send_receive_empty_data(self):
        data = [(0,b'')]
        self.global_test(data)

    def test_send_receive_non_bytes_data(self):
        with self.assertRaises(ValueError):
            self.global_test("string data")

if __name__ == '__main__':
    unittest.main()
