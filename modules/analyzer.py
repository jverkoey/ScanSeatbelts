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


def gen_expected_pattern(seq: list[tuple[int, Seq]]) -> int:
    expected_pattern = [0]*SIZE*ANALYSIS_PRECISION
    for s in seq:
        for k in range(ANALYSIS_PRECISION):
            expected_pattern[s[0]*ANALYSIS_PRECISION+k] = s[1].value
   
    return expected_pattern


def get_spacial_pattern(pattern, size):
    tmp = pattern[0]
    spacial_pattern = [tmp]
    for i in range(1, size):
        if (c := pattern[i]) != tmp:
            spacial_pattern.append(c)
            tmp = c

    return spacial_pattern


def compare(data, expected_pattern, delta):
    SIZE_ = round(delta)*ANALYSIS_PRECISION
    step = len(data) // SIZE_  # ~frames per second
    current_pattern = [0]*SIZE_
    prev_meant_data, meant_data = data[:step].mean(), 0
    score = 0
    tmp = 1
    for i in range(1, SIZE_):
        meant_data = data[i*step:(i+1)*step].mean()
        s = round(float(meant_data - prev_meant_data)) 
        current_pattern[i] = (1 if s > 0 else 0) # TODO: mettre -1 pour la décroissance ?
        prev_meant_data = meant_data
        
        # temporal comparison
        if current_pattern[i] == expected_pattern[i]:
            tmp += 1
            score += tmp**(current_pattern[i]+1)  # TODO: better heuristic ?

        else:
            tmp = 1

    # spacial comparison
    score *= get_spacial_pattern(expected_pattern, SIZE_) == get_spacial_pattern(current_pattern, SIZE_)

    return score


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
    # print(expected_pattern, '\n')

    scores = {}
    for arbitration_id, df_group in dfs_by_arbitration_id.items():
        num_bytes = df_group['data_ints'].apply(len).max()

        # plot_data(df_group, num_bytes, arbitration_id)

        try:
        # TODO: compare data to expected pattern
            for i in range(num_bytes):
                scores[compare(df_group[f'byte_{i+1}'], expected_pattern, delta)] = arbitration_id, i+1

        except Exception as e:
            print(f"Error analyzing arbitration ID {arbitration_id}: {e}")
    
    max_score = max(scores.keys())
    print("\nAnalysis complete.")
    print("Suspected ID:", scores[max_score][0], "| Octet:", scores[max_score][1], "| Score:", max_score)
    # plot the corresponding byte
    plot_one_byte(dfs_by_arbitration_id[scores[max_score][0]], scores[max_score][1], scores[max_score][0])