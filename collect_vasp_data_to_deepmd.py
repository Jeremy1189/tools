#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description:
    This script recursively searches the current directory and its subdirectories
    for VASP "OUTCAR" files, reads each valid file using dpdata (with the "vasp/outcar"
    format), and merges them into a MultiSystems object. Finally, it exports the merged
    data into both "deepmd/raw" and "deepmd/npy" formats, all stored within the 
    "deepmd_data" folder (i.e., "deepmd_data/deepmd_raw" and "deepmd_data/deepmd_npy").

Installation:
    1) Make sure you have dpdata installed:
       pip install dpdata

Usage:
    1) Place the script in your working directory (which contains all subdirectories
       with your OUTCAR files).
    2) Run the script:
       python collect_vasp_data.py
    3) After it finishes, you will see a "deepmd_data" folder containing
       "deepmd_raw" and "deepmd_npy" directories.

Notes:
    1) You can adjust the script for other DFT codes or file names by modifying the
       searching pattern and the "fmt" parameter.
    2) If you already have a "deepmd_data" folder, the script will not overwrite existing
       data but may add to it if new data is found.
    3) For further details about dpdata usage or advanced configurations, please refer to
       the official dpdata documentation:
       https://github.com/deepmodeling/dpdata
"""

import os
from glob import glob
import dpdata
from dpdata import LabeledSystem, MultiSystems

def collect_and_convert_vasp_data(root_dir=None):
    """Search for OUTCAR files, read them with dpdata, and merge into MultiSystems."""
    if root_dir is None:
        root_dir = os.getcwd()
    
    # 1. Recursively find all OUTCAR files
    outcar_paths = glob(os.path.join(root_dir, "**", "OUTCAR"), recursive=True)
    print(f"Found {len(outcar_paths)} OUTCAR file(s) under {root_dir}.")

    # 2. Create a MultiSystems object to store merged data
    ms = MultiSystems()

    # 3. Read data from each OUTCAR and append to MultiSystems
    for outcar_file in outcar_paths:
        try:
            ls = LabeledSystem(outcar_file, fmt='vasp/outcar')
            if len(ls) > 0:
                ms.append(ls)
                print(f"Successfully loaded data from: {outcar_file}")
            else:
                print(f"Warning: No valid frames found in {outcar_file}. Skipped.")
        except Exception as e:
            print(f"Error: Could not read {outcar_file}. Reason: {e}")

    # 4. Create the "deepmd_data" folder if it does not exist
    deepmd_data_dir = os.path.join(root_dir, "deepmd_data")
    if not os.path.exists(deepmd_data_dir):
        os.makedirs(deepmd_data_dir)

    raw_dir = os.path.join(deepmd_data_dir, "deepmd_raw")
    npy_dir = os.path.join(deepmd_data_dir, "deepmd_npy")

    # 5. Export data to deepmd/raw and deepmd/npy
    if len(ms) > 0:
        print(f"\nExporting deepmd/raw -> {raw_dir}")
        ms.to_deepmd_raw(raw_dir)
        
        print(f"\nExporting deepmd/npy -> {npy_dir}")
        ms.to_deepmd_npy(npy_dir)
        print("\nConversion complete!")
    else:
        print("No valid data found. Nothing to export.")

if __name__ == "__main__":
    collect_and_convert_vasp_data()
