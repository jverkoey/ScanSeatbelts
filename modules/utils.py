import matplotlib.pyplot as plt
from modules import Seq
import pandas as pd
import base64


def plot_data(df, num_bytes, arbitration_id):
    fig, axs = plt.subplots(num_bytes, 1, figsize=(8, num_bytes * 2))  # Une subplot par octet
    if num_bytes == 1:
        axs = [axs]

    for i in range(num_bytes):
        axs[i].plot(df['timestamp'], df[f'byte_{i + 1}'], linestyle='-', label=f'Byte {i + 1}')
        axs[i].set_xlabel('Timestamp')
        axs[i].set_ylabel(f'Byte {i + 1}')
        axs[i].grid(True)
        axs[i].legend(loc='upper right')

    plt.suptitle(f'Arbitration ID {arbitration_id} - Byte Data')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def plot_one_byte(df, byte, arbitration_id):
    plt.plot(df['timestamp'], df[f'byte_{byte}'], linestyle='-', label=f'Byte {byte}')
    plt.xlabel('Timestamp')
    plt.ylabel(f'Byte {byte}')
    plt.grid(True)
    plt.legend(loc='upper right')
    plt.title(f'Arbitration ID {arbitration_id} - Byte {byte}')
    plt.show()



def load_data(name: str):
    try:
        csv_path = f"{name}.csv"
        seq_path = f"{name}.seq"
        df = pd.read_csv(csv_path)
        
        with open(seq_path, "r") as file:
            delta = float(file.readline().strip())
            seq = [(int(parts[0]), Seq(int(parts[1]))) for line in file for parts in [line.strip().split(":", 1)]]

        return df, seq, delta
    except FileNotFoundError:
        print("Invalid or nonexistent file.")
        exit(1)


def base64_to_ints(b64_string):
    decoded_bytes = base64.b64decode(b64_string)
    decoded_ints = [int(byte) for byte in decoded_bytes]
    return decoded_ints