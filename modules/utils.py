import matplotlib.pyplot as plt
from models import Component, ComponentType, SignalType, Seq
import pandas as pd
import base64
import json
import os


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
            header = file.readline().strip().split(":", 1)
            assert round(float(header[0])) == 15
            component = load_components(compIndex=int(header[1]))
            seq = [(int(parts[0]), Seq(int(parts[1]))) for line in file for parts in [line.strip().split(":", 1)]]

        return df, seq, component
    except FileNotFoundError:
        print("Invalid or nonexistent file.")
        exit(1)
    except Exception as e:
        print(f"Error while loading data: {e}")
        exit(1)


def base64_to_ints(b64_string):
    decoded_bytes = base64.b64decode(b64_string)
    decoded_ints = [int(byte) for byte in decoded_bytes]
    return decoded_ints


def list_files():
    os.chdir('dumps')
    datas = {}
    files = os.listdir(".")
    files = [file for file in files if os.path.isfile(os.path.join(".", file))]
    
    i = 1
    for file in files:
        if file.endswith('.csv'):
            data_name = file.split('.')[0]
            datas[i] = data_name
            print(f"{i}. {data_name}")
            i += 1
    
    return datas


def build_components(components: dict):
    comps = []
    for component in components:
        comps.append(Component(name=component['name'], ctype=ComponentType(component['type']), stype=SignalType(component['signal'])))

    return comps

def load_components(compIndex: int = None):
    try:
        #os.chdir('..')
        with open("components.json", "r") as file:
            file_content = file.read()
        
        json_comps = json.loads(file_content)
        if compIndex is not None:
            component = json_comps[compIndex]
            return Component(name=component['name'], ctype=ComponentType(component['type']), stype=SignalType(component['signal']))

        comps = build_components(json_comps)
    
    except FileNotFoundError:
        raise FileNotFoundError("File components.json not found.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError("Invalid components.json file.")
    except Exception as e:
        raise Exception(f"Error while loading components: {e}")

    return comps