import pandas as pd
import base64
import matplotlib.pyplot as plt
from modules import SeqMessages
from settings import SIZE


def load_data(name: str):
    try:
        csv_path = f"{name}.csv"
        seq_path = f"{name}.seq"
        df = pd.read_csv(csv_path)
        
        with open(seq_path, "r") as file:
            seq = [(int(parts[0]), SeqMessages(parts[1])) for line in file for parts in [line.strip().split(":", 1)]]

        return df, seq
    except FileNotFoundError:
        print("Invalid or nonexistent file.")
        exit(1)

# Fonction pour décoder la base64 et retourner une liste d'entiers (un entier par octet)
def base64_to_ints(b64_string):
    decoded_bytes = base64.b64decode(b64_string)
    decoded_ints = [int(byte) for byte in decoded_bytes]
    return decoded_ints


def plot_data(df, num_octets, arbitration_id):
    fig, axs = plt.subplots(num_octets, 1, figsize=(8, num_octets * 2))  # Une subplot par octet
    if num_octets == 1:
        axs = [axs]

    for i in range(num_octets):
        axs[i].plot(df['timestamp'], df[f'byte_{i + 1}'], linestyle='-', label=f'Byte {i + 1}')
        axs[i].set_xlabel('Timestamp')
        axs[i].set_ylabel(f'Byte {i + 1}')
        axs[i].grid(True)
        axs[i].legend(loc='upper right')

    plt.suptitle(f'Arbitration ID {arbitration_id} - Byte Data')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def gen_expected_data(seq: list):
    expected_data = [0] * SIZE
    start = seq[0][0]
    val = 1
    ind = 0
    k = 0
    INCR_STEP = 3.5
    while k < len(seq):
        if seq[k][1] == SeqMessages.INCREMENT:
            if ind == seq[k][0]:
                expected_data[ind] = val
                val += INCR_STEP
                k += 1

            else:
                val = max(val - INCR_STEP, 0)
                for i in range(ind, seq[k][0]):
                    val = max(val - INCR_STEP, 0)
                    expected_data[i] = val

                ind = i
        
        elif seq[k][1] == SeqMessages.ACTIVATE:
            raise NotImplementedError("ACTIVATE not implemented yet")
        elif seq[k][1] == SeqMessages.PRESS:
            raise NotImplementedError("PRESS not implemented yet")

        ind += 1

    if (last_val:=expected_data[ind-1]) > 0:
        for k in range(ind, SIZE):
            last_val = max(last_val - INCR_STEP, 0)
            expected_data[k] = last_val

    return expected_data

def analyze(name: str):
    print("Analyzing the file...")
    df, seq = load_data(name)

    # Format data
    df['data_ints'] = df['data'].apply(base64_to_ints)
    max_octets = max(df['data_ints'].apply(len))
    for i in range(max_octets):
        df[f'byte_{i+1}'] = df['data_ints'].apply(lambda x: x[i] if i < len(x) else None)
    dfs_by_arbitration_id = {arbitration_id: group for arbitration_id, group in df.groupby('arbitration_id')}

    expected_data = gen_expected_data(seq)
            
    # Plot data
    # plt.plot(range(SIZE), expected_data, label="Expected")
    # plt.legend()

    # TODO: substraction of expected data from real data and see the closest to 0

    for arbitration_id, df_group in dfs_by_arbitration_id.items():
        num_octets = df_group['data_ints'].apply(len).max()

        if arbitration_id == "0x244":
            plot_data(df_group, num_octets, arbitration_id)

        for i in range(num_octets):
            pass
