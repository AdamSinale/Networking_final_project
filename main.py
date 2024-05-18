# This main file runs the program num_of_runs time.
# The program will save each run's stats in a file called receiver_sender_stats.txt
# The program will run the receiver and sender in parallel.
# The program will eventually print the statistics of each run, and the average statistics of all runs.

# Written by: Tomer Shor at the 16\05\2024


import threading
import matplotlib.pyplot as plt
from receiver import *
from sender import *

# Shared dictionary to store statistics
avg_bytes_per_sec_by_streams = []
avg_packets_per_sec_by_streams = []

def run_receiver(host, port):
    receiver = Receiver(host, port)
    avg_bytes_per_sec, avg_packets_per_sec = receiver.listen()
    # Store the statistics arrays
    avg_bytes_per_sec_by_streams.append(avg_bytes_per_sec)
    avg_packets_per_sec_by_streams.append(avg_packets_per_sec)

# Function to run the sender
def run_sender(host, port, i):
    sender = Sender(host, port)
    sender.start(i)

# Function to run the receiver and sender in parallel
def run_receiver_and_sender(host, port, num_runs):
    for i in range(1, num_runs + 1):
        print(f"XXXXXXXXXXXXXXXXXXXXXX Run #{i} XXXXXXXXXXXXXXXXXXXXXX")
        receiver_thread = threading.Thread(target=run_receiver, args=(host, port))
        sender_thread = threading.Thread(target=run_sender, args=(host, port, i))

        receiver_thread.start()
        time.sleep(1)
        sender_thread.start()

        receiver_thread.join()
        sender_thread.join()

    # Create a graph
    plt.figure(figsize=(12, 6))
    plt.plot([i for i in range(1, num_runs+1)], avg_bytes_per_sec_by_streams, marker='o')
    plt.xlabel('Number of Streams')
    plt.ylabel('Average Byte Rate')
    plt.title('Average Byte Rate vs. Number of Streams')
    plt.savefig('avg_bytes_per_sec.png')
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot([i for i in range(1, num_runs+1)], avg_packets_per_sec_by_streams, marker='o')
    plt.xlabel('Number of Streams')
    plt.ylabel('Average Packets per Second')
    plt.title('Average Packets per Second vs. Number of Streams')
    plt.savefig('avg_packets_per_sec.png')
    plt.show()
    return avg_bytes_per_sec_by_streams, avg_packets_per_sec_by_streams

def save_stats_to_file(avg_bytes_per_sec_by_streams, avg_packets_per_sec_by_streams, filename):
    with open(filename, 'w') as f:
        for i in range(len(avg_bytes_per_sec_by_streams)):
            f.write(f"Run {i + 1}:\n")
            f.write(f"Average number of bytes per second: {avg_bytes_per_sec_by_streams[i]:.2f}\n")
            f.write(f"Average number of packets per second: {avg_packets_per_sec_by_streams[i]:.2f}\n")
            f.write("\n")

# Example usage
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 1111
    num_runs = 10  # Number of times to run the receiver and sender
    avg_bytes_per_sec_by_streams, avg_packets_per_sec_by_streams = run_receiver_and_sender(host, port, num_runs)
    save_stats_to_file(avg_bytes_per_sec_by_streams, avg_packets_per_sec_by_streams, "receiver_sender_stats.txt")
