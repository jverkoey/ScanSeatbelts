import pandas as pd
from modules import Seq
from modules.utils import plot_data, plot_one_byte, load_data, base64_to_ints
from settings import SIZE, ANALYSIS_PRECISION



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