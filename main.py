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
stats_dict = {}


def run_receiver(host, port):
    receiver = Receiver(host, port)
    stats = receiver.listen()
    # Store the statistics in the shared dictionary
    stats_dict[threading.current_thread().ident] = stats

# Function to run the sender
def run_sender(host, port, i):
    sender = Sender(host, port)
    sender.start(i)

# Function to run the receiver and sender in parallel
def run_receiver_and_sender(host, port, num_runs):
    results = []
    for i in range(1, num_runs + 1):
        print(f"XXXXXXXXXXXXXXXXXXXXXX Run #{i} XXXXXXXXXXXXXXXXXXXXXX")
        receiver_thread = threading.Thread(target=run_receiver, args=(host, port))
        sender_thread = threading.Thread(target=run_sender, args=(host, port, i))

        receiver_thread.start()
        time.sleep(1)
        sender_thread.start()

        receiver_thread.join()
        sender_thread.join()

        stats = stats_dict[receiver_thread.ident]
        results.append(stats)

    # Calculate averages
    total_byte_rate = sum(stats['average_byte_rate'] for stats in results) / num_runs
    total_packets_per_second = sum(stats['average_packets_per_second'] for stats in results) / num_runs

    print(f"Average Byte Rate: {total_byte_rate}")
    print(f"Average Packets per Second: {total_packets_per_second}")

    # Create a graph
    streams = [stats['stream_size'] for stats in results]
    byte_rates = [stats['average_byte_rate'] for stats in results]
    packet_rates = [stats['average_packets_per_second'] for stats in results]

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.scatter(streams, byte_rates)
    plt.xlabel('Number of Streams')
    plt.ylabel('Average Byte Rate')
    plt.title('Average Byte Rate vs. Number of Streams')

    plt.subplot(1, 2, 2)
    plt.scatter(streams, packet_rates)
    plt.xlabel('Number of Streams')
    plt.ylabel('Average Packets per Second')
    plt.title('Average Packets per Second vs. Number of Streams')

    plt.tight_layout()
    plt.show()

    return results


def save_stats_to_file(stats, filename):
    with open(filename, 'w') as f:
        for i, stat in enumerate(stats):
            if stat is None:
                continue
            f.write(f"Run {i + 1}:\n")
            for key, value in stat.items():
                f.write(f"{key}: {value:.2f}\n")
            f.write("\n")


# Example usage
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 1111
    num_runs = 10  # Number of times to run the receiver and sender
    stats = run_receiver_and_sender(host, port, num_runs)
    save_stats_to_file(stats, "receiver_sender_stats.txt")
