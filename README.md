# canScan

THIS PROJECT IS NOT YET COMPLETE.

## What is it?
This tool is designed to assist in reverse engineering the CAN (Controller Area Network) system in your vehicle. By using this tool successfully, you should be able to identify which CAN ID corresponds to specific vehicle components.

## How does it work?
canScan will provide a specific sequence for you to replicate. It then compares each byte in every captured data frame against the expected data frame (a virtual data frame that aligns perfectly with the intended sequence). Based on the analysis, the tool will identify and return the most likely CAN ID associated with the specified component.

## How to use it ?
Linux install:

```bash
git clone https://github.com/B3LIOTT/canScan.git
cd canScan
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For windows, replace `source venv/bin/activate` by `venv\Scripts\activate`

You can specify your listenning interface/channel in `config.yaml`, as well as the dump folder.

Then you can use: 
- `python dump.py` to dump data frames with the provided sequence
- `python analyze.py` to analyse the dump, and return the most likely CAN ID associated with the specified component


## I don't have any car but I want to test it, how ?
You can use `ICSim` simulator to create a virtual environement with a CAN BUS.

Before using it, you have to create a virtual CAN interface:
```bash
chmod +x emulate-can.sh
./emulate-can.sh
```
