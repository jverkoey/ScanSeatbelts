import pandas as pd
import numpy as np
from models import SignalType, ComponentType
import matplotlib.pyplot as plt
from modules import Seq, Component
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


def get_freq_and_val(data):
    intervals = []
    prev = -1
    for i in range(0, len(data)):
        if data[i] != 0:
            if prev != -1:
                intervals.append((i - prev, int(data[i])))
            prev = i

    if len(intervals) == 0:
        return 0, 0

    for i in range(1, len(intervals)):
        if intervals[i] != intervals[i-1]:
            return 0, 0

    return 1/intervals[0][0], intervals[0][1]

def compare_periodic(data, expected_pattern, size, component: Component):
    windows = []
    start = 0
    prev = expected_pattern[0]

    # TODO: do this before the main loop
    for i in range(1, size):
        if expected_pattern[i] != prev:
            if prev == 2: windows.append((start, i-1, prev))
            start = i
        prev = expected_pattern[i]
    if prev == 2: windows.append((start, i-1, prev))
    # ----------------------------------

    data_sequence = np.array(data)
    init_freq_and_val = get_freq_and_val(data_sequence[windows[0][0]:windows[0][1]])

    # we are looking for a frequency < 1 because it is not continuous
    if (not 0 < init_freq_and_val[0] < 1) or init_freq_and_val[1] == 0: return 0
    for i in range(1, len(windows)):
        if get_freq_and_val(data_sequence[windows[i][0]:windows[i][1]]) != init_freq_and_val:
            return 0
    
    return 1

def compare_inst_cont(data, expected_pattern, size, component: Component):
    step = len(data) // size  # ~frames per second
    prev_meant_data, meant_data = data[:step].mean(), 0
    current_pattern = [0]*size
    score = 0
    tmp = 1
    for i in range(1, size):
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
    
    return score, current_pattern

# TODO
def compare_aon_cont(data, expected_pattern, size, component: Component):
    raise NotImplementedError("Not implemented")

# TODO
def compare_inst_disc(data, expected_pattern, size, component: Component):
    raise NotImplementedError("Not implemented")

def compare(data, expected_pattern, component: Component):
    SIZE_ = SIZE*ANALYSIS_PRECISION
    if component.stype == SignalType.Instant:
        if component.ctype == ComponentType.Continuous:  # like an accelerator
            score, current_pattern = compare_inst_cont(data, expected_pattern, SIZE_, component)

        elif component.ctype == ComponentType.AllOrNothing:  # like a button
            score, current_pattern = compare_aon_cont(data, expected_pattern, SIZE_, component)
        
        elif component.ctype == ComponentType.Discrete:  # like a gearbox
            score, current_pattern = compare_inst_disc(data, expected_pattern, SIZE_, component)

        # spacial comparison
        score *= get_spacial_pattern(expected_pattern, SIZE_) == get_spacial_pattern(current_pattern, SIZE_)
    
    elif component.stype == SignalType.Periodic and component.ctype == ComponentType.AllOrNothing:  # like turn signals
        score = compare_periodic(data, expected_pattern, SIZE_, component)

    else:
        raise NotImplementedError("Not implemented")


    return score


def analyze(name: str):
    print("Analyzing the file...")
    df, seq, component = load_data(name)
    print("Component:", component, '\n')

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
            for i in range(num_bytes):
                scores[compare(df_group[f'byte_{i+1}'], expected_pattern, component)] = arbitration_id, i+1

        except Exception as e:
            print(f"Error analyzing arbitration ID {arbitration_id}: {e}")
    
    max_score = max(scores.keys())
    print("\nAnalysis complete.")
    print("Suspected ID:", scores[max_score][0], "| Octet:", scores[max_score][1], "| Score:", max_score)

    # plot the corresponding byte
    plot_one_byte(dfs_by_arbitration_id[scores[max_score][0]], scores[max_score][1], scores[max_score][0])
    
    return