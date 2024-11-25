from models import Component, ComponentType, SignalType, Seq
from modules.utils import load_components, load_config
from modules.dumper import *
from settings import SIZE
from time import sleep, perf_counter
import random
import json
import os

"""
The Maestro module is the one which orchestrates CAN messages sended by the user.
The user wants to find which messages are sent by the ECU when he presses the brake pedal for example.
Maestro will create a specific sequence, and the user has to reproduce it.
Then, the analyzer can easily find the specific sequence (if the user isn't too bad at reproducing it).
"""

def seqToMessage(seq: int):
    if seq == 1:
        return "increment progressively"
    elif seq == 2:
        return "activate"
    elif seq == 3:
        return "press"
    elif seq == 4:
        return "release"
    elif seq == 5:
        return "go to initial position and wait"
    else:
        raise ValueError("Invalid sequence.")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def orchestrates_sequence(component: Component, sequence, default_msg, rep: bool):
    watch_m = "Watch this sequence"
    rep_m = "Reproduce this sequence"
    m = f"{watch_m if not rep else rep_m}"
    print(m)

    init_line = "-" * SIZE
    messages = [seqToMessage(default_msg.value)] * SIZE
    for step in sequence:
        messages[step[0]] = seqToMessage(step[1].value)
        init_line = init_line[:step[0]] + "X" + init_line[step[0]+1:]
    
    line = ""
    config, file_path, zoomies, = None, None, None
    start, delta = 0, 0
    try:
        if rep:
            print("Listening to CAN bus...")
            config, file_path = load_config()
            zoomies = listen(config=config, file_path=file_path)
            start = perf_counter()

        for i in range(SIZE):
            clear_terminal()
            line = init_line[:i] + "." + init_line[i+1:]
            print(f"{m}:\n{line}\n\t{messages[i]}")
            sleep(1)
        
        delta = perf_counter() - start

        if not rep:
            input("Press Enter to reproduce the sequence.")
            orchestrates_sequence(component, sequence, default_msg, True)

        else:
            dispose(*zoomies)
            again = input("Do you want to try again ? (o/n) > ")
            if again.lower() == "o":
                os.remove(file_path)
                orchestrates_sequence(component, sequence, default_msg, True)
            
            print("compIndex: ", compIndex)
            end_checks(file_path, sequence, delta, compIndex)
            print("Sequence reproduced, use the analyzer to determine the ID of the component.")

    except KeyboardInterrupt:
        dispose(*zoomies)
        raise Exception("User interrupted.")  

    return


def generate_sequence(component: Component):
    if component.ctype == ComponentType.AllOrNothing:
        print("Generating a random sequence for AllOrNothing component.")
        input("Press Enter to continue...")
        default_msg = Seq.RELEASE
        if component.stype == SignalType.Instant:
            # TODO: improve
            seq = [(2, Seq.PRESS), (4, Seq.PRESS), (5, Seq.PRESS), (8, Seq.PRESS), (10, Seq.PRESS), (12, Seq.PRESS)]
        elif component.stype == SignalType.Periodic:
            # TODO: improve
            seq = [(i, Seq.ACTIVATE) for i in range(1, 5)] + [(i, Seq.ACTIVATE) for i in range(7, SIZE-2)]
        else:
            raise ValueError("Invalid SignalType.")

        return orchestrates_sequence(component, seq, default_msg, False)
    
    elif component.ctype == ComponentType.Continuous:
        print("Generating a random sequence for Continuous component.")
        input("Press Enter to continue...")
        default_msg = Seq.WAIT
        seq = [(i, Seq.INCREMENT) for i in range(1, 5)] + [(i, Seq.INCREMENT) for i in range(8, SIZE-2)]

        return orchestrates_sequence(component, seq, default_msg, False)

    raise NotImplementedError("Not implemented.")
    

def choose_component(components: list[Component]):
    print("Choose a component:")
    for i, component in enumerate(components):
        print(f"{i+1}. {component.name}")

    try:
        choice = int(input("> "))
        assert 0 < choice <= len(components)
    except KeyboardInterrupt:
        raise Exception("User interrupted.")
    except ValueError:
        raise ValueError("Invalid choice.")

    global compIndex
    compIndex = choice-1
    
    print("compIndex: ", compIndex)
    comp = components[choice-1]
    print(f"Component {comp.name} choosen.")
    return generate_sequence(comp)


def wake_up_maestro():
    comps = load_components()
    print("Maestro is ready to guide you.")
    return choose_component(comps)
