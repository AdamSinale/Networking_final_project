import threading
from sender import Sender
from receiver import Receiver

def main():
    for cur_data_num in range(1,21):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX "+str(cur_data_num)+" XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        # Create receiver and sender objects
        receiver = Receiver('127.0.0.1', 1111)
        sender = Sender('127.0.0.1', 1111)

        # Start listening on receiver in a separate thread
        receiver_thread = threading.Thread(target=receiver.listen)
        receiver_thread.start()

        # Perform handshake and send data in the main thread
        data = sender.start(cur_data_num)

        # Wait for receiver thread to finish
        receiver_thread.join()

        for i in range(len(data)):
            print("----------------------------------------------------------------")
            print("Strings length: " + str(len(receiver.files[i])))
            if receiver.files[i] == data[i][1]:
                print("Strings are: same")
            else:
                print("Strings are: different")
                diff_i = -1
                for j in range(min(len(receiver.files[i]), len(data[i][1]))):
                    if receiver.files[i][j] != data[i][1][j]:
                        diff_i = j
                        break

                if diff_i != -1:
                    print("First difference: ", diff_i)
                    print("Sent Different: ", data[i][1][diff_i-15:])
                    print("Got Different : ", receiver.files[i][diff_i-15:])

if __name__ == "__main__":
    main()
