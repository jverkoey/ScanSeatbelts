import pandas as pd
import base64
import matplotlib.pyplot as plt
from modules import Seq
from settings import SIZE, ANALYSIS_PRECISION


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


def gen_expected_pattern(seq: list[tuple[int, Seq]]) -> int:
    expected_pattern = [0]*SIZE*ANALYSIS_PRECISION
    for s in seq:
        for k in range(ANALYSIS_PRECISION):
            expected_pattern[s[0]*ANALYSIS_PRECISION+k] = s[1].value
   
    return expected_pattern


def compare(data, expected_pattern, delta):
    SIZE_ = round(delta)*ANALYSIS_PRECISION
    step = len(data) // SIZE_  # ~frames per second
    current_pattern = [0]*SIZE_
    meant_data = [0]*SIZE_
    for i in range(0, SIZE_):
        meant_data[i] = data[i*step:(i+1)*step].mean()

    for i in range(1, SIZE_):
        s = round(float(meant_data[i] - meant_data[i-1])) 
        current_pattern[i] = 1 if s > 0 else -1 if s < 0 else 0

    print(current_pattern)
    return current_pattern


def analyze(name: str):
    print("Analyzing the file...")
    df, seq, delta = load_data(name)

    # Format data
    df['data_ints'] = df['data'].apply(base64_to_ints)
    max_octets = max(df['data_ints'].apply(len))
    for i in range(max_octets):
        df[f'byte_{i+1}'] = df['data_ints'].apply(lambda x: x[i] if i < len(x) else None)
    dfs_by_arbitration_id = {arbitration_id: group for arbitration_id, group in df.groupby('arbitration_id')}

    expected_pattern = gen_expected_pattern(seq)
    print(expected_pattern, '\n')

    for arbitration_id, df_group in dfs_by_arbitration_id.items():
        num_octets = df_group['data_ints'].apply(len).max()

        if arbitration_id == "0x244":
            #plot_data(df_group, num_octets, arbitration_id)

            # TODO: compare data to expected pattern
            for i in range(num_octets):
                current_pattern = compare(df_group[f'byte_{i+1}'], expected_pattern, delta)

            # plot_data(df_group, num_octets, arbitration_id)
