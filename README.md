# canScan

## What is it?
This tool is designed to assist in reverse engineering the CAN (Controller Area Network) system in your vehicle. By using this tool successfully, you should be able to identify which CAN ID corresponds to specific vehicle components.

## How does it work?
canScan will provide a specific sequence for you to replicate. It then compares each byte in every captured data frame against the expected data frame (a virtual data frame that aligns perfectly with the intended sequence). Based on the analysis, the tool will identify and return the most likely CAN ID associated with the specified component.